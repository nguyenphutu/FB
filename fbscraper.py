from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
import sys
import time
import calendar
import xlsxwriter
from datetime import datetime


class CollectGroups(object):

    def __init__(self, depth=3, delay=3):
        self.depth = depth + 1
        self.delay = delay
        # browser instance
        chrome_option = Options()
        chrome_option.add_argument("--disable-notifications")
        self.browser = webdriver.Chrome(service=Service(executable_path=r"C:\Users\nguye\PycharmProjects\Selenium\chromedriver.exe"), options=chrome_option)

    def close_driver(self):
        self.browser.quit()
    def collect_groups(self, category, out_file):
        workbook = xlsxwriter.Workbook(out_file)
        worksheet = workbook.add_worksheet()
        # navigate to category link
        if category == "":
            self.browser.get(
                'https://www.facebook.com/groups/discover/')
        else:
            self.browser.get(
                'https://www.facebook.com/groups/categories/?category=' + category + '/')

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.delay)
        # Once the full page is loaded, we can start scraping
        groups = self.browser.find_elements(By.XPATH, "//div[@aria-label='Tham gia nhóm']")
        file_log = open("log.txt", "a+")
        log_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        len_groups = len(groups)
        log = log_time + ": " + str(len_groups) + " Groups \n"
        print(log)
        file_log.write(log)
        step = 1
        # header excel
        worksheet.write(0, 0, "STT")
        worksheet.write(0, 1, "name_group")
        worksheet.write(0, 2, "member_group")
        worksheet.write(0, 3, "link_group")
        for group in groups:
            try:
                div_info_group = group.find_elements(By.XPATH, '../../..')[0]
                info_group = div_info_group.text
                split_info = info_group.split("\n")
                name_group = split_info[0]
                member_group = split_info[1]
                link_group = div_info_group.find_elements(By.TAG_NAME, "a")[0].get_attribute('href')
                worksheet.write(step, 0, step)
                worksheet.write(step, 1, name_group)
                worksheet.write(step, 2, member_group)
                worksheet.write(step, 3, link_group)
                step+=1
            except Exception as e:
                print(e)
                worksheet.write(step, 0, step)
                worksheet.write(step, 1, e)
                worksheet.write(step, 2, group.find_elements(By.XPATH, '../../..')[0].get_attribute("outerHTML"))
        workbook.close()

    def collect_posts(self, group_id, out_file):
        workbook = xlsxwriter.Workbook(out_file)
        worksheet = workbook.add_worksheet()
        # navigate to group link
        if group_id == "":
            self.browser.get(
                'https://www.facebook.com')
        else:
            self.browser.get(
                'https://www.facebook.com/groups/' + group_id)

        # Scroll down depth-times and wait delay seconds to load
        # between scrolls
        for scroll in range(self.depth):
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.delay)
        # Once the full page is loaded, we can start scraping
        feed_element = self.browser.find_elements(By.XPATH, "//div[@role='feed']")[0]
        posts = feed_element.find_elements(By.XPATH, '*')[1:]
        file_log = open("log.txt", "a+")
        log_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')
        len_posts = len(posts)
        log = log_time + ": " + str(len_posts) + " Posts \n"
        print(log)
        file_log.write(log)
        step = 1
        # header excel
        worksheet.write(0, 0, "STT")
        worksheet.write(0, 1, "id_post")
        worksheet.write(0, 2, "photo_link")
        worksheet.write(0, 3, "post_data")
        worksheet.write(0, 4, "post_num_like")
        worksheet.write(0, 5, "post_num_cmt")
        worksheet.write(0, 6, "post_num_share")
        for post in posts:
            try:
                links_post = post.find_elements(By.TAG_NAME, "a")
                href_links = [e.get_attribute("href") for e in links_post]
                photo_link = []
                # https://www.facebook.com/groups/{id-grroup}/permalink/{id-post}
                link_post = ""
                for link in href_links:
                    if "/posts/" in link:
                        print("post: " + link)
                        id_post = link.split("?")[0].split("/")[-2]
                        link_post = "https://www.facebook.com/groups/" + str(group_id) + "/permalink/" + str(id_post)
                    if '/photo/' in link:
                        print("photo: " + link)
                        l_temp = link.split("&")
                        photo_link.append(l_temp[0])
                        if link_post == "":
                            print("Vào đây rồi" + l_temp[1])
                            id_post = l_temp[1].split(".")[1]
                            link_post = "https://www.facebook.com/groups/" + str(group_id) + "/permalink/" + str(id_post)
                # Lấy số lượng like, share, coment
                # Lấy element thích
                post_num_like = 0
                post_num_cmt = 0
                post_num_share = 0
                try:
                    like_element = post.find_elements(By.XPATH, "*//div[@aria-label='Thích']")[0]
                    # Lấy cha của element bao quát du lieu
                    parent_element = like_element.find_elements(By.XPATH, "../../../..")[0]
                    # Lấy các elemt con của cha, trong do có 2 div chua du lieu like, cmt, share và div thao tác like cmt share
                    item_el_parent = parent_element.find_elements(By.XPATH,"*")
                    # Check số lượng div trong element cha, nếu 1 thì k có lượt tương tác nào, nếu 2 thì có lượt tương tác
                    if len(item_el_parent) == 1:
                        post_num_cmt = 0
                        post_num_cmt = 0
                    elif len(item_el_parent) == 2:
                        # Lấy ra element chưa thông tin tương tác
                        count_action_element = item_el_parent[0].find_elements(By.XPATH,"*")[0].find_elements(By.XPATH,"*")
                        count_like_element = count_action_element[0]
                        # Check có like
                        if len(count_like_element.find_elements(By.XPATH, "*")) > 0:
                            post_num_like = count_like_element.find_elements(By.XPATH, "*")[1].find_elements(By.XPATH, "*//span[@aria-hidden='true']")[0].text
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
                step+=1
            except Exception as e:
                print(e)
                worksheet.write(step, 0, step)
                worksheet.write(step, 1, e)
                worksheet.write(step, 2, post.text)
        workbook.close()

    def collect_comments(self, post_link, out_file):
        workbook = xlsxwriter.Workbook(out_file)
        worksheet = workbook.add_worksheet()
        file_log = open("log.txt", "a+")
        log_time = datetime.now().strftime('%d-%m-%Y %H:%M:%S')

        # navigate to post_link
        self.browser.get(post_link)

        if "Bạn hiện không xem được nội dung này" in self.browser.page_source:
            file_log.write("Link post không tồn tại")
            return
        # between scrolls
        for scroll in range(self.depth):
            # Scroll down to bottom
            self.browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(self.delay)
        # Select all comment
        # import pdb;pdb.set_trace()
        # select_type_comment_element = self.browser.find_element(By.XPATH, "//div[@role='button']")
        # select_type_comment_element.click()
        # menu_element = self.browser.find_elements(By.XPATH, "//div[@role='menuitem']")
        # menu_element[-1].click()

        comments = self.browser.find_elements(By.XPATH, "//div[@role='article']")
        len_cmts = len(comments)
        log = log_time + ": " + str(len_cmts) + " Comments \n"
        print(log)
        file_log.write(log)
        step = 1
        # header excel
        worksheet.write(0, 0, "STT")
        worksheet.write(0, 1, "aria_label")
        worksheet.write(0, 2, "user_cmt")
        worksheet.write(0, 3, "cmt")
        worksheet.write(0, 4, "sticker")
        worksheet.write(0, 5, "media_links")
        for cmt in comments:
            try:
                sticker = ""
                media_links = ""
                aria_label = cmt.get_attribute("aria-label")
                # read_more_element = cmt.find_element(By.XPATH, "*//div[contains(text(), 'Xem thêm')]")
                # if read_more_element:
                #     read_more_element.click()
                div_cmt = cmt.find_elements(By.XPATH, '*')[1]
                div_cmt = div_cmt.find_elements(By.XPATH, '*')
                if len(div_cmt) == 2:
                    content_cmt = div_cmt[0].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH, '*')
                    user_cmt = content_cmt[0].text
                    text_cmt = content_cmt[len(content_cmt)-1].text
                else:
                    content_cmt = \
                    div_cmt[0].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH,
                                                                                                             '*')[
                        0].find_elements(By.XPATH, '*')
                    user_cmt = content_cmt[0].text
                    text_cmt = ""
                    try:
                        if div_cmt[1].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH, '*')[0].get_attribute("aria-label") is not None:
                            sticker = div_cmt[1].find_elements(By.XPATH, '*')[0].find_elements(By.XPATH, '*')[0].get_attribute("aria-label")
                        media_elements = div_cmt[1].find_elements(By.TAG_NAME, "a")
                        if len(media_elements) > 0:
                            media_links = [e.get_attribute("href").split("&_")[0] for e in media_elements]
                            media_links = ";".join(media_links)
                    except Exception as e:
                        print(e)
                        pass
                worksheet.write(step, 0, step)
                worksheet.write(step, 1, aria_label)
                worksheet.write(step, 2, user_cmt)
                worksheet.write(step, 3, text_cmt)
                worksheet.write(step, 4, sticker)
                worksheet.write(step, 5, media_links)
                step+=1
            except Exception as e:
                print(e)
                worksheet.write(step, 0, step)
                worksheet.write(step, 1, e)
                worksheet.write(step, 2, cmt.text)
        workbook.close()

    def like_post(self, post_link):
        self.browser.get(post_link)
        if "Bạn hiện không xem được nội dung này" in self.browser.page_source:
            print("Link post không tồn tại")
            return
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Thích']"))
        )
        like_element = self.browser.find_element(By.XPATH, "//div[@aria-label='Thích']")
        like_element.click()
    def cmt_post(self, post_link):
        self.browser.get(post_link)
        if "Bạn hiện không xem được nội dung này" in self.browser.page_source:
            print("Link post không tồn tại")
            return
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Viết bình luận']"))
        )
        cmt_element = self.browser.find_element(By.XPATH, "//div[@aria-label='Viết bình luận']")
        cmt_element.click()
        form_element = self.browser.find_element(By.XPATH, "//div[@aria-label='Viết câu trả lời...']")
        form_element.send_keys("Xin Chào!")
        form_element.send_keys(Keys.ENTER)
    def share_post(self, post_link):
        self.browser.get(post_link)
        if "Bạn hiện không xem được nội dung này" in self.browser.page_source:
            print("Link post không tồn tại")
            return
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Gửi nội dung này cho bạn bè hoặc đăng lên trang cá nhân của bạn.']"))
        )
        share_element = self.browser.find_element(By.XPATH, "//div[@aria-label='Gửi nội dung này cho bạn bè hoặc đăng lên trang cá nhân của bạn.']")
        share_element.click()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//div[@aria-label='Chia sẻ ngay']"))
        )
        share_form_element = self.browser.find_element(By.XPATH, "//div[@aria-label='Chia sẻ ngay']")
        share_form_element.click()
    def login(self, email, password):
        try:

            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            # filling the form
            self.browser.find_element(By.NAME, 'email').send_keys(email)
            self.browser.find_element(By.NAME,'pass').send_keys(password)

            # clicking on login button
            self.browser.find_element(By.NAME, 'login').click()
            time.sleep(5)

        except Exception as e:
            print("There was some error while logging in.")
            print(sys.exc_info()[0])
            exit()

    def main(self, group_id):
        self.login("0854659595", "FuuFuu1102@")
        out_file = group_id + ".xlsx"
        self.collect_posts(group_id, out_file)
        self.close_driver()




