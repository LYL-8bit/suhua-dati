from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/classes", tags=["classes"])


class ClassCreate(BaseModel):
    name: str


class StudentCreate(BaseModel):
    name: str
    username: str
    password: str
    class_id: int


class StudentUpdate(BaseModel):
    name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    class_id: Optional[int] = None


@router.get("")
def list_classes(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    classes = db.query(models.Class).filter(models.Class.teacher_id == current_user.id).all()
    result = []
    for c in classes:
        student_count = db.query(models.User).filter(
            models.User.class_id == c.id,
            models.User.role == "student"
        ).count()
        result.append({"id": c.id, "name": c.name, "student_count": student_count, "created_at": c.created_at})
    return result


@router.post("")
def create_class(
    req: ClassCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    cls = models.Class(name=req.name, teacher_id=current_user.id)
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return {"id": cls.id, "name": cls.name}


@router.delete("/{class_id}")
def delete_class(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    cls = db.query(models.Class).filter(models.Class.id == class_id, models.Class.teacher_id == current_user.id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="班级不存在")
    db.delete(cls)
    db.commit()
    return {"ok": True}


@router.get("/{class_id}/students")
def list_students(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    students = db.query(models.User).filter(
        models.User.class_id == class_id,
        models.User.role == "student"
    ).all()
    result = []
    for s in students:
        # 计算档位
        total = db.query(models.SubmissionDetail).join(
            models.Submission, models.Submission.id == models.SubmissionDetail.submission_id
        ).filter(models.Submission.student_id == s.id).count()
        correct = db.query(models.SubmissionDetail).join(
            models.Submission, models.Submission.id == models.SubmissionDetail.submission_id
        ).filter(
            models.Submission.student_id == s.id,
            models.SubmissionDetail.is_correct == True
        ).count()
        accuracy = round(correct / total * 100, 1) if total > 0 else 0
        tier = 1 if accuracy >= 70 else 2
        result.append({
            "id": s.id,
            "name": s.name,
            "username": s.username,
            "accuracy": accuracy,
            "tier": tier,
            "total_answered": total,
        })
    return result


@router.post("/students")
def create_student(
    req: StudentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    existing = db.query(models.User).filter(models.User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")
    student = models.User(
        name=req.name,
        username=req.username,
        password_hash=auth_utils.get_password_hash(req.password),
        role="student",
        class_id=req.class_id,
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return {"id": student.id, "name": student.name, "username": student.username}


@router.put("/students/{student_id}")
def update_student(
    student_id: int,
    req: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    if req.name:
        student.name = req.name
    if req.username:
        student.username = req.username
    if req.password:
        student.password_hash = auth_utils.get_password_hash(req.password)
    if req.class_id:
        student.class_id = req.class_id
    db.commit()
    return {"ok": True}


@router.delete("/students/{student_id}")
def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    student = db.query(models.User).filter(models.User.id == student_id, models.User.role == "student").first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")
    db.delete(student)
    db.commit()
    return {"ok": True}
