from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


import time
import os

mobile_emulation = {
   "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
   "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
   "clientHints": {"platform": "Android", "mobile": True} }
chrome_options = Options()
chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)


try:
    # Mở trang mbasic.facebook.com
    driver.get('https://facebook.com')

    # Tìm và điền vào email
    email_input = driver.find_element(By.NAME, 'email')
    email_input.send_keys('trungtamcntt.dbn@gmail.com')  # Điền email của bạn vào

    # Tìm và điền vào password
    password_input = driver.find_element(By.NAME, 'pass')
    password_input.send_keys('Vnpt@123')  # Điền mật khẩu của bạn vào

    # Gửi form để đăng nhập
    password_input.send_keys(Keys.RETURN)

    # Chờ một chút để trang tải xong
    time.sleep(3)

    # Kiểm tra xem đã đăng nhập thành công chưa
    if "login_attempt" in driver.current_url:
        print("Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.")
    else:
        print("Đăng nhập thành công!")

except Exception as e:
    print(e)

driver.get("https://fb.watch/udfpfcB8O7/")
src = driver.find_elements(By.TAG_NAME, "video")[0].get_attribute("src")