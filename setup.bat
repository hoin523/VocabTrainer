@echo off
echo [1/3] 가상환경 생성...
python -m venv venv

echo [2/3] 가상환경 활성화 및 라이브러리 설치...
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] 프로그램 실행...
python main.py

pause
