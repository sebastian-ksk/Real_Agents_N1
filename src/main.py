from data.ApiServiceEstacionMet import ApiServiceEstacionMet 
from data.FireBase import FIREBASE_CLASS
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

from apscheduler.schedulers.background import BackgroundScheduler  #para programar tareas

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
        self.groundDivision="SanRafael"
        self.agent=1
        self.FlagPrescriptionDone = False
        #estacion meteorlogica
        '''consulta a estacion metereologica a las 00:00 todos los dias '''
        self.apiServiceMet = ApiServiceEstacionMet(DatMet)
        self.schedWeatherSatation = BackgroundScheduler()
        self.schedWeatherSatation.add_job(self.apiServiceMet.checkStation, 'cron',  hour = 0, minute = 0)
        self.schedWeatherSatation.start()
        #modelo defaul del cultivo
        self.cropModel = Crop("Maize",20,80,"Moisture_Sensor",11,date(2020,1,1),'00:00',"00:00")
        print('-- firebase -- ')
        #conexion a firebase y actualizacion de datos
        self.FB=FIREBASE_CLASS('Sanrafael_2',self.cropModel)
        #Modelo de sensores 
        self.sensors = Sensors(self.cropModel.typeCrop,'0x000000000')
        print(f'niveles de sensores: { self.sensors._SensorsLevels}' )
        #Modelo Resultados de prescripciones
        self.prescriptionResult = PrescriptionResults('--',str(datetime.now()).split()[0],str(datetime.now()).split()[1],0,0,0,0,0,0,0,0,0,0) #resultados de prescripcion
        #modelo de metodos de prescripciones
        self.presc_Meth =  prescriptionMethods(self.cropModel,self.sensors,self.prescriptionResult) #inicializacion de metodos de prescripcion
        self.presc_Meth.Moisture_Sensor_Presc()
        '''========Inicializacion de Protocolos de comunicacion ====='''
        self.Mqtt = MqttComunication( self.agent)
        timedelay.sleep(5)
        print('---------XbeeCommunication --------------------')
        self.xbeeComm=XbeeCommunication("/dev/ttyUSB0",9600,self.sensors)
        self.subproces_Sens=Thread(target=self.xbeeComm.runCallback)
        self.subproces_Sens.daemon=True
        self.subproces_Sens.start()
        #print(sensor.allSensors)

   
    def realAgentRun(self):
        while True:  
            
            # print(self.xbeeComm.sensors.allSensors)
            # print(self.sensors.allSensors)
            # print(self.presc_Meth.sensors.allSensors)
            #contador de dias
            self.today = date(datetime.now().year,datetime.now().month,datetime.now().day)
            self.cropModel.dayscrop = abs(self.today-self.cropModel.seedTime).days

            self.contWeeks = int(self.cropModel.dayscrop/7)+1

            if self.FlagPrescriptionDone == False:
                self.horNouwStr = f'{datetime.now().hour}:{datetime.now().minute}'
                if  self.horNouwStr==self.cropModel.presctime: 
                    if self.Mqtt.FlagPetition == False:
                        self.ActualPrescription=self.getPrescriptionData(self.cropModel.prescMode)
                        print(f'Prescription= {self.ActualPrescription}')
                        self.FlagPrescriptionDone=True       
                if  self.Mqtt.FlagPetition==True:
                    if self.FlagPrescriptionDone == False:
                        self.ActualPrescription=self.getPrescriptionData(self.cropModel.prescMode)
                        self.FlagPrescriptionDone=True
                    self.Report_Agent = self.AgentReport()
                    self.Mqtt.client.publish(f"Ag/SanRafael/Bloque_1/{self.agent}",f"{self.Report_Agent}",qos=2)     
           
            elif self.FlagPrescriptionDone == True:
                self.horNouwStr = f'{datetime.now().hour}:{datetime.now().minute}'
                if self.horNouwStr == self.cropModel.irrigationtime:
                    if self.Mqtt.FlagIrrigation == True:
                        print('sent irrigation')
                        self.xbeeComm.sendIrrigationOrder('SITASK', self.agent,self.ActualPrescription)
                        self.FlagPrescriptionDone = False
                        self.Mqtt.FlagIrrigation = False
                    elif self.Mqtt.FlagNewIrrigation == True :
                        self.xbeeComm.sendIrrigationOrder('SITASK', self.agent,self.ActualPrescription)
                        self.FlagPrescriptionDone = False
                        self.Mqtt.FlagIrrigation = False
            
            timedelay.sleep(5)

    def AgentReport(self):
        self.prescData = self.prescriptionResult.allDataPrescription
        LOTE,CROP_DEFAULT,STAR_DATE = self.groundDivision,self.cropModel.typeCrop,self.cropModel.seedTime
        presc,Kc,Ks=self.prescData[3],self.prescData[5],self.prescData[9]
        CONT_DAYS,CONT_WEEK,root_depth = self.cropModel.dayscrop,self.contWeeks,self.prescData[7]
        Taw,Mae,PRESC_MODE_send=self.prescData[8],self.prescData[9],self.prescData[0].split('-')[0]
        VWC,deple=self.sensors.allSensors[0],self.prescData[4]
        date_report,hour_report=date_report=str(datetime.now()).split()[0],str(datetime.now()).split()[1]
        Report_Agent=f"{LOTE};{CROP_DEFAULT}.CRO;{str(STAR_DATE)};{presc};{Kc};{Ks};{CONT_DAYS};{CONT_WEEK};{root_depth};{Taw};{Mae};{PRESC_MODE_send};{VWC};{deple};{date_report};{hour_report}"
        return Report_Agent

    def getPrescriptionData(self,prescriptionMode):
        
        if prescriptionMode=='Moisture_Sensors':
            #self.prescription = 1.2
            self.prescription=self.presc_Meth.Moisture_Sensor_Presc()
        elif prescriptionMode=='Weather_Station':            
            self.prescription=self.presc_Meth.Weather_Station_presc(self.cropModel.dayscrop)
            #self.prescription = 1.2
        else:
            self.prescription = 1

        return self.prescription    


if __name__ == "__main__":
    PS= Main()
    timedelay.sleep(5)
    subproces_PrincF=Thread(target=PS.realAgentRun())
    subproces_PrincF.start()

