git fetch --all
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD') do set branch=%%b
git reset --hard origin/%branch%
uv pip install -r requirements.txt
call .venv\Scripts\activate.bat
python backend/main.py
pause