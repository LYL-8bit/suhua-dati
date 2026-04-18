# -*- coding: utf-8 -*-
"""
闯关任务模块
第一关：在线作答（自动批改）
第二关：拍照提交 + 教师批注
第三关：抢答模式
"""
import uuid
import os
import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
import models
import auth as auth_utils

router = APIRouter(prefix="/api/challenge", tags=["challenge"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ===== 固定题目 =====
ROUND1_QUESTIONS = [
    {
        "id": "r1q1",
        "type": "fill",
        "content": "嫦娥号的环月轨道半径是 1000 公里，它的直径是多少公里？",
        "answer": "2000",
        "unit": "公里",
        "hint": "直径 = 半径 × 2",
    },
    {
        "id": "r1q2",
        "type": "fill",
        "content": "嫦娥号的环月轨道直径是 3000 公里，它的半径是多少公里？",
        "answer": "1500",
        "unit": "公里",
        "hint": "半径 = 直径 ÷ 2",
    },
    {
        "id": "r1q3",
        "type": "judge",
        "content": "圆的直径是半径的 2 倍。",
        "answer": "true",
        "hint": "d = 2r",
    },
]

ROUND3_QUESTIONS = [
    {
        "id": "r3q1",
        "subject": "科学联动",
        "content": "结合六年级科学《天体的运动》单元，为什么太阳系八大行星的公转轨道近似圆形？用今天学到的知识解释。",
    },
    {
        "id": "r3q2",
        "subject": "语文联动",
        "content": "结合课文《千年梦圆在今朝》，你能说出哪些和圆相关的诗词？这些诗词里的圆，寄托了怎样的情感？",
    },
    {
        "id": "r3q3",
        "subject": "道法联动",
        "content": "结合《科技发展 振兴中华》单元，从墨子的'一中同长'到今天的嫦娥探月，你有什么感受？",
    },
    {
        "id": "r3q4",
        "subject": "生活应用",
        "content": "车轮为什么是圆的？井盖为什么是圆的？",
    },
]

# ===== 内存状态（课堂进行中用，重启清空） =====
# session_id -> { round, submissions_r1, photos_r2, buzz_r3, answering_student }
challenge_sessions: Dict[str, dict] = {}

# WebSocket 连接池: session_id -> { student_id: WebSocket, "teacher": WebSocket }
ws_connections: Dict[str, Dict] = {}


def get_or_create_session(session_id: str):
    if session_id not in challenge_sessions:
        challenge_sessions[session_id] = {
            "round": 1,
            "submissions_r1": {},   # student_id -> {answers, score, submitted_at}
            "photos_r2": {},        # student_id -> {filename, annotation, tag, student_name}
            "buzz_r3": [],          # [{"student_id", "name", "time", "result"}]
            "answering": None,      # 当前点名的student_id
            "active_question": None,  # 当前第三关展示的题目id
        }
    return challenge_sessions[session_id]


# ===== 广播给所有连接 =====
async def broadcast(session_id: str, message: dict, exclude=None):
    if session_id not in ws_connections:
        return
    dead = []
    for key, ws in ws_connections[session_id].items():
        if key == exclude:
            continue
        try:
            await ws.send_text(json.dumps(message, ensure_ascii=False))
        except Exception:
            dead.append(key)
    for k in dead:
        ws_connections[session_id].pop(k, None)


# ===== 第一关 =====
@router.get("/round1/questions")
def get_round1_questions():
    return ROUND1_QUESTIONS


class Round1Submit(BaseModel):
    session_id: str
    answers: dict   # {"r1q1": "2000", "r1q2": "1500", "r1q3": "true"}


@router.post("/round1/submit")
async def submit_round1(
    req: Round1Submit,
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    session = get_or_create_session(req.session_id)
    score = 0
    details = []
    for q in ROUND1_QUESTIONS:
        student_ans = str(req.answers.get(q["id"], "")).strip()
        correct = student_ans.lower() == q["answer"].lower()
        if correct:
            score += 1
        details.append({
            "id": q["id"],
            "student_answer": student_ans,
            "correct_answer": q["answer"],
            "is_correct": correct,
            "hint": q["hint"],
        })
    session["submissions_r1"][str(current_user.id)] = {
        "student_name": current_user.name,
        "answers": req.answers,
        "score": score,
        "total": len(ROUND1_QUESTIONS),
        "details": details,
        "submitted_at": datetime.now().isoformat(),
    }
    await broadcast(req.session_id, {
        "type": "r1_update",
        "submitted_count": len(session["submissions_r1"]),
        "stats": _r1_stats(session),
    }, exclude=str(current_user.id))
    return {"score": score, "total": len(ROUND1_QUESTIONS), "details": details}


def _r1_stats(session):
    subs = session["submissions_r1"].values()
    if not subs:
        return []
    stats = {q["id"]: {"content": q["content"][:20], "correct": 0, "total": 0} for q in ROUND1_QUESTIONS}
    for sub in subs:
        for d in sub["details"]:
            stats[d["id"]]["total"] += 1
            if d["is_correct"]:
                stats[d["id"]]["correct"] += 1
    return [
        {
            "id": k,
            "content": v["content"],
            "correct": v["correct"],
            "total": v["total"],
            "accuracy": round(v["correct"] / v["total"] * 100, 1) if v["total"] > 0 else 0,
        }
        for k, v in stats.items()
    ]


@router.get("/round1/stats/{session_id}")
def get_round1_stats(
    session_id: str,
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = get_or_create_session(session_id)
    return {
        "submitted_count": len(session["submissions_r1"]),
        "submissions": list(session["submissions_r1"].values()),
        "stats": _r1_stats(session),
    }


# ===== 第二关 =====
@router.post("/round2/upload")
async def upload_photo(
    session_id: str = Form(...),
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    filename = f"{session_id}_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        content = await file.read()
        f.write(content)

    session = get_or_create_session(session_id)
    session["photos_r2"][str(current_user.id)] = {
        "student_id": current_user.id,
        "student_name": current_user.name,
        "filename": filename,
        "annotation": None,
        "tag": None,
        "uploaded_at": datetime.now().isoformat(),
    }
    await broadcast(session_id, {
        "type": "r2_new_photo",
        "student_id": current_user.id,
        "student_name": current_user.name,
        "filename": filename,
    })
    return {"filename": filename, "ok": True}


@router.get("/round2/photo/{filename}")
def get_photo(filename: str):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="图片不存在")
    return FileResponse(filepath)


class AnnotationSave(BaseModel):
    session_id: str
    student_id: int
    annotation_data: str   # base64 PNG（Canvas toDataURL）
    tag: Optional[str] = None   # "excellent" | "improve" | None


@router.post("/round2/annotate")
async def save_annotation(
    req: AnnotationSave,
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = get_or_create_session(req.session_id)
    photo = session["photos_r2"].get(str(req.student_id))
    if not photo:
        raise HTTPException(status_code=404, detail="未找到该学生的提交")

    # 保存批注图（base64写成文件）
    import base64
    ann_filename = f"ann_{req.session_id}_{req.student_id}.png"
    ann_path = os.path.join(UPLOAD_DIR, ann_filename)
    img_data = req.annotation_data
    if "," in img_data:
        img_data = img_data.split(",", 1)[1]
    with open(ann_path, "wb") as f:
        f.write(base64.b64decode(img_data))

    photo["annotation"] = ann_filename
    photo["tag"] = req.tag
    return {"ok": True, "annotation_file": ann_filename}


@router.get("/round2/photos/{session_id}")
def get_round2_photos(
    session_id: str,
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = get_or_create_session(session_id)
    return list(session["photos_r2"].values())


# ===== 第三关 =====
@router.get("/round3/questions")
def get_round3_questions():
    return ROUND3_QUESTIONS


class BuzzRequest(BaseModel):
    session_id: str


@router.post("/round3/buzz")
async def buzz(
    req: BuzzRequest,
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    session = get_or_create_session(req.session_id)
    already = any(b["student_id"] == current_user.id for b in session["buzz_r3"])
    if already:
        return {"rank": next(i + 1 for i, b in enumerate(session["buzz_r3"]) if b["student_id"] == current_user.id)}

    session["buzz_r3"].append({
        "student_id": current_user.id,
        "name": current_user.name,
        "time": datetime.now().isoformat(),
        "result": None,
    })
    rank = len(session["buzz_r3"])
    await broadcast(req.session_id, {
        "type": "r3_buzz",
        "rank": rank,
        "student_id": current_user.id,
        "name": current_user.name,
        "buzz_list": session["buzz_r3"],
    })
    return {"rank": rank}


class CallStudent(BaseModel):
    session_id: str
    student_id: int
    question_id: str


@router.post("/round3/call")
async def call_student(
    req: CallStudent,
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = get_or_create_session(req.session_id)
    session["answering"] = req.student_id
    session["active_question"] = req.question_id
    q = next((q for q in ROUND3_QUESTIONS if q["id"] == req.question_id), None)
    await broadcast(req.session_id, {
        "type": "r3_call",
        "student_id": req.student_id,
        "question": q,
    })
    return {"ok": True}


class MarkResult(BaseModel):
    session_id: str
    student_id: int
    result: str   # "correct" | "incorrect"


@router.post("/round3/mark")
async def mark_result(
    req: MarkResult,
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = get_or_create_session(req.session_id)
    for b in session["buzz_r3"]:
        if b["student_id"] == req.student_id:
            b["result"] = req.result
            break
    await broadcast(req.session_id, {
        "type": "r3_result",
        "student_id": req.student_id,
        "result": req.result,
        "buzz_list": session["buzz_r3"],
    })
    return {"ok": True}


@router.post("/round3/reset-buzz")
async def reset_buzz(
    session_id: str,
    current_user: models.User = Depends(auth_utils.require_teacher)
):
    session = get_or_create_session(session_id)
    session["buzz_r3"] = []
    session["answering"] = None
    await broadcast(session_id, {"type": "r3_reset"})
    return {"ok": True}


@router.get("/round3/status/{session_id}")
def get_round3_status(
    session_id: str,
    current_user: models.User = Depends(auth_utils.get_current_user)
):
    session = get_or_create_session(session_id)
    return {
        "buzz_list": session["buzz_r3"],
        "answering": session["answering"],
        "active_question": session["active_question"],
    }


# ===== WebSocket 实时推送 =====
@router.websocket("/ws/{session_id}/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    client_id: str,
):
    await websocket.accept()
    if session_id not in ws_connections:
        ws_connections[session_id] = {}
    ws_connections[session_id][client_id] = websocket
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_connections[session_id].pop(client_id, None)
