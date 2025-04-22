import time

def main():
    print(f"Add-on started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
    while True:
        print(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        time.sleep(10)

if __name__ == "__main__":
    main()
