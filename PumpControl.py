import serial
import time

class PumpControl():
    """
    泵控制类
    """
    def __init__(self, SerialPort: str, baud_rate = 9600, timeout = 1): # 初始化
        self.statlist = {"00": None, # 状态列表
                         "01": "帧错误", 
                         "02": "参数错误", 
                         "03": "光耦错误", 
                         "04": "电机忙", 
                         "05": "电机堵转",
                         "06": "未知位置", 
                         "07": "指令被拒绝", 
                         "08": "非法位置", 
                         "FE": "任务挂起",
                         "FF": "未知错误"}
        self.ser = serial.Serial(SerialPort, baud_rate, timeout=timeout)
        #state = self.examine()
        self.addr = "06"
        self.reposition()
        self.quantity = 0
        self.velocity = 1.6667

    def examine(self) -> list: # （还没实现)检查波特率， 地址， 协议等；返回状态 or 设置状态
        pass 

    def int_to_hex(self, num: int) -> str: # 将整数转化为需要的指令格式
        return hex(num)[2:].rjust(4, '0')

    def send_codes(self, func: str, params = "0000", return_lenth = 8) -> str: # 生成命令码并发送，接受返回信息
        codelist = ["cc", self.addr, func, params[2:], params[:2], "dd"]
        # 生成校验码
        testcode = self.int_to_hex(sum([int(i, 16) for i in codelist]))
        codelist += [testcode[2:], testcode[:2]]
        code = " ".join(codelist)
        # 发送指令
        self.ser.write(bytes.fromhex(code)) 
        # 接收返回码
        return_code = []
        for i in range(return_lenth): 
            return_code.append(bytes.hex(self.ser.read()))
            
        return return_code
    
    def stat_check(self) -> str: # 检查电机状态直到电机正常，不正常报错
        stat = self.send_codes("4A")[2]
        while(stat == "04"): # 等待泵响应
            time.sleep(0.1)
            stat = self.send_codes("4A")[2]
        if not stat == "00": raise PumpException('电机状态错误', self.send_codes("4A")[2])
        print("电机结束动作")

    def reposition(self,velocity = 1.6667, timeout = 5): # 复位
        self.set_velocity(velocity)
        # 传递复位指令
        return_bytes = self.send_codes("45")
        # 检查是否正常执行
        if not return_bytes[2] == "fe": raise PumpException('复位错误', code=return_bytes[2])
        self.stat_check()
        print("复位完成")

    def set_velocity(self, velocity: float): # 速度最大1.6667mL/s, 最小0.0028mL/s
        if velocity > 1.6667 and velocity < 0.0028: raise PumpException("速度设置错误")
        # 设置速度
        param = self.int_to_hex(round(velocity*600/1.6667))
        reply = self.send_codes("4B", param)
        if not reply[2] == "00": raise PumpException('速度设置错误', code=reply[2])
        print(f"速度设置为:{velocity:.4f}mL/s")

    def push(self, quantity: float, velocity: float, timeout = 5): # 以一定速度(mL/s)推出一定量(mL)。推出量大于当前量视为全部推出
        self.set_velocity(velocity)
        # 检查量
        if quantity < 0: raise PumpException("推出量设置小于0")
        # 推出
        if quantity > self.quantity: quantity = self.quantity
        param = self.int_to_hex(round(quantity*12000/5))
        reply = self.send_codes("42", param)
        if not reply[2] == "fe": raise PumpException('推出错误', code=reply[2])
        self.quantity -= quantity
        self.stat_check()
        print(f"成功推出{quantity:.2f}mL, 目前剩余{self.quantity:.2f}mL")
    
    def pull(self, quantity: float, velocity: float, timeout = 5): # 以一定速度(mL/s)吸入一定量(mL)。吸入量大于空余部分则视为填满
        self.set_velocity(velocity)
        # 检查量
        if quantity < 0: raise PumpException("吸入量设置小于0")
        # 推出
        if quantity > 5 - self.quantity: quantity = 5 - self.quantity
        param = self.int_to_hex(round(quantity*12000/5))
        reply = self.send_codes("4D", param)
        if not reply[2] == "fe": raise PumpException('吸入错误', code=reply[2])
        self.quantity += quantity
        self.stat_check()
        print(f"成功吸入{quantity:.2f}mL, 现有{self.quantity:.2f}mL")

    def close(self): #关闭并复位
        self.reposition()
        self.ser.close()


class PumpException(Exception): # 错误类
    def __init__(self, msg, code = "00"):
        self.errordict = {"00": None, 
                          "01": "帧错误", 
                          "02": "参数错误", 
                          "03": "光耦错误", 
                          "04": "电机忙", 
                          "05": "电机堵转",
                          "06": "未知位置", 
                          "07": "指令被拒绝", 
                          "08": "非法位置", 
                          "FE": "任务挂起",
                          "FF": "未知错误"}
        self.msg = msg
        self.code = code
    def __str__(self):
        return_msg = self.msg 
        if not self.code == "00":
            return_msg += ", 电机状态：" + self.errordict[self.code]
        return return_msg
