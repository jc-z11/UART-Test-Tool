# UART Test Tool (串口测试上位机)
## 📖 项目简介
基于 Python + PyQt6 开发的一款硬件测试上位机。实现“虚拟硬件数据发送 -> 虚拟串口传输 -> 上位机接收分析”的完整链路。

## ✨ 功能特性
- 多线程数据采集（QThread），避免界面卡顿。
- 看门狗机制与异常容错，断线不崩溃。
- 数据缓冲区机制，解决串口粘包/断包问题。
- 实时数据解析、CSV持久化存储与阈值（>30°C）报警。

## 🛠️ 技术栈
- 语言：Python
- GUI：PyQt6
- 通信：pyserial
- 测试环境：VSPD虚拟串口

## 🚀 运行说明
1. 安装依赖：`pip install -r requirements.txt`
2. 使用 VSPD 创建 COM3 (发送端) 与 COM4 (接收端)。
3. 运行发送端：`python hardware_simulator.py`
4. 运行上位机：`python uart_test_tool.py`，选择 COM4，波特率选 115200，点击 Connect。