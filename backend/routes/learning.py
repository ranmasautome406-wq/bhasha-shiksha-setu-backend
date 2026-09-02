"""Personalized learning endpoints."""
from flask import Blueprint, g
from backend.database import db
from backend.models import Lesson, StudentProgress, QuizAttempt
from backend.utils import login_required, ok

bp=Blueprint("learning",__name__,url_prefix="/api/learning")

@bp.get("/profile")
@login_required
def profile():
    attempts=QuizAttempt.query.filter_by(user_id=g.user.id).all()
    progress=StudentProgress.query.filter_by(user_id=g.user.id).all()
    avg=round(sum(a.percentage for a in attempts)/len(attempts)) if attempts else 0
    return ok({"user_id":g.user.id,"language_preference":g.user.language_preference,"lessons_completed":sum(1 for p in progress if p.status=="completed"),"average_score":avg,"quiz_attempts":len(attempts)})

@bp.get("/weak-topics")
@login_required
def weak_topics():
    attempts=QuizAttempt.query.filter_by(user_id=g.user.id).order_by(QuizAttempt.created_at.desc()).limit(20).all()
    if not attempts:return ok([])
    avg=sum(a.percentage for a in attempts)/len(attempts)
    if avg<60:
        return ok([{"topic":"Recent lesson concepts","score":round(avg),"reason":"Your recent quiz scores show that these concepts need another explanation and practice round."}])
    return ok([])

@bp.get("/recommendations")
@login_required
def recommendations():
    done={p.lesson_id for p in StudentProgress.query.filter_by(user_id=g.user.id).all()}
    lessons=Lesson.query.filter_by(status="published").filter(~Lesson.id.in_(done or {-1})).order_by(Lesson.views.desc()).limit(6).all()
    return ok([{"lesson_id":l.id,"title":l.title,"subject":l.subject,"reason":"Recommended from your language and learning activity."} for l in lessons])
