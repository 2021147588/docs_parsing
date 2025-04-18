# How to RUN

## 1. Frontend 실행
```bash
cd fe
npm install         # 필요한 프론트엔드 패키지 설치
npm run dev         # 개발 서버 실행 (기본 포트: http://localhost:5173)
```

## 2. Backend 실행
```bash
cd be               # 백엔드 디렉토리로 이동
pip install -r requirements.txt  # 외부 라이브러리 설치
pip install -e .                 # 현재 로컬 패키지를 개발 모드로 설치
python app.py                   # 서버 실행 (기본 포트: http://localhost:9000)
```
이제 http://localhost:9000 에서 테스트할 수 있습니다.
