from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    teacher = relationship("User", back_populates="classes", foreign_keys=[teacher_id])
    students = relationship("User", back_populates="student_class", foreign_keys="User.class_id")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)  # teacher / student
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    created_at = Column(DateTime, default=func.now())

    classes = relationship("Class", back_populates="teacher", foreign_keys="Class.teacher_id")
    student_class = relationship("Class", back_populates="students", foreign_keys=[class_id])
    submissions = relationship("Submission", back_populates="student")
    wrong_answers = relationship("WrongAnswer", back_populates="student")


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # 数学、语文、英语
    created_at = Column(DateTime, default=func.now())

    questions = relationship("Question", back_populates="subject")


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)   # ["A.选项1", "B.选项2", ...]
    answer = Column(String(10), nullable=False)  # "A" / "B" / "C" / "D"
    explanation = Column(Text, nullable=True)
    difficulty = Column(Integer, default=1)  # 1=基础 2=进阶
    tags = Column(JSON, default=list)        # ["圆心", "半径"]
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    subject = relationship("Subject", back_populates="questions")


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    deadline = Column(DateTime, nullable=True)
    status = Column(String(20), default="published")  # draft / published
    tier1_question_ids = Column(JSON, default=list)   # 一档题目（进阶）
    tier2_question_ids = Column(JSON, default=list)   # 二档题目（基础）
    created_at = Column(DateTime, default=func.now())

    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submissions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    classroom_session_id = Column(Integer, ForeignKey("classroom_sessions.id"), nullable=True)
    answers = Column(JSON, default=dict)       # {question_id: "A", ...}
    score = Column(Integer, default=0)
    total = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=func.now())

    student = relationship("User", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
    details = relationship("SubmissionDetail", back_populates="submission")


class SubmissionDetail(Base):
    __tablename__ = "submission_details"
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    student_answer = Column(String(10))
    is_correct = Column(Boolean, default=False)

    submission = relationship("Submission", back_populates="details")


class WrongAnswer(Base):
    __tablename__ = "wrong_answers"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    wrong_count = Column(Integer, default=1)
    last_wrong_at = Column(DateTime, default=func.now())

    student = relationship("User", back_populates="wrong_answers")
    question = relationship("Question")


class ClassroomSession(Base):
    """课堂实时答题会话"""
    __tablename__ = "classroom_sessions"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    question_ids = Column(JSON, default=list)
    status = Column(String(20), default="active")   # active / closed
    qr_token = Column(String(100), unique=True)     # 二维码唯一token
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=func.now())

    submissions = relationship("Submission", back_populates=None)
