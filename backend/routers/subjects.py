from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/subjects", tags=["subjects"])


class SubjectCreate(BaseModel):
    name: str


@router.get("")
def list_subjects(db: Session = Depends(get_db)):
    subjects = db.query(models.Subject).all()
    return [{"id": s.id, "name": s.name} for s in subjects]


@router.post("")
def create_subject(
    req: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    subject = models.Subject(name=req.name)
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return {"id": subject.id, "name": subject.name}


@router.delete("/{subject_id}")
def delete_subject(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    subject = db.query(models.Subject).filter(models.Subject.id == subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="科目不存在")
    db.delete(subject)
    db.commit()
    return {"ok": True}
