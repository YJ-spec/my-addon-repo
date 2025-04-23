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
BASE_URL = "http://homeassistant:8123/api"

# 設定單位條件
unit_conditions = {
    "ct": "°C",
    "t": "°C",
    "ch": "%",
    "h": "%",
    "p1": "µg/m³",
    "p25": "µg/m³",
    "p10": "µg/m³",
    "v": "ppm",
    "c": "ppm",
    "ec": "ppm",
    "rset": "rpm",
    "rpm": "rpm"
}

# 當連線成功時執行
def on_connect(client, userdata, flags, rc):
    logging.info(f"Connected to MQTT broker with result code {rc}")
    for topic in TOPICS:
        client.subscribe(topic)
        logging.info(f"Subscribed to topic: {topic}")

def generate_mqtt_discovery_config(device_name, device_mac, sensor_type, sensor_name):
    """ 根據 MQTT 訊息生成 Home Assistant MQTT Discovery 設定 """
    # 生成 topic
    topic = f"{device_name}/{device_mac}/data"

    # 基本 config
    config = {
        "name": sensor_name,
        "state_topic": topic,
        "expire_after": 300,
        "value_template": f"{{{{ value_json.{sensor_type}.{sensor_name} }}}}",
        "unique_id": f"{device_name}_{device_mac}_{sensor_name}",
        "state_class": "measurement",
        "force_update": True,
        "device": {
            "identifiers": f"{device_name}_{device_mac}",
            "name": f"{device_name}_{device_mac}",
            "model": device_name,
            "manufacturer": "CurieJet"
        }
    }

    # 如果有單位才加上
    if sensor_name in unit_conditions:
        config["unit_of_measurement"] = unit_conditions[sensor_name]

    return config


		
# 處理 MQTT 訊息並產生 Discovery 設定
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    logging.info(f"Received message on {msg.topic}: {payload}")

    try:
        # 提取 deviceName 和 deviceMac
        topic_parts = msg.topic.split('/')
        if len(topic_parts) < 3:
            logging.warning(f"Invalid topic format: {msg.topic}")
            return
        device_name = topic_parts[0]
        device_mac = topic_parts[1]
				
        message_json = json.loads(payload)
        if not device_name or not device_mac:
            logging.warning(f"Missing deviceName or deviceMac in message: {payload}")
            return
        
        # 生成對應的 MQTT Discovery 配置
        discovery_configs = []
        
        # 處理 data 欄位的感測器
        data_sensors = message_json.get("data", {})
        for sensor, value in data_sensors.items():
            config = generate_mqtt_discovery_config(device_name, device_mac, "data", sensor)
            discovery_configs.append(config)

        # 處理 data1 欄位的感測器
        data1_sensors = message_json.get("data1", {})
        for sensor, value in data1_sensors.items():
            config = generate_mqtt_discovery_config(device_name, device_mac, "data1", sensor)
            discovery_configs.append(config)

        # 推送 MQTT Discovery 配置到 HA
        for config in discovery_configs:
            discovery_topic = f"homeassistant/sensor/{device_name}_{device_mac}_{config['name']}/config"
            mqtt_payload = json.dumps(config, indent=2)
            client.publish(discovery_topic, mqtt_payload, retain=True)
            logging.info(f"Published discovery config to {discovery_topic}")

    except json.JSONDecodeError:
        logging.error(f"Failed to decode payload: {payload}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

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
