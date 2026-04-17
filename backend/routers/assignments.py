from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/assignments", tags=["assignments"])


class AssignmentCreate(BaseModel):
    title: str
    class_id: int
    subject_id: int
    deadline: Optional[datetime] = None
    tier1_question_ids: List[int] = []
    tier2_question_ids: List[int] = []


@router.get("")
def list_assignments(
    class_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    if current_user.role == "teacher":
        query = db.query(models.Assignment)
        if class_id:
            query = query.filter(models.Assignment.class_id == class_id)
        assignments = query.order_by(models.Assignment.created_at.desc()).all()
    else:
        # 学生：根据档位获取对应作业
        student = current_user
        total = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(models.Submission.student_id == student.id).count()
        correct = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(
            models.Submission.student_id == student.id,
            models.SubmissionDetail.is_correct == True
        ).count()
        accuracy = correct / total if total > 0 else 0
        tier = 1 if accuracy >= 0.7 else 2

        assignments = db.query(models.Assignment).filter(
            models.Assignment.class_id == student.class_id,
            models.Assignment.status == "published"
        ).order_by(models.Assignment.created_at.desc()).all()

        result = []
        for a in assignments:
            # 判断是否已提交
            submitted = db.query(models.Submission).filter(
                models.Submission.student_id == student.id,
                models.Submission.assignment_id == a.id
            ).first()

            question_ids = a.tier1_question_ids if tier == 1 else a.tier2_question_ids
            result.append({
                "id": a.id,
                "title": a.title,
                "subject_id": a.subject_id,
                "deadline": a.deadline,
                "tier": tier,
                "question_count": len(question_ids),
                "submitted": submitted is not None,
                "score": submitted.score if submitted else None,
                "total": submitted.total if submitted else None,
            })
        return result

    result = []
    for a in assignments:
        submission_count = db.query(models.Submission).filter(
            models.Submission.assignment_id == a.id
        ).count()
        result.append({
            "id": a.id,
            "title": a.title,
            "class_id": a.class_id,
            "subject_id": a.subject_id,
            "deadline": a.deadline,
            "status": a.status,
            "tier1_count": len(a.tier1_question_ids or []),
            "tier2_count": len(a.tier2_question_ids or []),
            "submission_count": submission_count,
            "created_at": a.created_at,
        })
    return result


@router.post("")
def create_assignment(
    req: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    a = models.Assignment(
        title=req.title,
        class_id=req.class_id,
        subject_id=req.subject_id,
        deadline=req.deadline,
        tier1_question_ids=req.tier1_question_ids,
        tier2_question_ids=req.tier2_question_ids,
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"id": a.id, "title": a.title}


@router.get("/{assignment_id}/questions")
def get_assignment_questions(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    assignment = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="作业不存在")

    if current_user.role == "student":
        total = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(models.Submission.student_id == current_user.id).count()
        correct = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(
            models.Submission.student_id == current_user.id,
            models.SubmissionDetail.is_correct == True
        ).count()
        accuracy = correct / total if total > 0 else 0
        tier = 1 if accuracy >= 0.7 else 2
        question_ids = assignment.tier1_question_ids if tier == 1 else assignment.tier2_question_ids
    else:
        question_ids = list(set((assignment.tier1_question_ids or []) + (assignment.tier2_question_ids or [])))

    questions = db.query(models.Question).filter(models.Question.id.in_(question_ids)).all()
    result = []
    for q in questions:
        item = {
            "id": q.id,
            "content": q.content,
            "options": q.options,
            "difficulty": q.difficulty,
            "tags": q.tags,
        }
        if current_user.role == "teacher":
            item["answer"] = q.answer
            item["explanation"] = q.explanation
        result.append(item)
    return result


@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    a = db.query(models.Assignment).filter(models.Assignment.id == assignment_id).first()
    if not a:
        raise HTTPException(status_code=404, detail="作业不存在")
    db.delete(a)
    db.commit()
    return {"ok": True}
