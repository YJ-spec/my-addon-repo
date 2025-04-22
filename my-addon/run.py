import logging
import json
import paho.mqtt.client as mqtt

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

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
    logging.info(f"Received message on {msg.topic}: {msg.payload.decode()}")

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
