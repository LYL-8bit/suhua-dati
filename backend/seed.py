# -*- coding: utf-8 -*-
"""
假数据初始化脚本
运行: python seed.py
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

from datetime import datetime, timedelta
import random
import uuid
from database import SessionLocal, engine
import models
from auth import get_password_hash

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()

def clear_all():
    db.query(models.WrongAnswer).delete()
    db.query(models.SubmissionDetail).delete()
    db.query(models.Submission).delete()
    db.query(models.ClassroomSession).delete()
    db.query(models.Assignment).delete()
    db.query(models.Question).delete()
    db.query(models.Subject).delete()
    db.query(models.User).filter(models.User.role == "student").delete()
    db.query(models.Class).delete()
    db.query(models.User).filter(models.User.role == "teacher").delete()
    db.commit()

clear_all()

# ===== 科目 =====
subjects = []
for name in [u"数学", u"语文", u"英语"]:
    s = models.Subject(name=name)
    db.add(s)
    db.flush()
    subjects.append(s)
db.commit()
math_id = subjects[0].id
chinese_id = subjects[1].id
english_id = subjects[2].id

# ===== 教师 =====
teacher = models.User(
    name=u"苏华",
    username="teacher",
    password_hash=get_password_hash("123456"),
    role="teacher",
)
db.add(teacher)
db.flush()

# ===== 班级 =====
cls = models.Class(name=u"六年级（1）班", teacher_id=teacher.id)
db.add(cls)
db.flush()
db.commit()

# ===== 学生 =====
student_names = [
    u"张明", u"李华", u"王芳", u"赵磊", u"陈静",
    u"刘洋", u"杨晨", u"周颖", u"吴浩", u"郑丽",
    u"孙强", u"钱琳", u"林峰", u"徐敏", u"何宇",
    u"朱婷", u"黄鹏", u"许雪", u"胡杰", u"谢欣",
]
students = []
for i, name in enumerate(student_names):
    s = models.User(
        name=name,
        username="s" + str(i+1).zfill(2),
        password_hash=get_password_hash("123456"),
        role="student",
        class_id=cls.id,
    )
    db.add(s)
    db.flush()
    students.append(s)
db.commit()

# ===== 题库（数学-圆的认识） =====
math_questions_data = [
    {
        "content": u"圆的圆心到圆上任意一点的距离叫做什么？",
        "options": [u"A.直径", u"B.半径", u"C.弦", u"D.弧"],
        "answer": "B",
        "explanation": u"圆的圆心到圆上任意一点的距离叫做半径，通常用字母r表示。",
        "difficulty": 1,
        "tags": [u"半径", u"基础概念"],
    },
    {
        "content": u"通过圆心且两端都在圆上的线段叫做什么？",
        "options": [u"A.半径", u"B.弦", u"C.直径", u"D.切线"],
        "answer": "C",
        "explanation": u"通过圆心且两端都在圆上的线段叫做直径，通常用字母d表示。",
        "difficulty": 1,
        "tags": [u"直径", u"基础概念"],
    },
    {
        "content": u"同一个圆内，直径和半径的关系是？",
        "options": [u"A.d = r", u"B.d = 2r", u"C.r = 2d", u"D.d = 3r"],
        "answer": "B",
        "explanation": u"直径等于半径的2倍，即 d = 2r，或 r = d/2。",
        "difficulty": 1,
        "tags": [u"直径", u"半径", u"基础概念"],
    },
    {
        "content": u"圆的大小由什么决定？",
        "options": [u"A.圆心的位置", u"B.半径的长短", u"C.直径的条数", u"D.圆弧的长短"],
        "answer": "B",
        "explanation": u"圆的大小由半径决定：半径越大，圆越大；半径越小，圆越小。",
        "difficulty": 1,
        "tags": [u"半径", u"圆的大小"],
    },
    {
        "content": u"圆的位置由什么决定？",
        "options": [u"A.半径", u"B.直径", u"C.圆心", u"D.弧长"],
        "answer": "C",
        "explanation": u"圆心决定圆的位置：圆心在哪里，圆就在哪里。",
        "difficulty": 1,
        "tags": [u"圆心", u"圆的位置"],
    },
    {
        "content": u"同一个圆内，所有半径的长度关系是？",
        "options": [u"A.不相等", u"B.全部相等", u"C.只有部分相等", u"D.无法确定"],
        "answer": "B",
        "explanation": u"同一个圆内，所有半径都相等。这是圆的重要特性。",
        "difficulty": 1,
        "tags": [u"半径", u"一中同长"],
    },
    {
        "content": u"墨经中说圆是一中同长，其中一中指的是？",
        "options": [u"A.一条直径", u"B.一个圆心", u"C.一半半径", u"D.一段弧"],
        "answer": "B",
        "explanation": u"一中指圆心，同长指从圆心到圆上各点距离相等，即半径相等。",
        "difficulty": 2,
        "tags": [u"圆心", u"一中同长", u"数学文化"],
    },
    {
        "content": u"用圆规画圆时，两脚间的距离决定了圆的什么？",
        "options": [u"A.圆心位置", u"B.圆的半径大小", u"C.直径条数", u"D.弧的长度"],
        "answer": "B",
        "explanation": u"圆规两脚间的距离就是所画圆的半径，距离越大圆越大。",
        "difficulty": 1,
        "tags": [u"半径", u"画圆"],
    },
    {
        "content": u"下列关于圆的说法正确的是？",
        "options": [
            u"A.圆有无数条直径且每条长度都不同",
            u"B.直径一定比半径长",
            u"C.同一个圆内直径是最长的弦",
            u"D.半径可以延伸到圆外",
        ],
        "answer": "C",
        "explanation": u"直径是圆内最长的弦。A错（同圆直径相等），D错（半径只到圆上）。",
        "difficulty": 2,
        "tags": [u"直径", u"半径", u"综合"],
    },
    {
        "content": u"将一个圆对折，折痕所在的直线一定经过？",
        "options": [u"A.弧的中点", u"B.圆心", u"C.弦的端点", u"D.随机位置"],
        "answer": "B",
        "explanation": u"圆的对称轴都经过圆心，对折后折痕必过圆心。",
        "difficulty": 2,
        "tags": [u"圆心", u"对称", u"进阶"],
    },
    {
        "content": u"一个圆的半径是5cm，则其直径是多少？",
        "options": [u"A.5cm", u"B.10cm", u"C.15cm", u"D.2.5cm"],
        "answer": "B",
        "explanation": u"d = 2r = 2×5 = 10cm。",
        "difficulty": 1,
        "tags": [u"直径", u"半径", u"计算"],
    },
    {
        "content": u"已知圆的直径是12cm，则其半径是多少？",
        "options": [u"A.24cm", u"B.12cm", u"C.6cm", u"D.3cm"],
        "answer": "C",
        "explanation": u"r = d/2 = 12/2 = 6cm。",
        "difficulty": 1,
        "tags": [u"直径", u"半径", u"计算"],
    },
    {
        "content": u"探月工程中月球基地建成圆形，主要原因是圆形具有？",
        "options": [u"A.最大的面积", u"B.等距离特性各方向受力均匀", u"C.最多的角", u"D.最小的周长"],
        "answer": "B",
        "explanation": u"圆形各方向到圆心距离相等，结构受力均匀，在极端环境中最稳固。",
        "difficulty": 2,
        "tags": [u"圆的应用", u"工程", u"进阶"],
    },
    {
        "content": u"正多边形的边数越多，形状越接近？",
        "options": [u"A.正方形", u"B.三角形", u"C.圆形", u"D.椭圆"],
        "answer": "C",
        "explanation": u"正多边形边数趋向无穷大时，形状趋近于圆，这体现了极限思想。",
        "difficulty": 2,
        "tags": [u"极限思想", u"进阶"],
    },
    {
        "content": u"下列图形中，哪个的对称轴有无数条？",
        "options": [u"A.正三角形", u"B.长方形", u"C.圆", u"D.正方形"],
        "answer": "C",
        "explanation": u"圆的任意一条直径所在的直线都是对称轴，因此有无数条对称轴。",
        "difficulty": 2,
        "tags": [u"对称", u"进阶"],
    },
]

math_qs = []
for d in math_questions_data:
    q = models.Question(
        content=d["content"],
        options=d["options"],
        answer=d["answer"],
        explanation=d["explanation"],
        difficulty=d["difficulty"],
        tags=d["tags"],
        subject_id=math_id,
        created_by=teacher.id,
    )
    db.add(q)
    db.flush()
    math_qs.append(q)
db.commit()

basic_ids = [q.id for q in math_qs if q.difficulty == 1]
advanced_ids = [q.id for q in math_qs if q.difficulty == 2]

# ===== 作业 =====
now = datetime.now()
assignments = []
for i in range(3):
    a = models.Assignment(
        title=u"圆的认识 第" + str(i+1) + u"次作业",
        class_id=cls.id,
        subject_id=math_id,
        deadline=now + timedelta(days=7 - i * 2),
        status="published",
        tier1_question_ids=advanced_ids,
        tier2_question_ids=basic_ids[:5],
    )
    db.add(a)
    db.flush()
    assignments.append(a)
db.commit()

# ===== 课堂答题会话 =====
session = models.ClassroomSession(
    title=u"课堂练习-圆的基础概念",
    class_id=cls.id,
    subject_id=math_id,
    question_ids=basic_ids[:5],
    status="closed",
    qr_token=uuid.uuid4().hex,
    created_by=teacher.id,
    created_at=now - timedelta(days=3),
)
db.add(session)
db.flush()
db.commit()

# ===== 模拟学生提交 =====
def simulate_submission(student, question_ids, accuracy_target, assignment=None, sess=None, offset_days=0):
    questions = db.query(models.Question).filter(models.Question.id.in_(question_ids)).all()
    if not questions:
        return
    answers = {}
    for q in questions:
        if random.random() < accuracy_target:
            answers[str(q.id)] = q.answer
        else:
            choices = [x for x in ["A", "B", "C", "D"] if x != q.answer]
            answers[str(q.id)] = random.choice(choices)

    score = 0
    total = len(questions)
    details_data = []
    wrong_qids = []
    for q in questions:
        student_ans = answers.get(str(q.id), "A")
        is_correct = student_ans.upper() == q.answer.upper()
        if is_correct:
            score += 1
        else:
            wrong_qids.append(q.id)
        details_data.append((q.id, student_ans, is_correct))

    sub = models.Submission(
        student_id=student.id,
        assignment_id=assignment.id if assignment else None,
        classroom_session_id=sess.id if sess else None,
        answers=answers,
        score=score,
        total=total,
        submitted_at=now - timedelta(days=offset_days),
    )
    db.add(sub)
    db.flush()

    for qid, ans, correct in details_data:
        db.add(models.SubmissionDetail(
            submission_id=sub.id,
            question_id=qid,
            student_answer=ans,
            is_correct=correct,
        ))

    for qid in wrong_qids:
        existing = db.query(models.WrongAnswer).filter(
            models.WrongAnswer.student_id == student.id,
            models.WrongAnswer.question_id == qid
        ).first()
        if existing:
            existing.wrong_count += 1
        else:
            db.add(models.WrongAnswer(student_id=student.id, question_id=qid))

# 前10名高正确率（一档）
for i, student in enumerate(students[:10]):
    acc = random.uniform(0.75, 0.95)
    for j, assignment in enumerate(assignments):
        simulate_submission(student, advanced_ids, acc, assignment=assignment, offset_days=j * 2 + 1)
    simulate_submission(student, basic_ids[:5], acc, sess=session, offset_days=3)

# 后10名低正确率（二档）
for i, student in enumerate(students[10:]):
    acc = random.uniform(0.35, 0.65)
    for j, assignment in enumerate(assignments):
        simulate_submission(student, basic_ids[:5], acc, assignment=assignment, offset_days=j * 2 + 1)
    simulate_submission(student, basic_ids[:5], acc, sess=session, offset_days=3)

db.commit()
db.close()

print("假数据初始化完成！")
print("教师账号: teacher / 123456")
print("学生账号: s01~s20 / 123456")
print("班级: 六年级1班，共" + str(len(students)) + "名学生")
print("题库: 数学" + str(len(math_qs)) + "题")
print("作业: " + str(len(assignments)) + "次")
