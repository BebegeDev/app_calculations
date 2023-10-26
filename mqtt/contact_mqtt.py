import configparser
import paho.mqtt.client as mqtt
import os
from sys import platform


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Подключение к MQTT СЕРВЕРУ прошло успешно")
        print("------------------------------------------------------------------")
        client.subscribe('#')
    else:
        print("Ошибка при подключении к MQTT СЕРВЕРУ")


def connection():
    config = configparser.ConfigParser()
    if platform == 'win32' or platform == 'win64':
        current_script_path = os.path.abspath(__file__)
        project_root_path = os.path.dirname(os.path.dirname(current_script_path)) + "\\utils\\setting.ini"
        config.read(project_root_path)

    elif platform == 'linux' or platform == 'linux2':
        config = configparser.ConfigParser()
        current_script_path = os.path.abspath(__file__)
        project_root_path = os.path.dirname(os.path.dirname(current_script_path)) + "/utils/setting.ini"
        config.read(project_root_path)
    
    user = config["MQTT"]["USER"]
    password = config["MQTT"]["PASSWORD"]
    host = config["MQTT"]["MQTT_HOST"]
    port = int(config["MQTT"]["MQTT_PORT"])
    interval = int(config["MQTT"]["MQTT_KEEPALIVE_INTERVAL"])
    mqttc = mqtt.Client()
    mqttc.username_pw_set(username=user, password=password)
    mqttc.on_connect = on_connect
    mqttc.connect(host, port, interval)
    mqttc.loop_start()
    return mqttc
