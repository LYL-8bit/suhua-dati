from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models

from routers import auth, classes, subjects, questions, assignments, submissions, classroom, analysis

# 创建数据库表
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="数智学情平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(classes.router)
app.include_router(subjects.router)
app.include_router(questions.router)
app.include_router(assignments.router)
app.include_router(submissions.router)
app.include_router(classroom.router)
app.include_router(analysis.router)


@app.get("/")
def root():
    return {"message": "数智学情平台 API 运行中"}
