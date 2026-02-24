# Auto IP/MAC Authentication

Selenium 기반 웹 인증 자동화 스크립트입니다. 지정된 IP 및 MAC 주소에 대한 인증을 자동으로 수행합니다.

## 디렉터리 및 파일 구조
- `auto_auth.py`: `drivers/` 경로에 포함된 로컬 ChromeDriver 및 Chrome 바이너리를 사용하는 자동 인증 스크립트.
- `new_auto_auth.py`: `webdriver_manager` 패키지를 통해 시스템에 설치된 Chrome 버전에 맞는 드라이버를 자동 다운로드하여 사용하는 스크립트.
- `.env`: 계정 정보 및 실행 옵션이 포함된 설정 파일.
- `requirements.txt`: 스크립트 실행에 필요한 파이썬 패키지 목록.

## 실행 환경
- Python 3.11 이상

## 설치

### 패키지 의존성 설치
```bash
pip install -r requirements.txt
```

### 드라이버 및 브라우저 (auto_auth.py 사용 시)
`auto_auth.py`를 사용할 경우 프로젝트 루트의 `drivers/` 폴더 내에 운영체제에 맞는 ChromeDriver와 Chrome for Testing 바이너리가 위치해야 합니다.

## 환경 변수 설정
`.env` 파일에 아래와 같이 인증 정보 및 실행 옵션을 입력합니다.
```env
ip_address="192.168.x.x"
mac_address="XX:XX:XX:XX:XX:XX"
user_id="인증_아이디"
user_pw="인증_비밀번호"
headless="true" # UI 없이 백그라운드에서 실행하려면 "true", 화면을 확인하려면 "false"
```

## 실행 방법

번들된 로컬 드라이버 사용:
```bash
python auto_auth.py
```

`webdriver_manager` 자동 드라이버 사용:
```bash
python new_auto_auth.py
```

스크립트는 1회 인증 완료 후 5분 단위로 대기 및 재시작하여 인증 상태를 유지합니다.

## 라이선스
MIT License
