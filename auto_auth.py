# python 3.11+
import os
import sys
import time
import platform
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

def resource_path(relative_path):
    """PyInstaller 번들 환경에서 리소스 경로 가져오기"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_chromedriver_path():
    """OS와 아키텍처에 맞는 ChromeDriver 경로 반환"""
    system = platform.system()
    machine = platform.machine().lower()

    print(f"감지된 시스템: {system}, 아키텍처: {machine}")

    if system == "Windows":
        if machine in ["arm64", "aarch64"]:
            driver_name = "chromedriver-win-arm64.exe"
        else:
            driver_name = "chromedriver-win64.exe"

    elif system == "Darwin":
        if machine in ["arm64", "aarch64"]:
            driver_name = "chromedriver-mac-arm64"
        else:
            driver_name = "chromedriver-mac-x64"

    elif system == "Linux":
        if machine in ["aarch64", "arm64"]:
            driver_name = "chromedriver-linux-arm64"
        else:
            driver_name = "chromedriver-linux64"

    else:
        raise Exception(f"지원하지 않는 OS입니다: {system}")

    driver_path = resource_path(os.path.join('drivers', driver_name))

    if not os.path.exists(driver_path):
        raise FileNotFoundError(
            f"ChromeDriver를 찾을 수 없습니다: {driver_path}\n"
            f"시스템: {system}, 아키텍처: {machine}\n"
            f"필요한 파일: {driver_name}"
        )

    if system in ["Darwin", "Linux"]:
        try:
            os.chmod(driver_path, 0o755)
            print(f"실행 권한 설정 완료: {driver_path}")
        except Exception as e:
            print(f"실행 권한 설정 실패 (무시 가능): {e}")

    print(f"ChromeDriver 경로: {driver_path}")
    return driver_path

def get_chrome_binary_path():
    """OS와 아키텍처에 맞는 Chrome for Testing 바이너리 경로 반환
    - 시스템 Chrome 자동 업데이트와 무관하게 동작
    - drivers/ 폴더에 번들된 Chrome for Testing 사용
    """
    system = platform.system()
    machine = platform.machine().lower()

    if system == "Windows":
        rel = os.path.join("chrome-win64", "chrome.exe")

    elif system == "Darwin":
        sub = "arm64" if machine in ["arm64", "aarch64"] else "x64"
        rel = os.path.join(
            f"chrome-mac-{sub}",
            "Google Chrome for Testing.app",
            "Contents", "MacOS", "Google Chrome for Testing"
        )

    elif system == "Linux":
        rel = os.path.join("chrome-linux64", "chrome")

    else:
        raise Exception(f"지원하지 않는 OS입니다: {system}")

    chrome_path = resource_path(os.path.join("drivers", rel))

    if not os.path.exists(chrome_path):
        raise FileNotFoundError(
            f"Chrome 바이너리를 찾을 수 없습니다: {chrome_path}\n"
            f"시스템: {system}, 아키텍처: {machine}\n"
            f"drivers/ 폴더에 Chrome for Testing 바이너리를 추가하세요."
        )

    if system in ["Darwin", "Linux"]:
        try:
            os.chmod(chrome_path, 0o755)
            print(f"실행 권한 설정 완료: {chrome_path}")
        except Exception as e:
            print(f"실행 권한 설정 실패 (무시 가능): {e}")

    print(f"Chrome 바이너리 경로: {chrome_path}")
    return chrome_path

def read_env():
    env_path = resource_path('.env')
    load_dotenv(env_path)

    env = {}
    env['ip_address'] = os.getenv('ip_address').strip('"')
    env['mac_address'] = os.getenv('mac_address').strip('"')
    env['user_id'] = os.getenv('user_id').strip('"')
    env['user_pw'] = os.getenv('user_pw', '').strip('"')
    env['headless'] = os.getenv('headless', 'false').strip('"').lower() == 'true'
    return env

def handle_alert(driver, timeout=3):
    """Alert 존재 여부 확인 및 처리"""
    try:
        WebDriverWait(driver, timeout).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"Alert 감지: {alert_text}")
        alert.accept()
        time.sleep(1)
        return True
    except TimeoutException:
        return False

def swing_login(env):
    url = f"https://121.67.201.63/gnauth/usr?SRCIP={env['ip_address']}&SMAC={env['mac_address']}"

    chromedriver_path = get_chromedriver_path()
    chrome_binary_path = get_chrome_binary_path()

    options = Options()
    options.binary_location = chrome_binary_path  # 시스템 Chrome 무시, 번들 Chrome 사용
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if env['headless']:
        options.add_argument('--headless=new')  # Chrome 112+ 권장 방식
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')    # Linux 환경 필수

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(5)

        handle_alert(driver)

        try:
            driver.find_element(By.XPATH, "/html/body/div[4]/div/div[3]/img[1]").click()
            time.sleep(1)
            handle_alert(driver)
        except Exception:
            pass

        try:
            handle_alert(driver)

            login_id = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="swingLoginId"]'))
            )
            login_id.send_keys(env['user_id'])
            time.sleep(0.3)

            driver.find_element(By.XPATH, '//*[@id="swingLoginPw"]').send_keys(env['user_pw'])
            time.sleep(0.3)

            driver.find_element(By.XPATH, '//*[@id="loginSwingBtn"]').click()
            time.sleep(3)

            handle_alert(driver)

        except UnexpectedAlertPresentException as e:
            print(f"예상치 못한 Alert 발생: {str(e)}")
            try:
                alert = driver.switch_to.alert
                print(f"Alert 텍스트: {alert.text}")
                alert.accept()
                time.sleep(1)
            except Exception as alert_error:
                print(f"Alert 처리 중 오류: {alert_error}")

        except TimeoutException:
            print("이미 인증된 상태이거나 로그인 폼을 찾을 수 없습니다")

        if env['headless']:
            from datetime import datetime
            page_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
            print(page_text)

    except Exception as e:
        print(f"오류 발생: {type(e).__name__} - {str(e)}")

    finally:
        driver.quit()

def main():
    while True:
        env = read_env()
        swing_login(env)
        print("완료. 5분 대기 후 재시작...")
        time.sleep(300)

if __name__ == "__main__":
    main()
