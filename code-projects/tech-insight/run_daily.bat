@echo off
REM TechInsight Windows 批处理 - 每日运行
cd /d "%~dp0"

echo ==========================================
echo TechInsight Daily Run %date% %time%
echo ==========================================

echo [1/3] Collecting...
python run.py collect

echo [2/3] Analyzing...
python run.py analyze --max-articles 300

echo [3/3] Stats:
python run.py stats

echo ==========================================
echo Done %date% %time%
echo ==========================================
pause
