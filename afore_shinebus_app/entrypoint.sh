#!/bin/bash

python3 /app/shinebus.py \
  --mqtt-host "$MQTT_HOST" \
  --mqtt-port "$MQTT_PORT" \
  --mqtt-username "$MQTT_USERNAME" \
  --mqtt-password "$MQTT_PASSWORD" \
  --mqtt-topic "$MQTT_TOPIC" \
  --inverter-host "$INVERTER_HOST" \
  --inverter-port "$INVERTER_PORT" \
  --interval "$INTERVAL"

