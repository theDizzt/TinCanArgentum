# TinCanArgentum
디스코드 봇 

1세대 2017년 5월 20일 ~ 2020년 11월 18일
2세대 2020년 11월 19일 ~ 2024년 1월 10일
3세대 2024년 1월 11일 ~ 

## 환경 설정

1. `.env.example`을 `.env`로 복사합니다.
2. `.env`의 각 항목에 실제 키와 토큰을 입력합니다.
3. 운영체제에 맞는 명령으로 의존성을 설치한 뒤 봇을 실행합니다.

Windows:

```powershell
py -3.10 -m pip install -r requirements-windows.txt
```

또는 `run.bat`을 실행하면 `.venv` 가상환경 생성과 패키지 설치를 자동으로 진행합니다.
KoNLPy를 사용하려면 Java 9 이상이 필요하며, `run.bat`은 설치된 최신 JDK를 자동으로 선택합니다.

Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y default-jre
python3.10 -m pip install -r requirements-ubuntu.txt
```

`.env`는 Git에서 제외되므로 커밋하지 않습니다.
