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
    def __init__(self, depth=3, delay=5):
        self.depth = depth + 1
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

            self.driver.get("https://www.facebook.com")
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
        self.group_link_list = [f'https://www.facebook.com/groups/{group_id}' for group_id in group_id_list]
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
        worksheet.write(0, 1, "id_post")
        worksheet.write(0, 2, "photo_link")
        worksheet.write(0, 3, "post_data")
        worksheet.write(0, 4, "post_num_like")
        worksheet.write(0, 5, "post_num_cmt")
        worksheet.write(0, 6, "post_num_share")
        post_ids = []
        for scroll in range(self.depth):
            time.sleep(self.delay)
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-200);")
            time.sleep(self.delay)
            log_scroll = ("Scroll: " + str(scroll))
            print(log_scroll)
            # Lay feed element
            feed_element = self.driver.find_elements(By.XPATH, "//div[@role='feed']")[0]
            posts = feed_element.find_elements(By.XPATH, '*')
            len_post = len(posts)
            # trong dom div đầu tiên và 3 div cuối cùng không phải chưa post
            if scroll == 0:
                posts = posts[1:len_post-3]
            file_log = open("log.txt", "a+")
            log_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
            log = log_time + ": " + str(len_post - 4) + " Posts \n"
            log_ram = psutil.virtual_memory().percent
            log_cpu = psutil.cpu_percent()
            log = log + "RAM: " + str(log_ram) + "\n"
            log = log + "CPU: " + str(log_cpu) + "\n"
            print(log)
            file_log.write(log_scroll + "\n")
            file_log.write(log)
            for post in posts:
                try:
                    links_post = post.find_elements(By.TAG_NAME, "a")
                    href_links = [e.get_attribute("href") for e in links_post]
                    photo_link = []
                    # https://www.facebook.com/groups/{id-group}/permalink/{id-post}
                    link_post = ""
                    id_post = None
                    for link in href_links:
                        if "/posts/" in link:
                            print("post: " + link)
                            id_post = link.split("?")[0].split("/")[-2]
                            post_ids.append(id_post)
                            link_post = group_link + "/permalink/" + str(id_post)
                        if '/photo/' in link:
                            print("photo: " + link)
                            l_temp = link.split("&")
                            photo_link.append(l_temp[0])
                            if link_post == "":
                                print("Vào đây rồi" + l_temp[1])
                                id_post = l_temp[1].split(".")[1]
                                post_ids.append(id_post)
                                link_post = group_link + "/permalink/" + str(id_post)
                    # Lấy số lượng like, share, coment
                    # Lấy element thích
                    post_num_like = 0
                    post_num_cmt = 0
                    post_num_share = 0
                    if id_post is not None and id_post not in post_ids:
                        try:
                            like_element = post.find_elements(By.XPATH, "*//div[@aria-label='Thích']")[0]
                            # Lấy cha của element bao quát du lieu
                            parent_element = like_element.find_elements(By.XPATH, "../../../..")[0]
                            # Lấy các elemt con của cha, trong do có 2 div chua du lieu like, cmt, share và div thao tác like cmt share
                            item_el_parent = parent_element.find_elements(By.XPATH, "*")
                            # Check số lượng div trong element cha, nếu 1 thì k có lượt tương tác nào, nếu 2 thì có lượt tương tác
                            if len(item_el_parent) == 1:
                                post_num_cmt = 0
                                post_num_cmt = 0
                            elif len(item_el_parent) == 2:
                                # Lấy ra element chưa thông tin tương tác
                                count_action_element = item_el_parent[0].find_elements(By.XPATH, "*")[0].find_elements(By.XPATH,
                                                                                                                       "*")
                                count_like_element = count_action_element[0]
                                # Check có like
                                if len(count_like_element.find_elements(By.XPATH, "*")) > 0:
                                    post_num_like = count_like_element.find_elements(By.XPATH, "*")[1].find_elements(By.XPATH,
                                                                                                                     "*//span[@aria-hidden='true']")[
                                        0].text
                                cmt_share_element = count_action_element[1]
                                cmt_share_element = cmt_share_element.find_elements(By.XPATH, "*")
                                # Check có cmt, share
                                len_item = len(cmt_share_element)
                                if len_item > 0:
                                    if len_item == 2:
                                        post_num_cmt = cmt_share_element[1].text
                                    if len_item == 3:
                                        post_num_cmt = cmt_share_element[1].text
                                        post_num_share = cmt_share_element[2].text
                        except Exception as e:
                            print(e)

                    # Xử lý xem thêm nội dung post nếu nội dung quá dài
                    # try:
                    #     xemthem_el = post.find_elements(By.XPATH, "*//div[contains(text(), 'Xem thêm')]")
                    #     if len(xemthem_el) > 0:
                    #         self.browser.execute_script("arguments[0].scrollIntoView();", xemthem_el[0])
                    #         xemthem_el[0].click()
                    # except Exception as e:
                    #     print(e)
                    post_data = post.text
                    worksheet.write(step, 0, step)
                    worksheet.write(step, 1, link_post)
                    worksheet.write(step, 2, ";".join(photo_link))
                    worksheet.write(step, 3, post_data)
                    worksheet.write(step, 4, post_num_like)
                    worksheet.write(step, 5, post_num_cmt)
                    worksheet.write(step, 6, post_num_share)
                    step += 1
                except Exception as e:
                    print(e)
                    worksheet.write(step, 0, step)
                    worksheet.write(step, 1, e)
                    worksheet.write(step, 2, post.text)

            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight-200);")
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