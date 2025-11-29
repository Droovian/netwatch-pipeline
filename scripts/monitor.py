import sys
import os
import json
import psycopg2
import xml.etree.ElementTree as ET

# Load Env Vars (These are injected by Jenkins)
DB_HOST = os.getenv("DB_HOST")
DB_PASS = os.getenv("DB_PASS")
DB_USER = os.getenv("DB_USER", "admin")
DB_NAME = os.getenv("DB_NAME", "netwatch")

def get_speed_results():
    try:
        with open("speed.json", "r") as f:
            data = json.load(f)
        # Convert bits to Mbps
        return data["download"] / 1_000_000, data["upload"] / 1_000_000
    except FileNotFoundError:
        print("Error: speed.json not found")
        return 0.0, 0.0

def get_device_count():
    devices = []
    try:
        tree = ET.parse('scan.xml')
        root = tree.getroot()
        for host in root.findall('host'):
            ip = host.find("address[@addrtype='ipv4']").get('addr')
            devices.append(ip)
    except FileNotFoundError:
        print("Error: scan.xml not found")
    
    return len(devices), ", ".join(devices)

def upload_to_db(down, up, count, dev_list):
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()
        query = """
            INSERT INTO scans (download_speed, upload_speed, connected_devices, raw_device_list)
            VALUES (%s, %s, %s, %s)
        """
        cur.execute(query, (down, up, count, dev_list))
        conn.commit()
        conn.close()
        print(f"SUCCESS: Logged {down:.2f} Mbps and {count} devices to DB.")
    except Exception as e:
        print(f"DB ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("Beginning Process")
    d_speed, u_speed = get_speed_results()
    d_count, d_list = get_device_count()
    
    upload_to_db(d_speed, u_speed, d_count, d_list)