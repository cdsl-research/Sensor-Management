from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import csv

# VMのIPアドレスとポート番号
VM_IP = ''  # VMの実際のIPアドレスに置き換える
VM_PORT = 8000

class DataHandler(BaseHTTPRequestHandler):
device_data = {}

def write_csv_header(self, csv_file, data):
    """CSVファイルにヘッダーを書き込む"""
    headers = []
    if 'temperature' in data:
        headers.append('Temperature (C)')
    if 'pressure' in data:
        headers.append('Pressure (Pa)')
    with open(csv_file, mode='w', newline='') as file:
        csv.writer(file).writerow(headers)

def append_csv_data(self, csv_file, data):
    """CSVファイルにデータを書き込む"""
    row = []
    if 'temperature' in data:
        row.append(data['temperature'])
    if 'pressure' in data:
        row.append(data['pressure'])
    with open(csv_file, mode='a', newline='') as file:
        csv.writer(file).writerow(row)

def do_POST(self):
    # リクエストデータを取得
    content_length = int(self.headers['Content-Length'])
    post_data = self.rfile.read(content_length)
    data = json.loads(post_data.decode('utf-8'))
    client_ip = self.client_address[0]

    # クライアントごとのCSVファイルを準備
    if client_ip not in self.device_data:
        csv_file = f"temperature_data_{client_ip.replace('.', '_')}.csv"
        self.write_csv_header(csv_file, data)
        self.device_data[client_ip] = csv_file
    csv_file = self.device_data[client_ip]

    # データをCSVに保存
    self.append_csv_data(csv_file, data)

    # 応答を返す
    self.send_response(200)
    self.end_headers()
    self.wfile.write("Data received and saved successfully".encode('utf-8'))

#HTTPサーバーの設定と起動
def run_server():
    server_address = (VM_IP, VM_PORT)
    httpd = HTTPServer(server_address, DataHandler)
    print(f'Starting HTTP server on {VM_IP}:{VM_PORT}...')
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
