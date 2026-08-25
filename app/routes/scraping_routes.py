import threading
from flask import Blueprint, request, jsonify, current_app
from app.container import get_scraping_service

scraping_bp = Blueprint("scraping_bp", __name__)

@scraping_bp.route("/scraping/launch", methods=["POST"])
def launch_scraping():
    data = request.get_json(silent=True) or {}
    app_ctx = current_app._get_current_object()

    def tache_fond():
        with app_ctx.app_context():
            service = get_scraping_service()
            service.launch(
                user_id=1, sector=data.get("sector"),
                location=data.get("location"), keywords=data.get("keywords")
            )

    thread = threading.Thread(target=tache_fond)
    thread.start()

    return jsonify({"message": "Scraping lancé en arrière-plan, consultez /scraping-jobs/<id> pour le suivi"}), 202

@scraping_bp.route("/scraping-jobs/<int:job_id>", methods=["GET"])
def get_job_status(job_id):
    from app.models.scraping_job import ScrapingJob
    job = ScrapingJob.query.get(job_id)
    if not job:
        return jsonify({"error": "Job introuvable"}), 404
    return jsonify({
        "id": job.id, "status": job.status,
        "results_count": job.results_count,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None
    }), 200