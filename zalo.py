from flask import Flask, redirect
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

def launchBrowser():
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    browser.get("https://chat.zalo.me/")
    return browser


def openZaloNumber():
    browser = None  # Khởi tạo browser là None
    try:
        path = r"d:\LUANVAN\chrome\chromedriver-win64\chromedriver-win64\chromedriver.exe"
        # path = r"http://127.0.0.1:5000/reportbreak"
        ser = Service(path)

        # Configure Chrome options
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")

        # Initialize the browser
        browser = webdriver.Chrome(service=ser, options=chrome_options)

        # Open Zalo web
        browser.get("https://chat.zalo.me/")

        # Wait for the add friend button to be clickable
        add_friend_class = 'fa-outline-add-new-contact-2'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, add_friend_class))).click()
        
        # Input phone number
        phone_input_class = 'phone-i-input'
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.CLASS_NAME, phone_input_class))).send_keys("0939878333")
        
        # Click search button
        search_button_class = 'z--btn--v2.btn-primary'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, search_button_class))).click()
        
        # Click message button
        message_button_class = 'z--btn--v2.btn-secondary'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, message_button_class))).click()
        
        # Write and send message
        write_text_id = 'input_line_0'
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, write_text_id))).send_keys("hello")
        
        send_button_class = 'fa-Sent-msg_24_Line'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, send_button_class))).click()
         
        # Wait for a few seconds to ensure the message is sent
        time.sleep(10)

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        if browser:
            browser.quit()

# Execute the function
# openZalo()

def openZaloGroup():
    try:
        ser = Service(ChromeDriverManager().install())  # Sử dụng webdriver_manager để xử lý cài đặt driver

        # Cấu hình tùy chọn Chrome
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")

        # Khởi tạo trình duyệt
        browser = webdriver.Chrome(service=ser, options=chrome_options)

        # Mở trang Zalo web
        # browser.get("https://zalo.me/g/wukxxy356")
        # Open Zalo web
        browser.get("https://chat.zalo.me/")

        # Nhap vao thanh search
        add_group_id = 'contact-search-input'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, add_group_id))).click()
        
        # Nhập ten group
        group_input_id = 'contact-search-input'
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, group_input_id))).send_keys("test")
        
        
        # Nhấp icon group
        search_button_id = 'group-item-g2442067688229168752'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.ID, search_button_id))).click()
        
        # Viết và gửi tin nhắn
        write_text_id = 'input_line_0'
        WebDriverWait(browser, 30).until(EC.presence_of_element_located((By.ID, write_text_id))).send_keys("hello")
        
        send_button_class = 'fa-Sent-msg_24_Line'
        WebDriverWait(browser, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, send_button_class))).click()
         
        # Chờ vài giây để đảm bảo tin nhắn được gửi
        time.sleep(30)

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")
    finally:
        if browser:
            browser.quit()

@app.route('/reportbreak', methods=['GET', 'POST'])
def report_break():
    # Thực hiện các thao tác tự động hóa trước khi redirect
    openZaloGroup()  # Gọi hàm openZalo để thực hiện tự động hóa Zalo
    return redirect("https://chat.zalo.me/")

if __name__ == '__main__':
    app.run(debug=True)
    
