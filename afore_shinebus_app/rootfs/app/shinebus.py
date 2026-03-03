import socket
import time
import json
import paho.mqtt.client as mqtt
import argparse


def read_inverter(host, port):
    """Read ShineBus data from Afore inverter."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((host, port))

            # ShineBus request frame
            request = bytes.fromhex("680200000000000000000000000000000000000000000000000000000000000016")
            s.sendall(request)

            data = s.recv(1024)
            return data

    except Exception as e:
        print(f"Error reading inverter: {e}")
        return None


def parse_data(data):
    """Parse ShineBus binary frame into JSON."""
    if not data or len(data) < 50:
        return None

    try:
        # Example parsing — adjust if needed
        voltage = int.from_bytes(data[10:12], "big") / 10
        current = int.from_bytes(data[12:14], "big") / 10
        power = int.from_bytes(data[14:16], "big")

        return {
            "voltage": voltage,
            "current": current,
            "power": power,
            "raw_hex": data.hex()
        }

    except Exception as e:
        print(f"Error parsing data: {e}")
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mqtt-host")
    parser.add_argument("--mqtt-port", type=int)
    parser.add_argument("--mqtt-username")
    parser.add_argument("--mqtt-password")
    parser.add_argument("--mqtt-topic")
    parser.add_argument("--inverter-host")
    parser.add_argument("--inverter-port", type=int)
    parser.add_argument("--interval", type=int)

    args = parser.parse_args()

    mqtt_client = mqtt.Client()

    if args.mqtt_username:
        mqtt_client.username_pw_set(args.mqtt_username, args.mqtt_password)

    mqtt_client.connect(args.mqtt_host, args.mqtt_port, 60)
    mqtt_client.loop_start()

    print("ShineBus daemon started")

    while True:
        data = read_inverter(args.inverter_host, args.inverter_port)
        parsed = parse_data(data)

        if parsed:
            mqtt_client.publish(args.mqtt_topic, json.dumps(parsed))
            print("Published:", parsed)
        else:
            print("No valid data")

        time.sleep(args.interval)


if __name__ == "__main__":
    main()

