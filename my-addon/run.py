import logging
import json
import paho.mqtt.client as mqtt
import requests
# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


# 讀取 HA 傳入的選項設定
with open("/data/options.json", "r") as f:
    options = json.load(f)

# 從環境變數取得 Long-Lived Token
TOPICS = options.get("mqtt_topics", "+/+/data,+/+/control").split(",")
MQTT_BROKER = options.get("mqtt_broker", "core-mosquitto")
MQTT_PORT = int(options.get("mqtt_port", 1883))
MQTT_USERNAME = options.get("mqtt_username", "")
MQTT_PASSWORD = options.get("mqtt_password", "")
LONG_TOKEN = options.get("HA_LONG_LIVED_TOKEN", "")

HEADERS = {
    "Authorization": f"Bearer {LONG_TOKEN}",
    "Content-Type": "application/json"
}

# HA 標準 API 的 base URL
BASE_URL = "http://homeassistant:8123/api/states"

# 當連線成功時執行
def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with result code {rc}")
    for topic in TOPICS:
        client.subscribe(topic)
        logging.info(f"Subscribed to topic: {topic}")

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logging.info(f"Received message on {msg.topic}: {payload}")

    # 嘗試從 HA API 取得所有 entity 狀態
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
