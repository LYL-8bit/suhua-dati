from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.get("/class/{class_id}")
def class_analysis(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    students = db.query(models.User).filter(
        models.User.class_id == class_id,
        models.User.role == "student"
    ).all()

    student_data = []
    tag_stats = {}  # 知识点统计

    for s in students:
        details = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(models.Submission.student_id == s.id).all()

        total = len(details)
        correct = sum(1 for d in details if d.is_correct)
        accuracy = round(correct / total * 100, 1) if total > 0 else 0
        tier = 1 if accuracy >= 70 else 2

        # 知识点统计
        for d in details:
            q = db.query(models.Question).filter(models.Question.id == d.question_id).first()
            if q and q.tags:
                for tag in q.tags:
                    if tag not in tag_stats:
                        tag_stats[tag] = {"total": 0, "correct": 0}
                    tag_stats[tag]["total"] += 1
                    if d.is_correct:
                        tag_stats[tag]["correct"] += 1

        # 历次作业趋势
        submissions = db.query(models.Submission).filter(
            models.Submission.student_id == s.id,
            models.Submission.assignment_id != None
        ).order_by(models.Submission.submitted_at).all()

        trend = [
            {
                "date": sub.submitted_at.strftime("%m/%d") if sub.submitted_at else "",
                "accuracy": round(sub.score / sub.total * 100, 1) if sub.total > 0 else 0
            }
            for sub in submissions
        ]

        student_data.append({
            "id": s.id,
            "name": s.name,
            "total_answered": total,
            "correct": correct,
            "accuracy": accuracy,
            "tier": tier,
            "trend": trend,
        })

    # 班级整体
    all_accuracies = [s["accuracy"] for s in student_data if s["total_answered"] > 0]
    avg_accuracy = round(sum(all_accuracies) / len(all_accuracies), 1) if all_accuracies else 0
    tier1_count = sum(1 for s in student_data if s["tier"] == 1)
    tier2_count = sum(1 for s in student_data if s["tier"] == 2)

    # 知识点掌握率
    tag_analysis = [
        {
            "tag": tag,
            "accuracy": round(v["correct"] / v["total"] * 100, 1) if v["total"] > 0 else 0,
            "total": v["total"],
        }
        for tag, v in tag_stats.items()
    ]
    tag_analysis.sort(key=lambda x: x["accuracy"])

    # 分布：各分数段人数
    score_distribution = {
        "90-100": sum(1 for s in student_data if s["accuracy"] >= 90),
        "70-89": sum(1 for s in student_data if 70 <= s["accuracy"] < 90),
        "60-69": sum(1 for s in student_data if 60 <= s["accuracy"] < 70),
        "0-59": sum(1 for s in student_data if s["accuracy"] < 60),
    }

    return {
        "student_count": len(students),
        "avg_accuracy": avg_accuracy,
        "tier1_count": tier1_count,
        "tier2_count": tier2_count,
        "score_distribution": score_distribution,
        "tag_analysis": tag_analysis,
        "students": student_data,
    }


@router.get("/student/{student_id}")
def student_analysis(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    # 学生只能看自己
    if current_user.role == "student" and current_user.id != student_id:
        raise HTTPException(status_code=403, detail="无权查看他人数据")

    student = db.query(models.User).filter(models.User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学生不存在")

    details = db.query(models.SubmissionDetail).join(
        models.Submission
    ).filter(models.Submission.student_id == student_id).all()

    total = len(details)
    correct = sum(1 for d in details if d.is_correct)
    accuracy = round(correct / total * 100, 1) if total > 0 else 0
    tier = 1 if accuracy >= 70 else 2

    # 知识点掌握
    tag_stats = {}
    for d in details:
        q = db.query(models.Question).filter(models.Question.id == d.question_id).first()
        if q and q.tags:
            for tag in q.tags:
                if tag not in tag_stats:
                    tag_stats[tag] = {"total": 0, "correct": 0}
                tag_stats[tag]["total"] += 1
                if d.is_correct:
                    tag_stats[tag]["correct"] += 1

    tag_analysis = [
        {
            "tag": tag,
            "accuracy": round(v["correct"] / v["total"] * 100, 1) if v["total"] > 0 else 0,
        }
        for tag, v in tag_stats.items()
    ]

    # 趋势
    submissions = db.query(models.Submission).filter(
        models.Submission.student_id == student_id,
        models.Submission.assignment_id != None
    ).order_by(models.Submission.submitted_at).all()

    trend = [
        {
            "date": sub.submitted_at.strftime("%m/%d") if sub.submitted_at else "",
            "accuracy": round(sub.score / sub.total * 100, 1) if sub.total > 0 else 0,
            "score": sub.score,
            "total": sub.total,
        }
        for sub in submissions
    ]

    # 班级排名
    class_students = db.query(models.User).filter(
        models.User.class_id == student.class_id,
        models.User.role == "student"
    ).all()
    class_accuracies = []
    for cs in class_students:
        d_total = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(models.Submission.student_id == cs.id).count()
        d_correct = db.query(models.SubmissionDetail).join(
            models.Submission
        ).filter(
            models.Submission.student_id == cs.id,
            models.SubmissionDetail.is_correct == True
        ).count()
        class_accuracies.append(d_correct / d_total * 100 if d_total > 0 else 0)

    beat_percent = 0
    if class_accuracies:
        beat_percent = round(sum(1 for a in class_accuracies if a < accuracy) / len(class_accuracies) * 100)

    return {
        "student_id": student_id,
        "name": student.name,
        "total_answered": total,
        "correct": correct,
        "accuracy": accuracy,
        "tier": tier,
        "beat_percent": beat_percent,
        "tag_analysis": tag_analysis,
        "trend": trend,
    }
