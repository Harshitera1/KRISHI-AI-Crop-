import logging
from threading import Lock

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
_KNOWLEDGE_DOCUMENTS = [
    "Nitrogen deficiency often appears first as pale green or yellowing leaves, usually starting on older leaves because nitrogen moves within the plant. Confirm the problem with a soil test before applying fertilizer. Use well-composted manure or a measured nitrogen source in small split applications rather than one heavy dose. Water after granular application when appropriate, but avoid runoff. Excess nitrogen creates soft, leafy growth that attracts pests and delays maturity, so match the rate to the crop and growth stage. Keep records of the product, rate, date, and field response. If yellowing occurs in patches, also check drainage, root damage, and compaction because those problems can prevent roots from taking up available nitrogen.",
    "Phosphorus deficiency can cause slow growth, weak roots, and dark green or purplish leaves, especially in cool or waterlogged soil. A soil test should guide correction because excess phosphorus can pollute waterways and interfere with micronutrient uptake. Place a suitable phosphorus fertilizer near, but not directly against, the seed or transplant roots. Correct soil pH toward the crop's recommended range, since phosphorus becomes less available in strongly acidic or alkaline soil. Organic matter and healthy root activity improve availability over time. Do not use leaf color alone to diagnose the issue; cold weather, variety, disease, and root stress can produce similar symptoms.",
    "Potassium deficiency commonly causes yellowing or scorching along leaf margins, weak stems, poor water regulation, and lower tolerance to drought or disease. Test soil potassium before applying potash because very high rates can upset magnesium and calcium balance. Apply the recommended amount based on crop removal and soil test results, preferably in a split dose for sandy soils where leaching is likely. Incorporating crop residues and adding mature compost can recycle some potassium. Maintain even soil moisture because drought stress can make symptoms worse. If symptoms are irregular, inspect roots and confirm that compaction, salinity, or poor drainage is not limiting nutrient uptake.",
    "Most field crops perform best when soil pH is maintained in a crop-appropriate range, often near 6.0 to 7.5. Test several representative samples from the root zone instead of relying on one handful of soil. For acidic soil, agricultural lime raises pH gradually; use the laboratory-recommended rate and incorporate it where practical. For alkaline soil, elemental sulfur can lower pH slowly, but it should also be guided by a test and applied well before planting. Avoid quick fixes with household acids or excessive amendments. Organic matter, good drainage, and balanced fertilization improve nutrient availability, but they do not replace a pH correction plan.",
    "Irrigate early in the morning when possible, because cooler air and lower wind reduce evaporation while leaves have time to dry. Water the root zone deeply and less frequently rather than wetting the surface lightly every day, adjusting for crop stage, soil texture, rainfall, and local weather. Rice needs managed standing water or saturated soil according to its growth stage, while wheat generally benefits from timely irrigation at crown-root initiation, flowering, and grain filling. Vegetables and fruiting crops need consistent moisture during flowering and fruit set. Check soil moisture below the surface before irrigating, and improve drainage if water remains ponded after watering.",
    "Early pest warnings include fresh holes, leaf mines, chewed edges, sticky honeydew, webbing, curled leaves, wilted shoots, frass, and clusters of eggs or young larvae on leaf undersides. Walk a field twice a week, checking different borders and growth stages, and record the pest, location, and severity. Yellowing alone does not prove insect damage; compare affected and healthy plants and inspect roots when needed. Remove heavily infested plant parts where practical, conserve beneficial insects, and use traps or scouting counts to decide whether action is justified. Choose a crop-labeled treatment only after identifying the pest, and rotate modes of action to slow resistance.",
    "Fertilizer timing should follow crop demand, root activity, rainfall risk, and the soil test rather than a fixed calendar alone. Apply phosphorus and potassium before planting or near the root zone when the test calls for them. Split nitrogen between planting, active vegetative growth, and the crop's highest-demand stage to reduce leaching and lodging. Avoid spreading fertilizer immediately before heavy rain or onto saturated soil. Keep fertilizer away from seed and stems unless the product label allows contact. Record rates and dates, then compare crop color, growth, and yield with untreated areas when possible. A balanced plan is safer than correcting a deficiency with a single excessive nutrient.",
    "Healthy soil has stable aggregates, active roots, earthworms and microbes, adequate organic matter, and enough air and water in the root zone. Keep living roots or residue on the soil as long as practical, rotate crops, add mature compost when appropriate, and minimize unnecessary tillage. Prevent compaction by avoiding field traffic when soil is wet. Use cover crops suited to the local climate to reduce erosion and recycle nutrients. Test pH, salinity, organic matter, and major nutrients at a regular interval, sampling consistently so results can be compared. Good soil health improves water infiltration and nutrient efficiency, but amendments should still be selected and applied from measured needs.",
    "When a crop is under stress, diagnose the whole field before treating it. Compare symptoms on old and new leaves, inspect roots, note recent weather, and check irrigation uniformity, drainage, compaction, salinity, and herbicide exposure. Take a representative soil sample and, when a disease or pest is suspected, use a local agricultural laboratory or extension service for confirmation. Mark the affected area and photograph symptoms with the date and crop stage. Avoid tank-mixing several products without checking labels and compatibility. Small, targeted changes followed by a short recheck are safer than repeated broad applications. Keep a field log so recurring patterns can be linked to soil, weather, and management decisions.",
]

_model = None
_index = None
_index_lock = Lock()


def _get_index():
    global _model, _index

    if _index is not None:
        return _index

    with _index_lock:
        if _index is None:
            _model = SentenceTransformer(_EMBEDDING_MODEL_NAME)
            embeddings = _model.encode(
                _KNOWLEDGE_DOCUMENTS,
                convert_to_numpy=True,
                normalize_embeddings=True,
            ).astype("float32")
            _index = faiss.IndexFlatIP(embeddings.shape[1])
            _index.add(embeddings)
            logger.info("Agronomy RAG index initialized", extra={"documents": len(_KNOWLEDGE_DOCUMENTS)})

    return _index


def retrieve_knowledge(crop: str, npk: dict, query_context: str = "") -> list[str]:
    """Return the most relevant local agronomy documents for a recommendation."""
    query = (
        f"Crop: {crop}. Soil nutrients: N={npk.get('N', 'unknown')}, "
        f"P={npk.get('P', 'unknown')}, K={npk.get('K', 'unknown')}. {query_context}"
    )
    index = _get_index()
    query_embedding = _model.encode(
        [query], convert_to_numpy=True, normalize_embeddings=True
    ).astype("float32")
    _, indices = index.search(query_embedding, min(4, len(_KNOWLEDGE_DOCUMENTS)))
    return [_KNOWLEDGE_DOCUMENTS[index] for index in indices[0] if index >= 0]