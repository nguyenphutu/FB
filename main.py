import fbAction
import concurrent.futures
import threading
import os
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, wait


date_end = "08/07/2024"
C = fbscraper.CollectGroups(depth=2)
# while datetime.now().strftime("%d/%m/%Y") != date_end:
#     C.collect_groups("GYSJ")
#     time.sleep(900)

# pool = concurrent.futures.ThreadPoolExecutor(max_workers=5)
#
# pool.submit(C.collect_posts("anngonmoingayso1", "anngonmoingayso1.xlsx"))
# pool.submit(C.collect_posts("1444402712557235", "1444402712557235.xlsx"))
# pool.submit(C.collect_posts("sapa.tattantat", "sapa.tattantat.xlsx"))
# pool.submit(C.collect_posts("985448989912919", "985448989912919.xlsx"))
# pool.submit(C.collect_posts("174764463261090", "174764463261090.xlsx"))
#
# pool.shutdown(wait=True)

id_groups = ["anngonmoingayso1", "1444402712557235", "sapa.tattantat", "1444402712557235", "1444402712557235"]

print(f'Starting scraping with multiprocessing ...')
start = time.time()
processList = []

with ProcessPoolExecutor() as executor:
    processList = [executor.submit(C.main, group_id=group_id) for group_id in id_groups]
wait(processList)
end = time.time()
print(f'Ending scraping with multithreading ...')
print(f'Time for scraping with multithreading: {round(end-start,2)} seconds')
#
# t1 = threading.Thread(target=C.collect_posts("anngonmoingayso1", "anngonmoingayso1.xlsx"), name='t1')
# t2 = threading.Thread(target=C.collect_posts("1444402712557235", "1444402712557235.xlsx"), name='t2')
# t3 = threading.Thread(target=C.collect_posts("anngonmoingayso1", "anngonmoingayso1.xlsx"), name='t3')
# t4 = threading.Thread(target=C.collect_posts("1444402712557235", "1444402712557235.xlsx"), name='t4')
# t5 = threading.Thread(target=C.collect_posts("1444402712557235", "1444402712557235.xlsx"), name='t5')
#
# t1.start()
# t2.start()
# t3.start()
# t4.start()
# t5.start()
#
# t1.join()
# t2.join()
# t3.join()
# t4.join()
# t5.join()
