# TinCanArgentum
디스코드 봇 

1세대 2017년 5월 20일 ~ 2020년 11월 18일
2세대 2020년 11월 19일 ~ 2024년 1월 10일
3세대 2024년 1월 11일 ~ 

## 환경 설정

1. `.env.example`을 `.env`로 복사합니다.
2. `.env`의 각 항목에 실제 키와 토큰을 입력합니다.
3. `config/admin.example.json`을 `config/admin.json`으로 복사하고 관리자 정보를 입력합니다. 키는 `UID` 뒤에 Discord 사용자 ID를 붙이며, `id`와 `pw`는 앞자리 0이 유지되도록 문자열로 입력합니다. 관리자가 없다면 `{}`로 설정합니다.
4. 운영체제에 맞는 명령으로 의존성을 설치한 뒤 봇을 실행합니다.

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

도움말 데이터는 `config/help.json`, 관리자 로그인 정보는 `config/admin.json`에서 읽습니다.
`config/admin.json`도 Git에서 제외됩니다. 설정 변경은 해당 Cog를 다시 로드하거나 봇을 재시작하면 적용됩니다.

## 다국어 데이터 검증

locale 파일을 수정한 뒤 다음 명령으로 JSON 키, 명령어 ID, 자리표시자 및 Discord 명령어 제한을 검사합니다.

```bash
python scripts/validate_locales.py
```
