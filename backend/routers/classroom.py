import uuid
import os
import qrcode
import io
import base64
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/classroom", tags=["classroom"])


class SessionCreate(BaseModel):
    title: str
    class_id: int
    subject_id: int
    question_ids: List[int]


def make_qr_base64(url: str) -> str:
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


@router.post("/sessions")
def create_session(
    req: SessionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    token = uuid.uuid4().hex
    session = models.ClassroomSession(
        title=req.title,
        class_id=req.class_id,
        subject_id=req.subject_id,
        question_ids=req.question_ids,
        qr_token=token,
        created_by=current_user.id,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    frontend_base = os.environ.get("FRONTEND_URL", "http://localhost:5173")
    join_url = f"{frontend_base}/classroom/join/{token}"
    qr_b64 = make_qr_base64(join_url)

    return {
        "id": session.id,
        "token": token,
        "join_url": join_url,
        "qr_base64": qr_b64,
    }


@router.get("/sessions")
def list_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    sessions = db.query(models.ClassroomSession).filter(
        models.ClassroomSession.created_by == current_user.id
    ).order_by(models.ClassroomSession.created_at.desc()).all()

    result = []
    for s in sessions:
        sub_count = db.query(models.Submission).filter(
            models.Submission.classroom_session_id == s.id
        ).count()
        student_count = db.query(models.User).filter(
            models.User.class_id == s.class_id,
            models.User.role == "student"
        ).count()
        result.append({
            "id": s.id,
            "title": s.title,
            "class_id": s.class_id,
            "subject_id": s.subject_id,
            "status": s.status,
            "question_count": len(s.question_ids or []),
            "submission_count": sub_count,
            "student_count": student_count,
            "created_at": s.created_at,
        })
    return result


@router.get("/sessions/{session_id}/stats")
def session_stats(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = db.query(models.ClassroomSession).filter(
        models.ClassroomSession.id == session_id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    submissions = db.query(models.Submission).filter(
        models.Submission.classroom_session_id == session_id
    ).all()

    student_count = db.query(models.User).filter(
        models.User.class_id == session.class_id,
        models.User.role == "student"
    ).count()

    # 每道题的正确率统计
    question_stats = {}
    for qid in (session.question_ids or []):
        total = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(
            models.Submission.classroom_session_id == session_id,
            models.SubmissionDetail.question_id == qid
        ).count()
        correct = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(
            models.Submission.classroom_session_id == session_id,
            models.SubmissionDetail.question_id == qid,
            models.SubmissionDetail.is_correct == True
        ).count()
        q = db.query(models.Question).filter(models.Question.id == qid).first()
        question_stats[qid] = {
            "question_id": qid,
            "content": q.content[:50] + "..." if q and len(q.content) > 50 else (q.content if q else ""),
            "total": total,
            "correct": correct,
            "accuracy": round(correct / total * 100, 1) if total > 0 else 0,
        }

    submitted_ids = [s.student_id for s in submissions]
    return {
        "session_id": session_id,
        "title": session.title,
        "status": session.status,
        "student_count": student_count,
        "submitted_count": len(submissions),
        "avg_score": round(sum(s.score for s in submissions) / len(submissions), 1) if submissions else 0,
        "avg_accuracy": round(sum(s.score / s.total for s in submissions if s.total > 0) / len(submissions) * 100, 1) if submissions else 0,
        "question_stats": list(question_stats.values()),
    }


@router.post("/sessions/{session_id}/close")
def close_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = db.query(models.ClassroomSession).filter(
        models.ClassroomSession.id == session_id,
        models.ClassroomSession.created_by == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")
    session.status = "closed"
    db.commit()
    return {"ok": True}


@router.get("/join/{token}")
def join_by_token(token: str, db: Session = Depends(get_db)):
    session = db.query(models.ClassroomSession).filter(
        models.ClassroomSession.qr_token == token
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="无效的课堂码")
    if session.status == "closed":
        raise HTTPException(status_code=400, detail="课堂已结束")

    questions = db.query(models.Question).filter(
        models.Question.id.in_(session.question_ids or [])
    ).all()
    return {
        "session_id": session.id,
        "title": session.title,
        "questions": [
            {
                "id": q.id,
                "content": q.content,
                "options": q.options,
            } for q in questions
        ]
    }
