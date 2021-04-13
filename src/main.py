from data.ApiServiceEstacionMet import ApiServiceEstacionMet 
from model.ModelVarMeTereologica import meteorologicalData as DatMet
from model.ModelCultivo import Crop
from model.ModelSensores import Sensors
from services.mqttComunication import MqttComunication
from services.xbeeCommunication import XbeeCommunication

'''
librerias externas al sistema 
'''
from datetime import datetime, date, time, timedelta #para fechas y hora
import time as timedelay #para cronometrar tiempo
from threading import Thread

import sys
print (sys.path)
import requests
import json
import urllib
import json


class Main():
    
    def __init__(self):
        super(Main,self).__init__()
        self.ApiService = ApiServiceEstacionMet()
        self.response = self.ApiService.request_station()
        #datmet = DatMet.from_dict(response)
        self.Cultivo = Crop('Potato','Fuzzmode',0,date(2020,12,1),time(23,25),time(23,25)) 
        self.sensor = Sensors('Potato','0x1111111111')
        self.Mqtt = MqttComunication()
        self.xbeeComm=XbeeCommunication("/dev/ttyUSB0",9600)
        self.subproces_Sens=Thread(target=self.xbeeComm.runCallback)
        self.subproces_Sens.daemon=True
        self.subproces_Sens.start()
        #print(sensor.allSensors)

    def realAgentRun(self):
        while True:  
            print(f'bandera {self.Mqtt.FlagAuth}' )
            if  self.Mqtt.FlagAuth:
                print('hola')
            else:
                print('not hola')
            timedelay.sleep(20)
            

if __name__ == "__main__":
    PS= Main()
    timedelay.sleep(5)
    
    subproces_PrincF=Thread(target=PS.realAgentRun())
    subproces_PrincF.start()


