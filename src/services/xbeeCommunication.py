
import sys
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice,XBee64BitAddress,OperatingMode,RemoteATCommandPacket
from datetime import datetime, date, time, timedelta #para fechas y hora

# "/dev/ttyUSB0"

class XbeeCommunication():
    xbees_properties={'Agent_1': ['0013A20040BE17CE'], 
    'Agent_2': ['0013A20040E8762A'],
    'Agent_3': ['0013A20040E7412C'],
    'Agent_4': ['0013A20040DADF27']}
    def __init__(self, UsbDirection, baudRate):
        self.device=XBeeDevice(UsbDirection,baudRate)
        self.device.open()
        # self.subproces_Sens=Thread(target=self.xbeeComm.runCallback)
        # self.subproces_Sens.daemon=True
        # self.subproces_Sens.start()

    def runCallback(self):
        try: 
            self.device.add_data_received_callback(self.data_receive_callback)
            print("Waiting for data...\n")
            input()
        finally:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
            if device is not None and device.is_open():
                device.close()  

    def data_receive_callback(self, xbee_message):
        source=xbee_message.remote_device.get_64bit_addr()
        source1=str(source)  
        message=str(xbee_message.data.decode())
        print(str(datetime.now()).split()[1])
        print(str(xbee_message.data.decode()))

    def sendIrrigationOrder(self,message,Agent,presc):
        try:
            self.remote_device=RemoteXBeeDevice(self.device,XBee64BitAddress.from_hex_string('0013A20040E8761A'))     
            self.device.send_data(self.remote_device,'SITASK;'+'1;'+str(presc))    
            return True
        except:
            return False