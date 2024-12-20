# Sensor-Management
BaseHTTPRequestHandlerを使用したデバイスごとのセンサーデータの管理

## サーバー
### BaseHTTPServer.py
サーバー用のコードで, Pythonの標準ライブラリhttp.serverモジュールに含まれているクラスで, HTTPリクエストを処理するための基本的なフレームワークを提供する. このクラスを拡張して独自のHTTPサーバーを構築することができる. 

・run_server()：サーバーIPとサーバーポートを参照してサーバーの開設を行い, 通信・ファイルの送受信の処理が行われる.

・do_POST()：受け取ったデータの処理を行っている。具体的には接続されたデバイスが既存のデバイスか, 未知のデバイスかをIPアドレスで判別しCSVの処理を行う.

・write_csv_header()：初めて接続した機器の受信したデータの種類によってCSVファイルの1行目に何のデータを取得したかを記載する.

・append_csv_data()：機器ごとのCSVファイルにデータを書き込む（機器はIPアドレスで簡易的に識別される).

## クライアント(ESP32)
### BMP280_Sensor.py
BMP280のモジュールファイル(BMP280_module.py)を参照しセンサーデータを取得しサーバーに送信することができる.

・execfile(f"BMP280_module.py")：最初にモジュールを読み込む(モジュールがないとデータが取れない).

・connect_wifi()：SSID_NAME(WI-Fiの名前), SSID_PASS(Wi-Fiのパスワード)を参照してWi-Fi接続を行う.

・send_data_to_vm()：モジュールを通して取得したデータをサーバーに送信する.

### BMP280_Module.py
BMP280センサーからデータを取得するためのモジュールファイル. BMP280のアドレスとレジスタや各種設定が施されている

・read_calibration_params():センサを正確に動作させるために必要なキャリブレーションデータを取得する部分. 

補正係数を取得した後は, このデータを利用して生のセンサデータを補正し, 正しい温度や気圧を計算する. 

・read_temp()：温度データを取得することができる

・read_pressure()：気圧データを取得することができる

## 実行結果
サーバーとクライアントのコードをそれぞれ実行させる.

仮にクライアントが先に実行され, データが送られなかった場合count1のように『送信失敗』という結果が表示される. 何もなければ正常に送受信が行えている.

サーバー側では5秒おきに送信されたデータが取得できている

```
クライアントでの実行結果
MPY: soft reboot
    WiFiに接続します...
    .
    .
    WiFiに接続しました
    count: 1
       Temperature: 26.83 °C,
       Pressure: 1017.922 Pa
    送信失敗
    count: 2
       Temperature: 26.84 °C,
       Pressure: 1017.431 Pa
    count: 3
       Temperature: 26.86 °C,
       Pressure: 1016.998 Pa
    count: 4
       Temperature: 26.86 °C,
       Pressure: 1016.45 Pa
    count: 5
       Temperature: 26.87 °C,
       Pressure: 1016.148 Pa
    count: 6
    .
    .
    .
```

サーバーでの実行結果

<img width="533" alt="basereqest" src="https://github.com/user-attachments/assets/6573aed0-9020-43e9-99e1-4b2ab6e51db8">

サーバーでCSVファイルによるクライアントごとのセンサーデータの管理

<img width="527" alt="temp date" src="https://github.com/user-attachments/assets/9b967670-747c-48e4-bf82-b3e66be14b2e">

詳しい記事は下記のQiitaにあるので参考にしてください

Qiita URL：https://qiita.com/c0a21121/items/313f4c3e1515bd06ac65
