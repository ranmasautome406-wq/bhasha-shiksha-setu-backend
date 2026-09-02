"""Quiz and assessment endpoints for the personalized-learning demo."""
from flask import Blueprint, g, request
from backend.database import db
from backend.models import Lesson, Quiz, Question, QuizAttempt
from backend.utils import fail, login_required, ok

bp = Blueprint("quiz", __name__, url_prefix="/api/quiz")

@bp.post("")
@login_required
def create_quiz():
    data=request.get_json(silent=True) or {}
    lesson_id=data.get("lesson_id")
    lesson=db.session.get(Lesson, int(lesson_id)) if str(lesson_id).isdigit() else None
    if not lesson: return fail("Lesson not found.",404)
    q=Quiz(lesson_id=lesson.id, title=f"Practice: {lesson.title}", language=g.user.language_preference or lesson.language)
    db.session.add(q); db.session.flush()
    bank=[
        (f"What is the main idea of {lesson.title}?", ["Understanding the lesson concept","Ignoring the lesson","Memorising unrelated facts","Skipping the topic"] ,0),
        (f"Which approach helps you learn {lesson.subject} better?", ["Practice and review","Never revising","Only guessing","Avoiding examples"],0),
        ("What should you do when a topic is difficult?", ["Ask for a simpler explanation and practise again","Stop learning","Skip every question","Memorise without understanding"],0),
    ]
    for text, options, answer in bank: db.session.add(Question(quiz_id=q.id,text=text,options_json=__import__('json').dumps(options,ensure_ascii=False),correct_index=answer))
    db.session.commit()
    return ok(q.to_dict(full=True),"Practice quiz created.",201)

@bp.get("/<int:quiz_id>")
@login_required
def get_quiz(quiz_id):
    q=db.session.get(Quiz,quiz_id)
    if not q:return fail("Quiz not found.",404)
    return ok(q.to_dict(full=True))

@bp.post("/<int:quiz_id>/submit")
@login_required
def submit(quiz_id):
    q=db.session.get(Quiz,quiz_id)
    if not q:return fail("Quiz not found.",404)
    answers=(request.get_json(silent=True) or {}).get("answers",{})
    score=sum(1 for x in q.questions if str(x.id) in answers and int(answers[str(x.id)])==x.correct_index)
    total=len(q.questions)
    pct=round(score*100/total) if total else 0
    attempt=QuizAttempt(user_id=g.user.id,quiz_id=q.id,score=score,total=total,percentage=pct)
    db.session.add(attempt); db.session.commit()
    return ok(attempt.to_dict(),"Quiz submitted.")

@bp.get("/student/history")
@login_required
def history():
    return ok([x.to_dict() for x in QuizAttempt.query.filter_by(user_id=g.user.id).order_by(QuizAttempt.created_at.desc()).limit(100).all()])
