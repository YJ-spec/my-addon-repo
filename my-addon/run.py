import time
import logging
import paho.mqtt.client as mqtt

# 設定日誌格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# 寫死 MQTT 設定
TOPICS = ["+/+/data", "+/+/control"]
MQTT_BROKER = "core-mosquitto"
MQTT_PORT = 1883
MQTT_USERNAME = "test"
MQTT_PASSWORD = "test"

def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with result code {rc}")
    for topic in TOPICS:
        client.subscribe(topic)
        logging.info(f"Subscribed to topic: {topic}")

def on_message(client, userdata, msg):
    logging.info(f"Received message on {msg.topic}: {msg.payload.decode()}")

def main():
    logging.info("Add-on started")

    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()

    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        client.loop_stop()

if __name__ == "__main__":
    main()
