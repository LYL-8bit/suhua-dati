@echo off
echo 启动数智学情平台...
echo.

echo [1/2] 启动后端 (端口 8001)...
start "后端服务" cmd /k "cd /d %~dp0backend && python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload"

timeout /t 3 /nobreak > nul

echo [2/2] 启动前端 (端口 5173)...
start "前端服务" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo 启动完成！
echo 浏览器访问: http://localhost:5173
echo 教师账号: teacher / 123456
echo 学生账号: s01~s20 / 123456
echo.
pause
