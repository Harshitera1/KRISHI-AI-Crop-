from flask import Blueprint, request, jsonify, send_file
from services.agentic_service import export_advisory_pdf, run_advisory_pipeline
from auth.auth_middleware import token_required


crop_bp = Blueprint("crop", __name__)

@crop_bp.route("/recommend", methods=["POST"])
@token_required   # 🔥 ADD THIS
def recommend():
    data = request.get_json(silent=True) or {}
    result = run_advisory_pipeline(data)
    return jsonify(result)


@crop_bp.route("/advisory", methods=["POST"])
@token_required
def advisory():
    data = request.get_json(silent=True) or {}
    result = run_advisory_pipeline(data)
    return jsonify(result)


@crop_bp.route("/advisory/pdf", methods=["POST"])
@token_required
def advisory_pdf():
    data = request.get_json(silent=True) or {}
    result = run_advisory_pipeline(data)

    if not result.get("success"):
        return jsonify(result), 400

    pdf_path = export_advisory_pdf(result["advisory_text"], {**data, **result})
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name="krishi_advisory.pdf",
        mimetype="application/pdf",
    )