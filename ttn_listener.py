import paho.mqtt.client as mqtt
import json
import base64
from database import init_db, save_packet, save_reading, get_latest

DEVICES = {"A840413AA189639E": "ARDUINO SHIELD 1"}

TTN_APP_ID = "my-test-app-aseke"
TTN_API_KEY = "NNSXS.QRAPMAEA73RMKN536ZCYPUN7FVMCDDZIFMGQZFI.YXV6CHO23PPIYRROMGRA3MLW32GRUM5GDZBBTZANKM22G6AMMDFA"
TTN_REGION = "eu1"


# Обновленная функция on_connect для версии 2.x (добавлен аргумент properties)
def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("✅ Успешно подключено к TTN MQTT Broker!")
        # Подписываемся на все устройства приложения
        topic = f"v3/{TTN_APP_ID}@ttn/devices/+/up"
        client.subscribe(topic)
        print(f"📡 Подписка на топик: {topic}")
    else:
        print(f"❌ Ошибка подключения. Код результата: {rc}")


# Функция обработки сообщений (сигнатура для 2.x совместима, если не менять логику)
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        dev_eui_raw = data["end_device_ids"]["dev_eui"]
        display_name = DEVICES.get(dev_eui_raw, dev_eui_raw)
        received_at = data["received_at"]
        uplink = data.get("uplink_message", {})

        # Декодируем payload
        payload_bytes = base64.b64decode(uplink.get("frm_payload", ""))

        # Получаем метаданные (RSSI и SNR)
        meta = uplink.get("rx_metadata", [{}])[0]
        rssi = meta.get("rssi", 0)
        snr = meta.get("snr", 0)

        # Парсим байты (согласно твоему Arduino скетчу)
        if len(payload_bytes) >= 8:
            pm1 = (payload_bytes[0] << 8) | payload_bytes[1]
            pm25 = (payload_bytes[2] << 8) | payload_bytes[3]
            pm10 = (payload_bytes[4] << 8) | payload_bytes[5]
            temp = payload_bytes[6]
            hum = payload_bytes[7]

            # Сохраняем в базу данных
            save_reading(display_name, received_at, rssi, snr, pm1, pm25, pm10, temp, hum)
            save_packet(display_name, received_at, payload_bytes.hex().upper())

            print(f"\n📥 Получены данные от [{display_name}]")
            print(f"PM2.5: {pm25} | T: {temp}°C | H: {hum}% | RSSI: {rssi}")

            # Вывод последних данных для контроля
            print("Последние данные из БД:")
            for row in get_latest(2):
                # row: (id, dev_eui, pm25, temp, hum, received_at)
                print(f"  ID {row[0]}: PM2.5={row[2]}, T={row[3]}, H={row[4]}")

    except Exception as e:
        print(f"⚠️ Ошибка обработки сообщения: {e}")


if __name__ == "__main__":
    init_db()

    # КРИТИЧЕСКОЕ ИЗМЕНЕНИЕ: указываем CallbackAPIVersion.VERSION2
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    client.username_pw_set(f"{TTN_APP_ID}@ttn", TTN_API_KEY)
    client.on_connect = on_connect
    client.on_message = on_message

    print("🔌 Соединение с TTN...")
    try:
        client.connect(f"{TTN_REGION}.cloud.thethings.network", 1883, 60)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n🛑 Остановка листнера...")
        client.disconnect()