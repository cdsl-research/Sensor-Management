import network
import urequests
import machine
import time
import json
from machine import Pin, SoftI2C

# WiFi接続情報の読み込み
SSID = ""

PASSWORD = ""

#モジュールの読み込み
execfile(f"BMP280_Module.py")

# VMのIPアドレスとポート番号
VM_IP = ''  # VMの実際のIPアドレスに置き換える
VM_PORT = 8000

# BMP280センサの初期化
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
init_bmp280(i2c)
count = 0

led_blue = machine.Pin(2, Pin.OUT)

# WiFiに接続する関数
def connect_wifi(ssid, passkey, timeout=10):
    wifi = network.WLAN(network.STA_IF)
    if wifi.isconnected():
        print('WiFiに接続済み。接続をスキップします。')
        return wifi
    else:
        wifi.active(True)
        wifi.connect(ssid, passkey)
        while not wifi.isconnected() and timeout > 0:
            print('.')
            time.sleep(1)
            timeout -= 1

    if wifi.isconnected():
        print('WiFiに接続しました')
        led_blue.value(1)
        return wifi
    else:
        print('WiFiへの接続に失敗しました')
        return None

# データをVMに送信する関数
def send_data_to_vm(temperature, pressure):
    url = f'http://{VM_IP}:{VM_PORT}'
    headers = {'Content-Type': 'application/json'}
    data = {
        "temperature": temperature,
        "pressure": pressure
    }
    response = urequests.post(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        #print('データの送信に成功しました')
        return
    else:
        print(f'データの送信に失敗しました: {response.status_code}')
    response.close()

# メインプログラムの実行部分
print('WiFiに接続します...')
wifi = connect_wifi(SSID, PASSWORD)

if wifi:
    while True:
        try:
            temp = str(read_temp(i2c))
        except:
            temp = "None"
        try:
            pres = str(read_pressure(i2c))
        except:
            pres = "None"
        
        print(f'count: {count+1}\n   Temperature: {temp} °C,\n   Pressure: {pres} Pa')
        try:
            send_data_to_vm(temp, pres)
        except Exception as e:
            print("送信失敗")
        time.sleep(5)  # 5秒間隔でデータを送信（適宜調整）
