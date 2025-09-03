import time
import paramiko
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime


devices = [
{"name": "R1", "ip": "192.168.1.1", "username": "admin", "password": "cisco"},
{"name": "R2", "ip": "192.168.1.2", "username": "admin", "password": "cisco"},
]

commands = {
"bgp": "show ip bgp summary | include ^Neighbor|^[0-9]",
"eigrp": "show ip eigrp neighbors",
"hsrp": "show standby brief",
"bfd": "show bfd neighbors",
"int": "show ip interface brief | include up|down",
}

def run_command(ip, username, password, cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=username, password=password, timeout=10)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        output = stdout.read().decode()
        ssh.close()
        return output.strip()
    except Exception as e:
        return f"ERROR: {e}"

def collect_status():
    rows = []
    for device in devices:
    row = {"device": device["name"], "timestamp": datetime.now()}
    for proto, cmd in commands.items():
    row[proto] = run_command(device["ip"], device["username"], device["password"], cmd)
    rows.append(row)
    return rows

def predict_anomalies(df):
    model = IsolationForest(contamination=0.1, random_state=42)
    features = df.drop(columns=["device", "timestamp"])
    features_encoded = features.apply(lambda x: pd.factorize(x)[0]) # Encode text
    df["anomaly"] = model.fit_predict(features_encoded)
    return df

all_data = []
for _ in range(3): # run 3 cycles for demo
    data = collect_status()
    all_data.extend(data)
    time.sleep(5)

df = pd.DataFrame(all_data)

#Run anomaly detection
result = predict_anomalies(df)


print("\n--- Monitoring Report ---")
print(result[["device", "timestamp", "anomaly"]])

