from data.ApiServiceEstacionMet import ApiServiceEstacionMet 
from model.ModelVarMeTereologica import meteorologicalData as DatMet
from model.ModelCultivo import Crop
from model.ModelSensores import Sensors
from model.ModelPrescriptionResult import PrescriptionResults
from services.mqttComunication import MqttComunication
from services.xbeeCommunication import XbeeCommunication
from services.PrescriptionMethods import prescriptionMethods

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
        '''inicializacion de datos'''
        print('init data')
        self.startDate=date(2020,12,1)
        self.contDays=0
        self.hourPrescription=[0,0]
        self.hourIrrigation=[9,0]
        self.groundDivision="SanRafael"
        self.agent=''
        self.num_GroundDivision=0
        self.prescriptionMode = 'Moisture_Sensor'
        self.FlagPrescriptionDone = False
        self.cropModel = Crop("Maize",20,80,"Moisture_Sensor",
            11,date(2021,5,1),[9,0],[0,0])
        
        
        self.sensors = Sensors('Potato','0x1111111111')
        print(self.sensors._SensorsLevels)
        self.prescriptionResult = PrescriptionResults('--',str(datetime.now()).split()[0],str(datetime.now()).split()[1],0,0,0,0,0,0,0,0,0,0) #resultados de prescripcion
        self.presc_Meth =  prescriptionMethods(self.cropModel,self.sensors,self.prescriptionResult) #inicializacion de etodos de prescripcion
        print(self.presc_Meth.crop._crop)
       
        self.presc_Meth.Moisture_Sensor_Presc()

        print(f'funciona  : {self.presc_Meth.prescriptionResult.allDataPrescription}')

        '''============================ '''

        self.ApiService = ApiServiceEstacionMet()
        self.response = self.ApiService.request_station()
        #datmet = DatMet.from_dict(response)
        self.Mqtt = MqttComunication(1)
        self.xbeeComm=XbeeCommunication("/dev/ttyUSB0",9600,self.sensors)
        self.subproces_Sens=Thread(target=self.xbeeComm.runCallback)
        self.subproces_Sens.daemon=True
        self.subproces_Sens.start()
        #print(sensor.allSensors)

    def realAgentRun(self):
        while True:  
            
            print(self.xbeeComm.sensors.allSensors)
            print(self.sensors.allSensors)
            print(self.presc_Meth.sensors.allSensors)
            self.today = date(datetime.now().year,datetime.now().month,datetime.now().day)
            self.contDays = abs(self.today-self.startDate).days
            self.contWeeks = int(self.contDays/7)+1
            self.hour_now=[datetime.now().hour , datetime.now().minute]
            if  self.hour_now==self.hourPrescription:  
                if self.Mqtt.FlagPetition == False:
                    self.ActualPrescription=self.getPrescriptionData(self.prescriptionMode)
                    self.FlagPrescriptionDone=True
            if  self.Mqtt.FlagPetition==True:
                if self.FlagPrescriptionDone == False:
                    self.ActualPrescription=self.getPrescriptionData(self.prescriptionMode)
                    self.FlagPrescriptionDone=True
                self.Report_Agent = '25;25;25'
                self.mqtt.client.publish(f"Ag/SanRafael/Bloque_1/{self.num_GroundDivision}",f"{self.Report_Agent}",qos=2)     
            if self.FlagPrescriptionDone == True:
                self.hour_now=[datetime.now().hour,datetime.now().minute]
                if self.hour_now==self.hourIrrigation:
                    if self.Mqtt.FlagIrrigation == True:
                        self.xbeeComm.sendIrrigationOrder('s','s',self.ActualPrescription)
                    elif self.Mqtt.FlagNewIrrigation == True :
                        self.xbeeComm.sendIrrigationOrder('s','s',self.Mqtt.NewPrescription)        
            timedelay.sleep(20)



    def getPrescriptionData(self,prescriptionMode):
        if prescriptionMode=='Moisture_Sensors':
            self.prescription = 1.2
            # presc=self.Moisture_Sensor_Presc(contDays)
        elif prescriptionMode=='Weather_Station':            
            # presc=self.Weather_Station_presc(contDays)
            self.prescription = 1.2

        return self.prescription    


if __name__ == "__main__":
    PS= Main()
    timedelay.sleep(5)
    subproces_PrincF=Thread(target=PS.realAgentRun())
    subproces_PrincF.start()


