
@echo off
cd /d "%~dp0"
echo Updating GitHub repository...
git add "Weekly Expenditure.xlsx"
git commit -m "📊 Weekly data update"
git push
pause
