import serial
import time
import random


PORT = 'COM3' 
with serial.Serial(PORT, 115200, timeout=1) as ser:
    print(f"虚拟硬件已启动，正在 {PORT} 端口发送数据...")
    while True:
        # 模拟温度数据
        # 模拟温度：20到35度之间随机
        temp = 25.0 + random.uniform(-5, 10)
        # 制造一个极端高温的情况（大约10%的概率），用来测试上位机的报警和曲线变红
        if random.random() < 0.1:
            temp = 32.0 + random.uniform(0, 3)  # 强制生成32-35度的高温
        data = f"TEMP:{temp:.1f}\n"
        # 把字符串编码成二进制发出去
        ser.write(data.encode('utf-8'))
        print(f"发送: {data.strip()}")
        time.sleep(1)