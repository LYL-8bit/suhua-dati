@echo off
echo 重置假数据...
cd /d %~dp0backend
python seed.py
echo 完成！
pause
