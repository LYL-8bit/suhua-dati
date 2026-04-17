from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/questions", tags=["questions"])


class QuestionCreate(BaseModel):
    content: str
    options: List[str]       # ["A.选项1", "B.选项2", "C.选项3", "D.选项4"]
    answer: str              # "A"
    explanation: Optional[str] = None
    difficulty: int = 1      # 1=基础 2=进阶
    tags: Optional[List[str]] = []
    subject_id: int


class QuestionUpdate(BaseModel):
    content: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[int] = None
    tags: Optional[List[str]] = None
    subject_id: Optional[int] = None


@router.get("")
def list_questions(
    subject_id: Optional[int] = Query(None),
    difficulty: Optional[int] = Query(None),
    tag: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    query = db.query(models.Question)
    if subject_id:
        query = query.filter(models.Question.subject_id == subject_id)
    if difficulty:
        query = query.filter(models.Question.difficulty == difficulty)
    questions = query.all()

    result = []
    for q in questions:
        if tag and tag not in (q.tags or []):
            continue
        result.append({
            "id": q.id,
            "content": q.content,
            "options": q.options,
            "answer": q.answer,
            "explanation": q.explanation,
            "difficulty": q.difficulty,
            "tags": q.tags,
            "subject_id": q.subject_id,
        })
    return result


@router.post("")
def create_question(
    req: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    q = models.Question(
        content=req.content,
        options=req.options,
        answer=req.answer,
        explanation=req.explanation,
        difficulty=req.difficulty,
        tags=req.tags,
        subject_id=req.subject_id,
        created_by=current_user.id,
    )
    db.add(q)
    db.commit()
    db.refresh(q)
    return {"id": q.id, "content": q.content}


@router.put("/{question_id}")
def update_question(
    question_id: int,
    req: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    q = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    for field, value in req.dict(exclude_none=True).items():
        setattr(q, field, value)
    db.commit()
    return {"ok": True}


@router.delete("/{question_id}")
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    q = db.query(models.Question).filter(models.Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="题目不存在")
    db.delete(q)
    db.commit()
    return {"ok": True}
