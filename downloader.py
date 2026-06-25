from concurrent.futures import ThreadPoolExecutor
from functools import partial
import threading
import requests
import time
import db
import os


def download_icon(icon,total,start_time,lock,download_count,failed_count):
    icon_id = icon[0]
    image_url = icon[2]

    attempt = 0
    time.sleep(0.5)
    while attempt < 3:
        try:
            response = requests.get(image_url)
            response.raise_for_status()

            local_path = f"images/{icon_id}.png"
            with open(local_path,"wb") as f:                
                f.write(response.content)
                db.update_icon(local_path,icon_id)
                print(f"Downloaded {icon_id}")
                with lock:
                    download_count[0] += 1
                    Completed = download_count[0] + failed_count[0]
                    Elapsed = time.time() - start_time
                    Average = Elapsed / Completed
                    Remaining = total - Completed
                    ETA = Average * Remaining
                    minutes = int(ETA // 60)
                    seconds = int(ETA % 60)
                    print(f"Successfull Download {download_count[0]}")
                    print(f"Completed : {Completed} , Elapsed : {Elapsed} , Average : {Average} , Remaining : {Remaining} , ETA : {minutes}m {seconds}s")
                    break
        except Exception as e:
            attempt = attempt + 1
            time.sleep(2)
            print(f"Retrying downloading {icon_id}: {e}")
    if attempt == 3:
        db.mark_failed(icon_id)
        print(f"image failed to download {icon_id}")
        with lock:
            failed_count[0] += 1
            print(f"Failed to downlaod {failed_count[0]}")



def download_single_icon():
    un_download = db.get_undownloaded_icons()
    print(f"Total undownloaded: {len(un_download)}")
    os.makedirs('images/',exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        total = len(un_download)
        start_time = time.time()
        lock = threading.Lock()
        downloaded_count = [0]
        failed_count = [0]
        worker = partial(download_icon, total=total, start_time=start_time, lock=lock, download_count=downloaded_count, failed_count=failed_count)

        executor.map(worker,un_download)
    
download_single_icon()

# import sqlite3
# conn = sqlite3.connect('/Users/touheed/Desktop/flaticon/scraper.db')
# conn.execute('UPDATE ICONS SET DOWNLOADED = NULL WHERE ID < 20')
# conn.commit()
# conn.close()
# print('Done')