import logging
import json
import paho.mqtt.client as mqtt
import requests
import os

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 從環境變數取得 Token（HA 會自動提供）
TOKEN = os.getenv("HASSIO_TOKEN") or os.getenv("SUPERVISOR_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}
# HA不支援requests 沒有LONG TOKEN的訪問
# Supervisor API 的 base URL
BASE_URL = "http://supervisor/core/api"

# 讀取 HA 傳入的選項設定
with open("/data/options.json", "r") as f:
    options = json.load(f)

TOPICS = options.get("mqtt_topics", "+/+/data,+/+/control").split(",")
MQTT_BROKER = options.get("mqtt_broker", "core-mosquitto")
MQTT_PORT = int(options.get("mqtt_port", 1883))
MQTT_USERNAME = options.get("mqtt_username", "")
MQTT_PASSWORD = options.get("mqtt_password", "")

# 當連線成功時執行
def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with result code {rc}")
    for topic in TOPICS:
        client.subscribe(topic)
        logging.info(f"Subscribed to topic: {topic}")

# 當收到訊息時執行
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logging.info(f"Received message on {msg.topic}: {payload}")
    logging.info(f"Using token: {TOKEN}")

    # ===== 取得裝置清單範例 =====
    try:
        entity_url = f"{BASE_URL}/states"
        response = requests.get(entity_url, headers=HEADERS, timeout=5)
        if response.status_code == 200:
            entities = response.json()
            logging.info("=== Entity List (sensor only) ===")
            for e in entities:
                if e["entity_id"].startswith("sensor."):
                    logging.info(e["entity_id"])
            logging.info("=== End of List ===")
        else:
            logging.warning(f"Failed to get entities: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error fetching entity list: {e}")

    # ===== 範例：根據 MQTT 指令開啟燈光 =====
    if payload == "turn_on_light":
        try:
            service_url = f"{BASE_URL}/services/light/turn_on"
            data = {"entity_id": "light.your_light_id"}  # 修改為你的實體ID
            response = requests.post(service_url, headers=HEADERS, json=data, timeout=5)
            if response.status_code == 200:
                logging.info("Light turned on successfully.")
            else:
                logging.warning(f"Failed to turn on light: {response.status_code} - {response.text}")
        except Exception as e:
            logging.error(f"Error turning on light: {e}")

def main():
    logging.info("Add-on started")

    client = mqtt.Client()

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_forever()  # 持續執行直到 Add-on 被 HA 關閉

if __name__ == "__main__":
    main()
