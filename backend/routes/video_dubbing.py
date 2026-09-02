"""Student video/audio translation and dubbing endpoints."""
from flask import Blueprint, g, request, Response

from backend.database import db
from backend.models import VideoDubbingJob
from backend.utils import fail, login_required, ok, log_activity, roles_required
from backend.services import video_dubbing_service as dubbing

bp = Blueprint("video_dubbing", __name__, url_prefix="/api/video-dubbing")

LANGS = {"en", "hi", "mr", "gu", "bn", "ta", "te"}


def _safe_lang(value, allow_auto=False):
    value = (value or "").strip().lower()
    if allow_auto and value in ("", "auto"):
        return "auto"
    return value if value in LANGS else None


@bp.post("/create")
@login_required
def create():
    if not dubbing.configured():
        return fail("Video dubbing is not configured on the server yet. Add ELEVENLABS_API_KEY in Render.", 503)

    file = request.files.get("file")
    source_url = (request.form.get("source_url") or "").strip()
    source_lang = _safe_lang(request.form.get("source_language"), allow_auto=True)
    target_lang = _safe_lang(request.form.get("target_language"))
    if not target_lang:
        return fail("Choose one of the supported target languages.")
    if not file and not source_url:
        return fail("Upload a video or paste a public video URL.")
    if file and not file.filename:
        return fail("The uploaded file has no filename.")
    if source_url and len(source_url) > 1000:
        return fail("Video URL is too long.")

    try:
        result = dubbing.create_dub(
            file_storage=file if file else None,
            source_url=source_url if not file else None,
            source_lang=source_lang,
            target_lang=target_lang,
            name=f"Bhasha Shiksha Setu - {g.user.name}",
        )
        job = VideoDubbingJob(
            user_id=g.user.id,
            dubbing_id=result.get("dubbing_id"),
            source_url=source_url if not file else "",
            original_filename=file.filename if file else "",
            source_language=source_lang,
            target_language=target_lang,
            status=result.get("status", "preparing"),
        )
        db.session.add(job)
        db.session.commit()
        log_activity(g.user, "video_dubbing_created", f"Video dub {job.id} -> {target_lang}")
        return ok(job.to_dict(), "Video translation started.", 201)
    except (ValueError, RuntimeError) as exc:
        return fail(str(exc), 400 if isinstance(exc, ValueError) else 502)


@bp.get("")
@login_required
def history():
    rows = VideoDubbingJob.query.filter_by(user_id=g.user.id).order_by(VideoDubbingJob.created_at.desc()).limit(100).all()
    return ok([r.to_dict() for r in rows])


@bp.get("/<int:job_id>")
@login_required
def detail(job_id):
    job = db.session.get(VideoDubbingJob, job_id)
    if not job or job.user_id != g.user.id:
        return fail("Dubbing job not found.", 404)
    return _refresh(job)


@bp.get("/<int:job_id>/status")
@login_required
def status(job_id):
    job = db.session.get(VideoDubbingJob, job_id)
    if not job or job.user_id != g.user.id:
        return fail("Dubbing job not found.", 404)
    return _refresh(job)


def _refresh(job):
    try:
        remote = dubbing.get_dub(job.dubbing_id)
        job.status = remote.get("status", job.status)
        job.source_language = remote.get("source_language") or job.source_language
        job.error_message = remote.get("error") or ""
        db.session.commit()
        data = job.to_dict()
        data["provider_status"] = remote.get("status")
        data["media_metadata"] = remote.get("media_metadata")
        data["target_languages"] = remote.get("target_languages", [])
        data["ready"] = remote.get("status") == "dubbed"
        data["download_url"] = f"/api/video-dubbing/{job.id}/download" if data["ready"] else None
        return ok(data)
    except RuntimeError as exc:
        return fail(str(exc), 502)


@bp.get("/<int:job_id>/download")
@login_required
def download(job_id):
    job = db.session.get(VideoDubbingJob, job_id)
    if not job or job.user_id != g.user.id:
        return fail("Dubbing job not found.", 404)
    try:
        r = dubbing.download_dub(job.dubbing_id, job.target_language)
        content_type = r.headers.get("Content-Type", "video/mp4")
        response = Response(r.iter_content(chunk_size=1024 * 256), content_type=content_type)
        response.headers["Content-Disposition"] = f'attachment; filename="bhasha-dub-{job.id}-{job.target_language}.mp4"'
        return response
    except RuntimeError as exc:
        return fail(str(exc), 502)


@bp.delete("/<int:job_id>")
@login_required
def remove(job_id):
    job = db.session.get(VideoDubbingJob, job_id)
    if not job or job.user_id != g.user.id:
        return fail("Dubbing job not found.", 404)
    try:
        dubbing.delete_dub(job.dubbing_id)
    except RuntimeError as exc:
        return fail(str(exc), 502)
    db.session.delete(job)
    db.session.commit()
    return ok(None, "Dubbing job deleted.")


@bp.get("/admin/list")
@roles_required("admin")
def admin_list():
    rows = VideoDubbingJob.query.order_by(VideoDubbingJob.created_at.desc()).limit(200).all()
    return ok([r.to_dict() for r in rows])
