import threading
import time
import pywifi
from pywifi import const
from flask import Flask, render_template_string, request, jsonify
import tkinter as tk
from tkinterweb import HtmlFrame
import json
from datetime import datetime
import os
import itertools
import string

app = Flask(__name__)

class WifiScanner:
    def __init__(self):
        self.wifi = pywifi.PyWiFi()
        self.iface = self.wifi.interfaces()[0]
        self.current_network = None
        self.password_found = None

    def scan_wifi(self):
        self.iface.scan()
        time.sleep(2)
        results = self.iface.scan_results()

        networks = []
        for network in results:
            # Calcular distancia aproximada
            rssi = network.signal
            distance = round(10 ** ((27.55 - (20 * 2.4) + abs(rssi)) / 20), 2)
            
            # Obtener información adicional
            encryption_type = self.get_encryption_type(network)
            channel = self.calculate_channel(network)
            
            networks.append({
                "ssid": network.ssid,
                "bssid": network.bssid,
                "signal": rssi,
                "distance": distance,
                "encryption": encryption_type,
                "channel": channel,
                "frequency": self.get_frequency(network),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        return networks

    def get_encryption_type(self, network):
        auth = network.akm[0] if network.akm else "Open"
        if auth == const.AKM_TYPE_WPA2PSK:
            return "WPA2-PSK"
        elif auth == const.AKM_TYPE_WPAPSK:
            return "WPA-PSK"
        elif auth == const.AKM_TYPE_NONE:
            return "Open"
        return "Unknown"

    def calculate_channel(self, network):
        try:
            frequency = network.frequency
            if frequency >= 2412 and frequency <= 2484:
                return int((frequency - 2412) / 5 + 1)
            elif frequency >= 5170 and frequency <= 5825:
                return int((frequency - 5170) / 5 + 34)
            return 0
        except:
            return 0

    def get_frequency(self, network):
        try:
            return f"{network.frequency} MHz"
        except:
            return "Unknown"

    def try_connect(self, ssid, password):
        profile = pywifi.Profile()
        profile.ssid = ssid
        profile.auth = const.AUTH_ALG_OPEN
        profile.akm.append(const.AKM_TYPE_WPA2PSK)
        profile.cipher = const.CIPHER_TYPE_CCMP
        profile.key = password

        self.iface.remove_all_network_profiles()
        tmp_profile = self.iface.add_network_profile(profile)

        self.iface.connect(tmp_profile)
        time.sleep(2)
        
        if self.iface.status() == const.IFACE_CONNECTED:
            return True
        return False

wifi_scanner = WifiScanner()

@app.route('/')
def home():
    wifi_networks = wifi_scanner.scan_wifi()
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Advanced Wi-Fi Scanner</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f9;
            }
            .container {
                max-width: 1200px;
                margin: 20px auto;
                padding: 20px;
                background: white;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                border-radius: 8px;
            }
            h1 {
                text-align: center;
                color: #333;
            }
            .controls {
                margin: 20px 0;
                text-align: center;
            }
            button {
                padding: 10px 20px;
                margin: 0 10px;
                border: none;
                border-radius: 4px;
                background-color: #4CAF50;
                color: white;
                cursor: pointer;
            }
            button:hover {
                background-color: #45a049;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th, td {
                padding: 10px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            tr:hover {
                background-color: #f1f1f1;
            }
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background-color: rgba(0,0,0,0.5);
            }
            .modal-content {
                background-color: white;
                margin: 15% auto;
                padding: 20px;
                width: 80%;
                max-width: 500px;
                border-radius: 8px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Wfi_info_basica</h1>
            <div class="controls">
                <button onclick="saveToFile()">Save to File</button>
                <button onclick="refreshNetworks()">Refresh Networks</button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>SSID</th>
                        <th>BSSID</th>
                        <th>Signal (dBm)</th>
                        <th>Distance (m)</th>
                        <th>Encryption</th>
                        <th>Channel</th>
                        <th>Frequency</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for network in networks %}
                    <tr>
                        <td>{{ network.ssid }}</td>
                        <td>{{ network.bssid }}</td>
                        <td>{{ network.signal }}</td>
                        <td>{{ network.distance }}</td>
                        <td>{{ network.encryption }}</td>
                        <td>{{ network.channel }}</td>
                        <td>{{ network.frequency }}</td>
                        <td>
                            <button onclick="attemptConnect('{{ network.ssid }}')">Connect</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div id="connectModal" class="modal">
            <div class="modal-content">
                <h2>Connect to Network</h2>
                <input type="password" id="passwordInput" placeholder="Enter password">
                <button onclick="tryPassword()">Connect</button>
                <button onclick="closeModal()">Cancel</button>
            </div>
        </div>

        <script>
            function saveToFile() {
                fetch('/save')
                    .then(response => response.json())
                    .then(data => alert(data.message));
            }

            function refreshNetworks() {
                location.reload();
            }

            let currentSSID = '';

            function attemptConnect(ssid) {
                currentSSID = ssid;
                document.getElementById('connectModal').style.display = 'block';
            }

            function closeModal() {
                document.getElementById('connectModal').style.display = 'none';
            }

            function tryPassword() {
                const password = document.getElementById('passwordInput').value;
                fetch('/connect', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ssid: currentSSID,
                        password: password
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    closeModal();
                });
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, networks=wifi_networks)

@app.route('/save')
def save_to_file():
    networks = wifi_scanner.scan_wifi()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"wifi_scan_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(networks, f, indent=4)
    
    return jsonify({"message": f"Network information saved to {filename}"})

@app.route('/connect', methods=['POST'])
def connect_to_network():
    data = request.get_json()
    ssid = data.get('ssid')
    password = data.get('password')
    
    if wifi_scanner.try_connect(ssid, password):
        return jsonify({"message": f"Successfully connected to {ssid}"})
    return jsonify({"message": f"Failed to connect to {ssid}"})

def start_flask():
    app.run(debug=False, use_reloader=False)

def start_tkinter():
    root = tk.Tk()
    root.title("Advanced Wi-Fi Scanner")
    root.geometry("1200x800")

    frame = HtmlFrame(root)
    frame.load_url("http://127.0.0.1:5000/")
    frame.pack(fill="both", expand=True)

    def refresh():
        frame.load_url("http://127.0.0.1:5000/")
        root.after(5000, refresh)

    refresh()
    root.mainloop()

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    time.sleep(1)  # Esperar a que Flask inicie
    start_tkinter()