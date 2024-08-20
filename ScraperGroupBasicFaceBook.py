from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait
import sys
import time
import calendar
import xlsxwriter
from datetime import datetime
import psutil

class ScrapeData():
    def __init__(self, depth=5, delay=5):
        self.depth = depth
        self.delay = delay

    def driver_setup(self):
        chrome_options = webdriver.ChromeOptions()
        # chrome_options.add_argument('--no-sandbox')
        # chrome_options.add_argument('--headless')
        # chrome_options.add_argument('--disable-gpu')
        # chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-notifications")
        # self.driver = webdriver.Chrome(options=chrome_options)
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print(f'driver_setup called')

    def close_driver(self):
        self.driver.quit()

    def login(self, email, password):
        try:
            self.driver.get("https://mbasic.facebook.com/")
            self.driver.maximize_window()

            # filling the form
            self.driver.find_element(By.NAME, 'email').send_keys(email)
            self.driver.find_element(By.NAME,'pass').send_keys(password)

            # clicking on login button
            self.driver.find_element(By.NAME, 'login').click()
            time.sleep(5)

        except Exception as e:
            print("There was some error while logging in.")
            print(sys.exc_info()[0])
            exit()
    def get_group_links(self, group_id_list):
        self.group_link_list = [f'https://mbasic.facebook.com/groups/{group_id}' for group_id in group_id_list]
        print(f'get_group_links called ')
        return self.group_link_list
    def get_post_data(self, group_link):
        # Tao file excel luu data
        out_file = group_link.split("/")[-1] + ".xlsx"
        workbook = xlsxwriter.Workbook(out_file)
        worksheet = workbook.add_worksheet()
        # mo link fb group
        self.driver.get(group_link)
        self.driver.implicitly_wait(2)
        # Scroll luong post muon thực hiện lấy data
        step = 1
        # header excel
        worksheet.write(0, 0, "STT")
        worksheet.write(0, 1, "url_post")
        worksheet.write(0, 2, "user_post")
        worksheet.write(0, 3, "user_id")
        worksheet.write(0, 4, "content_post")
        worksheet.write(0, 5, "media")
        worksheet.write(0, 6, "date_post")
        worksheet.write(0, 7, "data_action")
        try:
            for scroll in range(self.depth):
                time.sleep(self.delay)
                feed_element = self.driver.find_element(By.TAG_NAME, "section")
                articles = feed_element.find_elements(By.TAG_NAME, "article")
                # Loop all articles to get data
                try:
                    for article in articles:
                        header_user = article.find_element(By.TAG_NAME, "header").find_elements(By.TAG_NAME, "a")[0]
                        user_post = header_user.text
                        user_id = header_user.get_attribute("href").split("&")[0].split("=")[-1]
                        content_post = article.find_element(By.CLASS_NAME, "dm").text
                        imgs = article.find_elements(By.TAG_NAME, "img")
                        media = []
                        if len(imgs) > 0:
                            for img in imgs:
                                media.append(img.get_attribute("src"))
                        footer = article.find_element(By.TAG_NAME, "footer")
                        date_post = footer.find_element(By.TAG_NAME, "abbr").text
                        data_action = footer.find_elements(By.TAG_NAME, "div")[1].text
                        post_url = footer.find_element(By.LINK_TEXT, "Toàn bộ tin").get_attribute("href").split("?")[0]

                        # write data to excel
                        worksheet.write(step, 0, step)
                        worksheet.write(step, 1, post_url)
                        worksheet.write(step, 2, user_post)
                        worksheet.write(step, 3, user_id)
                        worksheet.write(step, 4, content_post)
                        worksheet.write(step, 5, ";".join(media))
                        worksheet.write(step, 6, date_post)
                        worksheet.write(step, 7, data_action)
                except Exception as e:
                    print(e)
                self.driver.find_element(By.LINK_TEXT, "Xem thêm bài viết").click()
        except Exception as e:
            print(e)

        workbook.close()
        print(f'get_post_data called for {group_link} ')

    def main(self, group_list):
        self.driver_setup()
        self.login("0854659595", "FuuFuu1102@")
        group_link_list = self.get_group_links(group_list)
        for group_link in group_link_list:
            self.get_post_data(group_link)
        self.close_driver()

if __name__ == '__main__':
    A = ScrapeData()
    group_list = ["anngonmoingayso1"]
    A.main(group_list)