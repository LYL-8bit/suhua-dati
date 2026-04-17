# 数智学情平台

> 面向中小学课堂的班级管理、学情分析、错题答疑一体化系统。支持课后分层作业推送、课堂实时答题（扫码进入）、学情可视化分析。

---

## 功能概览

### 教师端
- **班级管理** — 创建班级、管理学生账号、查看每位学生档位
- **题库管理** — 按科目/难度/知识点管理题目（单选题），支持多科目
- **作业管理** — 发布分层作业，一档学生（正确率≥70%）做进阶题，二档学生做基础题，学生自动收到对应版本
- **课堂实时答题** — 一键发起课堂答题，大屏展示二维码，学生扫码进入，实时统计各题正确率
- **学情分析** — 班级整体看板（平均分、档位分布、知识点掌握热力图）+ 单生详情（趋势折线图、雷达图）

### 学生端
- **我的作业** — 查看并完成教师布置的作业，提交后立即显示得分和解析
- **错题本** — 自动收录所有做错的题目，显示正确答案和解析
- **我的学情** — 个人正确率、当前档位、知识点雷达图、超过班级百分比

---

## 技术栈

| 层次 | 技术 |
|------|------|
| 前端 | Vue 3 + Element Plus + ECharts |
| 后端 | Python FastAPI |
| 数据库 | SQLite（本地）/ 可迁移 MySQL（云端） |
| 鉴权 | JWT Token |

---

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+

### 1. 克隆项目

```bash
git clone https://github.com/LYL-8bit/suhua-dati.git
cd suhua-dati
```

### 2. 启动后端

```bash
cd backend
pip install -r requirements.txt
python seed.py          # 初始化数据库和假数据
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

### 4. 访问系统

打开浏览器访问：**http://localhost:5173**

| 角色 | 账号 | 密码 |
|------|------|------|
| 教师 | `teacher` | `123456` |
| 学生 | `s01` ~ `s20` | `123456` |

> Windows 用户可直接双击根目录下的 `start.bat` 一键启动。

---

## 项目结构

```
suhua-dati/
├── backend/                # FastAPI 后端
│   ├── main.py             # 入口，注册路由
│   ├── models.py           # 数据库模型
│   ├── database.py         # SQLite 连接
│   ├── auth.py             # JWT 鉴权
│   ├── seed.py             # 假数据初始化脚本
│   ├── requirements.txt
│   └── routers/
│       ├── auth.py         # 登录接口
│       ├── classes.py      # 班级 & 学生管理
│       ├── subjects.py     # 科目管理
│       ├── questions.py    # 题库管理
│       ├── assignments.py  # 作业管理
│       ├── submissions.py  # 答题提交 & 错题本
│       ├── classroom.py    # 课堂实时答题
│       └── analysis.py     # 学情分析
│
├── frontend/               # Vue 3 前端
│   └── src/
│       ├── views/
│       │   ├── teacher/    # 教师端页面
│       │   ├── student/    # 学生端页面
│       │   └── classroom/  # 扫码答题页
│       ├── layouts/        # 布局组件
│       ├── router/         # 路由配置
│       ├── stores/         # Pinia 状态管理
│       └── api/            # Axios 封装
│
├── start.bat               # Windows 一键启动脚本
├── reset-data.bat          # 重置假数据脚本
└── README.md
```

---

## 数据库说明

默认使用 SQLite，数据库文件位于 `backend/data/db.sqlite3`，无需额外安装数据库软件。

如需迁移到 MySQL（云部署），修改 `backend/database.py` 中的连接字符串即可：

```python
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://user:password@host/dbname"
```

---

## 档位逻辑说明

系统根据学生历史答题的综合正确率自动判定档位，并在每次推送作业时动态计算：

| 档位 | 条件 | 推送题目 |
|------|------|------|
| 一档（优秀） | 综合正确率 ≥ 70% | 进阶题（difficulty = 2） |
| 二档（需加强） | 综合正确率 < 70% | 基础题（difficulty = 1） |

学生只看到自己的那份作业，不感知分档。

---

## 课堂实时答题流程

1. 教师在「课堂答题」页点击「发起课堂答题」，选择班级、科目和题目
2. 系统生成二维码，显示在大屏
3. 学生用手机扫码，输入账号密码后进入答题页
4. 学生提交后，教师端实时显示每道题的班级正确率
5. 教师点击「结束」关闭本次课堂会话

---

## API 文档

后端启动后访问：**http://localhost:8001/docs**

自动生成的 Swagger 交互文档，可直接在页面测试所有接口。

---

## License

MIT
