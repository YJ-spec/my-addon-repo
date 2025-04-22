import logging
import time

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def main():
    logging.info("Add-on started")
    while True:
        logging.info(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(10)

if __name__ == "__main__":
    main()