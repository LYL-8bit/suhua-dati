from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Dict, Optional
from database import get_db
import models
import auth as auth_utils
from sqlalchemy.sql import func

router = APIRouter(prefix="/api/submissions", tags=["submissions"])


class SubmitRequest(BaseModel):
    answers: Dict[str, str]           # {"question_id": "A", ...}
    assignment_id: Optional[int] = None
    classroom_session_id: Optional[int] = None


@router.post("")
def submit(
    req: SubmitRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可提交")

    # 防止重复提交课后作业
    if req.assignment_id:
        existing = db.query(models.Submission).filter(
            models.Submission.student_id == current_user.id,
            models.Submission.assignment_id == req.assignment_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="已提交过该作业")

    # 批改
    question_ids = [int(k) for k in req.answers.keys()]
    questions = db.query(models.Question).filter(models.Question.id.in_(question_ids)).all()
    q_map = {q.id: q for q in questions}

    score = 0
    total = len(questions)
    details = []
    wrong_updates = []

    for qid_str, student_answer in req.answers.items():
        qid = int(qid_str)
        q = q_map.get(qid)
        if not q:
            continue
        is_correct = student_answer.upper() == q.answer.upper()
        if is_correct:
            score += 1
        else:
            wrong_updates.append(qid)
        details.append({
            "question_id": qid,
            "student_answer": student_answer,
            "is_correct": is_correct,
        })

    # 保存提交记录
    submission = models.Submission(
        student_id=current_user.id,
        assignment_id=req.assignment_id,
        classroom_session_id=req.classroom_session_id,
        answers=req.answers,
        score=score,
        total=total,
    )
    db.add(submission)
    db.flush()

    for d in details:
        detail = models.SubmissionDetail(
            submission_id=submission.id,
            question_id=d["question_id"],
            student_answer=d["student_answer"],
            is_correct=d["is_correct"],
        )
        db.add(detail)

    # 更新错题本
    for qid in wrong_updates:
        wrong = db.query(models.WrongAnswer).filter(
            models.WrongAnswer.student_id == current_user.id,
            models.WrongAnswer.question_id == qid
        ).first()
        if wrong:
            wrong.wrong_count += 1
            wrong.last_wrong_at = func.now()
        else:
            db.add(models.WrongAnswer(
                student_id=current_user.id,
                question_id=qid,
            ))

    db.commit()

    # 返回结果（带答案解析）
    result_details = []
    for d in details:
        q = q_map.get(d["question_id"])
        result_details.append({
            "question_id": d["question_id"],
            "content": q.content if q else "",
            "options": q.options if q else [],
            "correct_answer": q.answer if q else "",
            "explanation": q.explanation if q else "",
            "student_answer": d["student_answer"],
            "is_correct": d["is_correct"],
        })

    return {
        "score": score,
        "total": total,
        "accuracy": round(score / total * 100, 1) if total > 0 else 0,
        "details": result_details,
    }


@router.get("/wrong-answers")
def get_wrong_answers(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="仅学生可查看")

    wrongs = db.query(models.WrongAnswer).filter(
        models.WrongAnswer.student_id == current_user.id
    ).order_by(models.WrongAnswer.wrong_count.desc()).all()

    result = []
    for w in wrongs:
        q = db.query(models.Question).filter(models.Question.id == w.question_id).first()
        if q:
            result.append({
                "wrong_id": w.id,
                "question_id": q.id,
                "content": q.content,
                "options": q.options,
                "answer": q.answer,
                "explanation": q.explanation,
                "tags": q.tags,
                "wrong_count": w.wrong_count,
                "last_wrong_at": w.last_wrong_at,
            })
    return result
