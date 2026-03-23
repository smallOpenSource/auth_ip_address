# python 3.11+
import os
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException

def resource_path(relative_path):
    """PyInstaller 번들 환경에서 리소스 경로 가져오기"""
    try:
        # PyInstaller가 생성한 임시 폴더 경로
        base_path = sys._MEIPASS
    except Exception:
        # 일반 실행 환경
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def read_env():
    # .env 파일 경로를 PyInstaller 환경에 맞게 수정
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
        alert.accept()  # Alert 확인 버튼 클릭
        time.sleep(1)
        return True
    except TimeoutException:
        # Alert이 없으면 정상
        return False

def swing_login(env):
    url = f"https://121.67.201.63/gnauth/usr?SRCIP={env['ip_address']}&SMAC={env['mac_address']}"

    options = Options()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    if env['headless']:
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        time.sleep(5)
        
        # 초기 Alert 처리 (페이지 로드 직후)
        handle_alert(driver)
        
        # 버튼 클릭
        try:
            driver.find_element(By.XPATH, "/html/body/div[4]/div/div[3]/img[1]").click()
            time.sleep(1)
            # 버튼 클릭 후 Alert 처리
            handle_alert(driver)
        except Exception:
            pass  # 버튼이 없을 수도 있으므로 예외 무시

        try:
            # 로그인 폼 처리 전 Alert 재확인
            handle_alert(driver)
            
            # 아이디 입력 필드가 interactable할 때까지 최대 60초 대기
            login_id = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="swingLoginId"]'))
            )
            login_id.send_keys(env['user_id'])
            time.sleep(0.3)

            driver.find_element(By.XPATH, '//*[@id="swingLoginPw"]').send_keys(env['user_pw'])
            time.sleep(0.3)

            driver.find_element(By.XPATH, '//*[@id="loginSwingBtn"]').click()
            time.sleep(3)
            
            # 로그인 후 발생할 수 있는 Alert 처리
            handle_alert(driver)
            
        except UnexpectedAlertPresentException as e:
            # 예상치 못한 Alert 발생 시 처리
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
