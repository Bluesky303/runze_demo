
# runze_demo — 注射泵串口控制

润泽注射泵 **SY-08 (RUNZE)** 的 Python 串口控制工具。基于 RS-232 协议控制泵的推液、吸液、复位和速度调节。

> 本项目为培训练手项目，仅针对 SY-08 单型号实现。通用控制方案由组内其他同事维护。

## 适用场景

- 化学自动化实验中的液体处理
- 微量液体的精确分配与抽取
- 注射泵串口通信协议学习参考

## 快速开始

```bash
pip install pyserial
```

### 基本用法

```python
from PumpControl import PumpControl

# 连接泵（根据实际端口修改）
pump = PumpControl("COM19")

# 先复位
pump.reposition()

# 以 0.5 mL/s 吸入 5 mL
pump.pull(5, 0.5)

# 以 1.0 mL/s 推出 2 mL
pump.push(2, 1.0)

# 复位并关闭连接
pump.close()
```

## 功能

### PumpControl 类

| 方法 | 说明 |
|------|------|
| `reposition(velocity)` | 复位，回到初始位置 |
| `set_velocity(velocity)` | 设置运行速度（最大 1.6667 mL/s） |
| `pull(quantity, velocity)` | 以指定速度吸入指定量（mL），超出容量自动填满 |
| `push(quantity, velocity)` | 以指定速度推出指定量（mL），超出剩余量自动清空 |
| `close()` | 复位后关闭串口连接 |

### 状态码

泵返回的状态码会被自动解析为可读的错误信息：

| 码 | 含义 |
|----|------|
| `00` | 正常 |
| `04` | 电机忙 |
| `05` | 电机堵转 |
| `06` | 未知位置 |
| `07` | 指令被拒绝 |
| `08` | 非法位置 |

## 硬件信息

- **设备**: 润泽注射泵 SY-08（RUNZE）
- **接口**: RS-232 串口
- **波特率**: 9600
- **通信协议**: 自定义校验协议（和校验）
- **参考手册**: [`SY-08（RUNZE）快速使用指南.pdf`](SY-08（RUNZE）快速使用指南.pdf)

## 项目结构

```
runze_demo/
├── PumpControl.py                 # 泵控制类
├── test.py                        # 使用示例
├── req.txt                        # 依赖
├── SY-08（RUNZE）快速使用指南.pdf  # 硬件参考手册
└── README.md
```

## 依赖

- Python >= 3.6
- pyserial
