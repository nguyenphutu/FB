import sys
import time

import mariadb
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from crawlGroup import search_group_by_member


def insert_post(post):
    try:
        cur.execute("INSERT INTO posts (group_id, post_name, post_user_name, post_user_link, post_info, post_link,"
                    " post_like, post_share, post_comment) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (post["group_id"], post["post_name"], post["post_user_name"], post["post_user_link"],
                     post["post_info"], post["post_link"], post["post_like"], post["post_share"], post["post_comment"]))
    except mariadb.Error as e:
        print(f"warning insert_post to database: {e}")
    conn.commit()
    return cur.lastrowid


def search_post_by_url(url):
    cur.execute("SELECT * FROM posts WHERE post_link=?", (url,))
    return cur.rowcount


def search_post_all():
    cur.execute("SELECT * FROM posts")
    rows = cur.fetchall()
    return rows


def delete_post_by_id(post_id):
    cur.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    return


def update_post(post_id, post):
    query = f"UPDATE posts SET post_info = '{post['post_info']}' WHERE id = {post_id}"
    print(query)
    cur.execute(query)
    conn.commit()
    return


def login(email, password):
    try:
        driver.get("https://www.facebook.com")
        driver.maximize_window()

        # filling the form
        driver.find_element(By.NAME, 'email').send_keys(email)
        driver.find_element(By.NAME, 'pass').send_keys(password)

        # clicking on login button
        driver.find_element(By.NAME, 'login').click()
        time.sleep(5)

    except Exception as e:
        print("There was some error while logging in.")
        print(sys.exc_info()[0])
        exit()


def run_crawl_post_from_group(stop=20, delay=5):
    # Crawl post off group have >= 100000 member
    groups = search_group_by_member(cur, 100000)
    for group in groups:
        driver.get(group[3])
        loop = 0
        while loop < stop:
            time.sleep(delay)
            # feed element
            feed_element = driver.find_elements(By.XPATH, "//div[@role='feed']")[0]
            posts = feed_element.find_elements(By.XPATH, '*')
            for post in posts:
                try:
                    post_user_name = ""
                    post_user_link = ""
                    link_post = ""
                    links_post = post.find_elements(By.TAG_NAME, "a")
                    if len(links_post) == 0:
                        continue
                    # https://www.facebook.com/groups/{id-group}/permalink/{id-post}
                    for link in links_post:
                        href = link.get_attribute("href")
                        if 'user' in href:
                            post_user_link = href.split("?")[0]
                            link.get_attribute("aria-label")
                            if link.get_attribute("aria-label") is not None:
                                post_user_name = link.get_attribute("aria-label")
                        if 'posts' in href:
                            link_post = href.split("?")[0]
                        if '/photo/' in href:
                            l_temp = href.split("&")
                            if link_post == "":
                                id_post = l_temp[1].split(".")[1]
                                link_post = group + "/posts/" + str(id_post)
                    # Lấy số lượng like, share, coment
                    # Lấy element thích
                    post_num_like = 0
                    post_num_cmt = 0
                    post_num_share = 0
                    post_data = ""
                    try:
                        parent_post_content_element = post.find_element(By.XPATH,
                                                                        "*//div[@class='html-div xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd']")
                        post_content_element = parent_post_content_element.find_elements(By.XPATH, "*")[0].find_elements(
                            By.XPATH, "*")[2]
                        post_data = post_content_element.text
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
                            count_action_element = item_el_parent[0].find_elements(By.XPATH, "*")[
                                0].find_elements(By.XPATH,
                                                 "*")
                            count_like_element = count_action_element[0]
                            # Check có like
                            if len(count_like_element.find_elements(By.XPATH, "*")) > 0:
                                post_num_like = \
                                count_like_element.find_elements(By.XPATH, "*")[1].find_elements(By.XPATH,
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


                    import pdb;pdb.set_trace()
                    post_obj = {
                        "group_id": group[0],
                        "post_name": post_data,
                        "group_link": group[3],
                        "post_user_name": post_user_name,
                        "post_user_link": post_user_link,
                        "post_info": post_data,
                        "post_link": link_post,
                        "post_like": post_num_like,
                        "post_share": post_num_share,
                        "post_comment": post_num_cmt
                    }
                    insert_post(post_obj)
                except Exception as e:
                    print(e)
            # Scroll down to bottom
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight-200);")


if __name__ == '__main__':
    # Configure Selenium WebDriver
    # mobile_emulation = {
    #     "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
    #     "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, "
    #                  "like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
    #     "clientHints": {"platform": "Android", "mobile": True}}
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--log-level=1")
    # chrome_options.add_argument('headless')
    # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    driver.maximize_window()

    print(f'driver_setup called')

    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="Vnpt@123",
            host="localhost",
            port=3306,
            database="fb_db"
        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    cur = conn.cursor()

    login("trungtamcntt.dbn@gmail.com", "Vnpt@123")
    run_crawl_post_from_group()
    driver.close()
    conn.close()