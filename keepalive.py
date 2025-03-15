import requests
from bs4 import BeautifulSoup
import re
import os
import socket
import struct
import time

# 登录Aternos
session = requests.Session()
login_url = "https://aternos.org/go/"
login_data = {
    "user": os.getenv("ATERNO_USER"),
    "password": os.getenv("ATERNO_PASS")
}
response = session.post(login_url, data=login_data)

# 获取服务器IP和端口
status_page = session.get("https://aternos.org/servers/").text
soup = BeautifulSoup(status_page, "html.parser")
server_div = soup.find("div", string=re.compile(os.getenv("SERVER_NAME")))
address = server_div.find_next("div", class_="server-address").text.strip()
ip, port = address.split(":")

# 构造协议握手包（Minecraft 1.12.2）
packet = b'\x00\x00'  # 握手包ID
packet += struct.pack('>i', 335)  # 协议版本号
packet += struct.pack('>b', len(ip)) + ip.encode()  # 服务器地址
packet += struct.pack('>H', int(port))  # 端口号
packet += b'\x01'  # 下一状态为Status
packet = struct.pack('>b', len(packet)) + packet  # 添加长度前缀

# 发送保活信号（重试3次）
max_retries = 3
for attempt in range(max_retries):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5)
            s.connect((ip, int(port)))
            s.send(packet)
            print(f"[Success] 保活信号已发送至 {ip}:{port}")
            break
    except Exception as e:
        print(f"[Error] 第 {attempt+1} 次尝试失败: {str(e)}")
        time.sleep(10)
