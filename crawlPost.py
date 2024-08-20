import sys
import time

import mariadb
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Configure Selenium WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--log-level=1")
# chrome_options.add_argument('headless')
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


def insert_group(group):
    try:
        cur.execute("INSERT INTO groups (group_name, group_info, group_link, group_member) VALUES (?, ?, ?, ?)",
                    (group["group_name"], group["group_info"], group["group_link"], group["group_member"]))
    except mariadb.Error as e:
        print(f"warning insert_card to database: {e}")
    conn.commit()
    return cur.lastrowid


def insert_link(url, name, type_note):
    try:
        cur.execute("INSERT INTO links (url, name, type_note) VALUES (?, ?, ?)", (url, name, type_note))
    except mariadb.Error as e:
        print(f"warning insert_link to database: {e}")
    conn.commit()
    return cur.lastrowid


def search_group_by_url(url):
    cur.execute("SELECT * FROM groups WHERE group_link=?", (url,))
    return cur.rowcount


def search_group_all():
    cur.execute("SELECT * FROM groups")
    rows = cur.fetchall()
    return rows


def delete_group_by_id(link_id):
    cur.execute("DELETE FROM groups WHERE id = ?", (link_id,))
    conn.commit()
    return


def update_group(group_id, group):
    query = f"UPDATE groups SET group_info = '{group['group_info']}' WHERE id = {group_id}"
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


def run_crawl_group_from_fb_search():
    search_list = ["tìm việc", "việc làm", "kiếm việc"]
    for search in search_list:
        driver.get(f"https://www.facebook.com/search/groups?q={search}")
        # search_element = driver.find_elements(By.XPATH, "*//input[@type='search']")[0]
        # search_element.clear()
        # search_element.send_keys(search)
        # search_element.send_keys(Keys.ENTER)
        time.sleep(5)
        loop = 0
        while loop < 20:
            time.sleep(3)
            feed_element = driver.find_elements(By.XPATH, "//div[@role='feed']")[0]
            articles = feed_element.find_elements(By.XPATH, "//div[@role='article']")
            for article in articles:
                try:
                    link = article.find_element(By.XPATH, "*//a[@role='presentation']")
                    href = link.get_attribute("href")
                    text = link.text
                    info_div = link.find_element(By.XPATH, "../../../..")
                    group_info = info_div.find_elements(By.XPATH, "div")[-1].text
                    group_member = ""
                    try:
                        group_member = group_info.split("·")[1].strip()
                    except Exception as e:
                        print(e)
                    group = {
                        "group_name": text,
                        "group_info": group_info,
                        "group_link": href,
                        "group_member": group_member
                    }
                    # Check link not have in database
                    search_link = search_group_by_url(href)
                    if search_link == 0:
                        insert_group(group)
                except Exception as e:
                    print(e)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            loop += 1


login("trungtamcntt.dbn@gmail.com", "Vnpt@123")
run_crawl_group_from_fb_search()
driver.close()
conn.close()
