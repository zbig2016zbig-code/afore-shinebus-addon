#!/usr/bin/env python3
import socket
import time
import yaml
import paho.mqtt.client as mqtt

def crc16(data: bytes):
    crc = 0xFFFF
    for pos in data:
        crc ^= pos
        for _ in range(8):
            if (crc & 1) != 0:
                crc >>= 1
                crc ^= 0xA001
            else:
                crc >>= 1
    return crc.to_bytes(2, byteorder='little')

def build_request():
    frame = bytes([0xA5, 0x15, 0x00, 0x10, 0x00, 0x00])
    frame += crc16(frame)
    return frame

def parse_response(data):
    if len(data) < 50:
        return None

    pv1_voltage = int.from_bytes(data[10:12], 'big') / 10
    pv1_current = int.from_bytes(data[12:14], 'big') / 10
    pv2_voltage = int.from_bytes(data[14:16], 'big') / 10
    pv2_current = int.from_bytes(data[16:18], 'big') / 10

    ac_power = int.from_bytes(data[18:20], 'big')
    grid_voltage = int.from_bytes(data[20:22], 'big') / 10
    grid_freq = int.from_bytes(data[22:24], 'big') / 100

    daily_yield = int.from_bytes(data[24:26], 'big') / 100
    total_yield = int.from_bytes(data[26:30], 'big') / 10

    return {
        "pv1_voltage": pv1_voltage,
        "pv1_current": pv1_current,
        "pv2_voltage": pv2_voltage,
        "pv2_current": pv2_current,
        "ac_power": ac_power,
        "grid_voltage": grid_voltage,
        "grid_frequency": grid_freq,
        "daily_yield": daily_yield,
        "total_yield": total_yield
    }

def main():
    with open("config.yaml", "r") as f:
        cfg = yaml.safe_load(f)

    mqttc = mqtt.Client()
    mqttc.username_pw_set(cfg["mqtt"]["username"], cfg["mqtt"]["password"])
    mqttc.connect(cfg["mqtt"]["host"], cfg["mqtt"]["port"], 60)
    mqttc.loop_start()

    topic = cfg["mqtt"]["topic"]
    host = cfg["inverter"]["host"]
    port = cfg["inverter"]["port"]
    interval = cfg["inverter"]["interval"]

    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((host, port))

            req = build_request()
            s.send(req)
            data = s.recv(200)
            s.close()

            parsed = parse_response(data)
            if parsed:
                for key, value in parsed.items():
                    mqttc.publish(f"{topic}/{key}", value, retain=True)

        except Exception as e:
            print("Error:", e)

        time.sleep(interval)

if __name__ == "__main__":
    main()
