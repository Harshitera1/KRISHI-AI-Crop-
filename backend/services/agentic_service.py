import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph

from controllers.crop_controller import get_crop
from services.rag_service import retrieve_knowledge

load_dotenv()

logger = logging.getLogger(__name__)


class AdvisoryState(TypedDict, total=False):
    farmer_input: dict
    recommendation: dict
    risk_flagged: bool
    risk_level: str
    risk_flags: list[str]
    knowledge: list[str]
    advisory_text: str


def predict_crop(state: AdvisoryState) -> dict:
    """Call the existing recommendation flow without duplicating ML logic."""
    return {"recommendation": get_crop(state["farmer_input"])}


def check_risk(state: AdvisoryState) -> dict:
    recommendation = state["recommendation"]
    farmer_input = state["farmer_input"]
    flags = []

    top_3 = recommendation.get("top_3", [])
    confidence = top_3[0].get("confidence", 0) if top_3 else 0
    if confidence < 0.60:
        flags.append(f"final crop confidence is low ({confidence:.3f})")

    weather = recommendation.get("weather", {})
    temperature = weather.get("temperature", farmer_input.get("temperature"))
    humidity = weather.get("humidity", farmer_input.get("humidity"))
    rainfall = farmer_input.get("rainfall")

    if temperature is not None and (temperature < 5 or temperature > 40):
        flags.append(f"temperature is extreme ({temperature} C)")
    if humidity is not None and (humidity < 20 or humidity > 90):
        flags.append(f"humidity is extreme ({humidity}%)")
    if rainfall is not None and (rainfall < 20 or rainfall > 300):
        flags.append(f"rainfall is outside the working range ({rainfall} mm)")

    ph = farmer_input.get("ph")
    if ph is not None and (ph < 5.5 or ph > 8.5):
        flags.append(f"soil pH needs attention ({ph})")

    nutrient_limits = {"N": 20, "P": 10, "K": 20}
    for nutrient, limit in nutrient_limits.items():
        value = farmer_input.get(nutrient)
        if value is not None and value < limit:
            flags.append(f"{nutrient} level is low ({value})")

    if not recommendation.get("success"):
        flags.append("the existing crop recommendation did not succeed")

    return {
        "risk_flagged": bool(flags),
        "risk_level": "high" if len(flags) >= 2 else "moderate" if flags else "low",
        "risk_flags": flags,
    }


def retrieve_for_recommendation(state: AdvisoryState) -> dict:
    recommendation = state["recommendation"]
    if not recommendation.get("success"):
        return {"knowledge": []}

    farmer_input = state["farmer_input"]
    npk = {key: farmer_input.get(key, "unknown") for key in ("N", "P", "K")}
    query_context = json.dumps(
        {
            "risk_flags": state.get("risk_flags", []),
            "soil": farmer_input.get("soil"),
            "ph": farmer_input.get("ph"),
            "weather": recommendation.get("weather", {}),
        },
        default=str,
    )
    return {
        "knowledge": retrieve_knowledge(
            recommendation["recommended_crop"], npk, query_context
        )
    }


def _generate_llm_advisory(state: AdvisoryState, include_warning: bool) -> dict:
    recommendation = state["recommendation"]
    if not recommendation.get("success"):
        return {
            "advisory_text": "The crop recommendation could not be completed. Please check the location, weather, and soil inputs."
        }

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    from langchain_groq import ChatGroq

    risk_section = "No risk warning was raised."
    if include_warning:
        risk_section = "Risk warning ({level}):\n{flags}".format(
            level=state.get("risk_level", "moderate"),
            flags="\n".join(f"- {flag}" for flag in state.get("risk_flags", [])),
        )

    prompt = f"""You are an agricultural advisor helping a farmer in plain English.
Write a short, practical advisory of no more than 180 words.
Include the recommended crop and confidence, why it fits the available information,
fertilizer and irrigation notes grounded only in the retrieved documents, and the risk
warning section when present. Do not invent exact fertilizer rates, diagnoses, or facts
not supported by the input or documents. Remind the farmer to confirm important input
rates with a soil test or local agricultural expert.

Farmer raw input:
{json.dumps(state["farmer_input"], indent=2, default=str)}

Crop recommendation:
{json.dumps(recommendation, indent=2, default=str)}

{risk_section}

Retrieved agronomy documents:
{chr(10).join(state.get("knowledge", [])) or "No documents were retrieved."}
"""
    response = ChatGroq(
        model="openai/gpt-oss-20b",
        groq_api_key=api_key,
        temperature=0.2,
        max_tokens=700,
        reasoning_effort="low",
    ).invoke(prompt)
    content = response.content
    if isinstance(content, list):
        content = " ".join(
            item.get("text", "") for item in content if isinstance(item, dict)
        )
    return {"advisory_text": str(content).strip()}


def synthesize_advisory(state: AdvisoryState) -> dict:
    return _generate_llm_advisory(state, include_warning=True)


def synthesize_without_warning(state: AdvisoryState) -> dict:
    return _generate_llm_advisory(state, include_warning=False)


def _risk_route(state: AdvisoryState) -> str:
    return "with_warning" if state.get("risk_flagged") else "without_warning"


def _build_graph():
    graph = StateGraph(AdvisoryState)
    graph.add_node("predict_crop", predict_crop)
    graph.add_node("check_risk", check_risk)
    graph.add_node("retrieve_knowledge", retrieve_for_recommendation)
    graph.add_node("synthesize_advisory", synthesize_advisory)
    graph.add_node("synthesize_without_warning", synthesize_without_warning)
    graph.add_edge(START, "predict_crop")
    graph.add_edge("predict_crop", "check_risk")
    graph.add_edge("check_risk", "retrieve_knowledge")
    graph.add_conditional_edges(
        "retrieve_knowledge",
        _risk_route,
        {
            "with_warning": "synthesize_advisory",
            "without_warning": "synthesize_without_warning",
        },
    )
    graph.add_edge("synthesize_advisory", END)
    graph.add_edge("synthesize_without_warning", END)
    return graph.compile()


_advisory_graph = _build_graph()


def run_advisory_pipeline(farmer_input: dict) -> dict:
    """Run prediction, risk checks, RAG retrieval, and LLM synthesis."""
    result = _advisory_graph.invoke({"farmer_input": farmer_input})
    return {
        **result["recommendation"],
        "risk_flagged": result.get("risk_flagged", False),
        "risk_level": result.get("risk_level", "low"),
        "risk_flags": result.get("risk_flags", []),
        "knowledge": result.get("knowledge", []),
        "advisory_text": result.get("advisory_text", ""),
    }


def export_advisory_pdf(advisory_text: str, farmer_input: dict) -> str:
    """Write a basic advisory PDF and return its absolute path."""
    from fpdf import FPDF

    output_dir = Path(__file__).resolve().parents[1] / "generated_reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"advisory_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.pdf"
    output_path = output_dir / file_name

    recommendation = farmer_input.get("recommendation", {})
    recommended_crop = farmer_input.get("recommended_crop") or recommendation.get(
        "recommended_crop", "Not provided"
    )
    raw_inputs = json.dumps(farmer_input, indent=2, default=str)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, "KRISHI AI Advisory Report", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, f"Recommended crop: {recommended_crop}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.cell(0, 8, "Farmer inputs", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, raw_inputs.encode("latin-1", "replace").decode("latin-1"))
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Advisory", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(
        0,
        6,
        advisory_text.encode("latin-1", "replace").decode("latin-1"),
    )
    pdf.output(str(output_path))
    return str(output_path)