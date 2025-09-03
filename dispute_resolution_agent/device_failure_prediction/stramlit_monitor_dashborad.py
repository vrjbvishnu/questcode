
import time
import streamlit as st
import pandas as pd
import paramiko
from datetime import datetime
from sklearn.ensemble import IsolationForest

-----------------------------
Device Inventory
-----------------------------
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

-----------------------------
SSH Function
-----------------------------
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
features_encoded = features.apply(lambda x: pd.factorize(x)[0])
df["anomaly"] = model.fit_predict(features_encoded)
return df

-----------------------------
Streamlit Dashboard
-----------------------------
st.set_page_config(page_title="Network Health Dashboard", layout="wide")

st.title("🌐 Network Failure Prediction Dashboard")
st.markdown("Monitor BGP, EIGRP, HSRP, BFD, and Interfaces in real time.")

placeholder = st.empty()
data_log = []

refresh_rate = st.sidebar.slider("Refresh Interval (seconds)", 5, 60, 10)

while True:
new_data = collect_status()
data_log.extend(new_data)
df = pd.DataFrame(data_log)
df = predict_anomalies(df)

with placeholder.container():
    st.subheader("📊 Live Device Status")
    st.dataframe(df.tail(len(devices)))

    st.subheader("⚠️ Predicted Anomalies")
    st.dataframe(df[df["anomaly"] == -1])

    st.line_chart(df.groupby("timestamp")["anomaly"].sum())

time.sleep(refresh_rate)
