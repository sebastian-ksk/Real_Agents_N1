# -*- coding: utf-8 -*-
"""
===============================================================================================================
========================================SCRIPT  GENERAL MAIN===================================================
============================SISTEMA CENTRAL DE CONTROL DEL AGENTE REAL EN CAMPO================================
===============================================================================================================
DESCRIPCION:Este script realiza la lectura de los datos y el acceso total a las funciones, ademas después de 
    organizar los datos necesarios para generar el  controldelagentereal, y ademas almacena los datosen la base 
    de datos de google fitebase.
"""
#===========IMPORTACIONB DE LIBRERIEAS 
import sys
import paho.mqtt.client
from pathlib import Path
import os
#====LIBRERIAS PARA ACCESO AL TIEMPO 
import time
import datetime
from datetime import date
from datetime import time as tm
from datetime import datetime,timedelta
import signal
#====LIBRERIA PARAGENERAE HILOS EN EL PROHRAMA===
from threading import Thread
import random
#====== LIBRERIAS PARAELMANEGO DE DISPOSITIVO DE TRANSMISION XBEE
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice,XBee64BitAddress,OperatingMode,RemoteATCommandPacket
import math
#=======LIBRERIAS DELSDK PARA EL ACCESO A LOS DATOS DE firebase DESDE EL MODULO ADMINISTRADOR
import firebase_admin 
from firebase_admin import credentials #ACCESO A LAS LLAVES PRIVADAS DEL MODULO DE ADMIN O DATOS DE ALMACVENAMIENTO
from firebase_admin import db  #ACCESO A LA BASE DE DATOS
from firebase_admin import firestore  #ACCESO A LA BASE DE DATOS
#==========================LIB LOGICA DIFUSA ========================
import matplotlib
matplotlib.use('Agg')
import numpy as np
import skfuzzy.control as ctrl
import skfuzzy as fuzz
#====================================================================

#cooeficientes de cultivos
Crop={"Maize": [25,37,40,30,   0.30,1.2,0.5,   0,0.4572,    5,108,0.55 ],
"Potato":      [25,30,36,30,   0.5,1.15,0.75,  0,0.3048,     6,100,0.25],
"Tomato":      [25,30,30,25,   0.60,1.15,0.8,  0.04,0.3048,  7,55,0.50],
"Barley":      [40,60,60,40,   0.30,1.15,0.25, 0,0.498,      11,93,0.55],
"Wheat":       [40,60,60,37,   0.30,1.15,0.4,  0,0.519,      14,60,0.55],
"Quinoa":      [25,60,60,35,   0.30,1.2,0.5,   0,0.4645,     9,83,0.50],
"Onion":       [21,42,49,38,   0.40,0.85,0.35, 0.04,0.165,   7,105,0.25]} 
cropcoeff=[0.36,0.36,0.39,0.43,0.43,0.43,0.53,0.59,0.77,0.77,0.8,0.9,0.73,0.66,0.7,0.6,0.34,0.36,0.35,0.35,0.35,0.35,0.35]

#niveles donde se encuentran los sensores
Sens_Lev={
"Maize":   [0.23,0.46,0.69,0.92,2.30],
"Potato":  [0.15,0.31,0.45,0.61,1.50],
"Tomato":  [0.15,0.31,0.45,0.61,1.00],
"Barley":  [0.26,0.52,0.78,1.04,1.50],
"Wheat":   [0.25,0.50,0.75,1.00,1.30],
"Quinoa":  [0.23,0.47,0.69,0.92,1.00],
"Onion":   [0.10,0.20,0.20,0.20,0.20]} 


PWP=25
FIELD_CAPACITY=70
CROP_DEFAULT='Onion'
PRESC_MODE='Fuzzy_System'
STAR_DATE=date(2020,12,1)
CONT_DAYS=0
HOUR_PRESC=[0,0]
IRR_SPEED=1 #mm/s
HOUR_IRRIG=[9,0] #hora de riego 
LOTE="SanRafael"

AGENT=''
NUM_LOTE=0

Path_Data="/home/pi/Desktop/Real_Agents_N1/Data"

Level=0
Flag_Pet=False
flag_seD=False
Fl_Irr=False #bandera de riego sin negociacion
Fl_IrrN=False #bandera de riego con Negociacion
Fl_Pres=False
Fl_petp=False

Date_R=""
Hour_R=""
New_pr=[0]*1092 #prescripciones nuevas por negociacion
device=XBeeDevice("/dev/ttyUSB0",9600)
device.open()

#agent#: ['PAN_ID DE NODO','DIRECCION DE XBEE ACTUADORES']
Xbees_properties={'Agent_1': ['0013A20040BE17CE'], 
'Agent_2': ['0013A20040E8762A'],
'Agent_3': ['0013A20040E7412C'],
'Agent_4': ['0013A20040DADF27']}

#-------------Firebase--------------
PAHT_CRED = 'Clave_Firebase.json'
URL_DB = 'https://inteligentagent-2cac4-default-rtdb.firebaseio.com/'


class FIREBASE_CLASS():
    def __init__(self):
        global AGENT 
        cred=credentials.Certificate(PAHT_CRED)
        firebase_admin.initialize_app(cred,{
            'databaseURL':URL_DB
        })   
        #self.val1 =firestore.client().collection('agentes').document('Agente1').set({"array":[1,2,3,4,5],"datyos":135.576})
        self.refAgents=db.reference('Agent')
        self.refAgent=self.refAgents.child(AGENT)
        self.refCrop=self.refAgent.child('Crop')
        self.refCultive_days=self.refAgent.child('Cultive_days')
        self.reFild_Cap=self.refAgent.child('Field_Cap')
        self.refId=self.refAgent.child('Id')
        self.refIrrig_Hour=self.refAgent.child('Irrig_Hour')
        self.refIrrig_aplied=self.refAgent.child('Irrig_applied')
        self.refPwp=self.refAgent.child('PWP')
        self.refPrescMethod=self.refAgent.child('Prescription_Method')
        self.refSeedtime=self.refAgent.child('seedtime')

    def Hour_applied_S(self):
        global HOUR_IRRIG
        prev_hour="--"
        while True:
            act_hour=self.refIrrig_Hour.get()
            if act_hour != prev_hour:
                HOUR_IRRIG[0]=int(str(act_hour).split(':')[0])
                HOUR_IRRIG[1]=int(str(act_hour).split(':')[1])
                print(f"hora de riego modificada: {act_hour} ")
                prev_hour=act_hour
        

class PumpStation():
    def __init__(self): 
        global device, AGENT,LOTE, Xbees_properties, NUM_LOTE
        print('INGRESE EL NUMERO DEL AGENTE A EJECUTAR [1-4]')
        numero_agente=input()
        while int(numero_agente) <0 or int(numero_agente)>4:
            print('error [1-4]')
            numero_agente=input()
        AGENT='Agent_'+numero_agente
        NUM_LOTE=int(numero_agente)
        LOTE=LOTE+numero_agente
        print(AGENT)
        print("id_pan")
        print(device.get_pan_id())
        print(".......")
        #self.Init_Menu()
        
        self.client =paho.mqtt.client.Client(client_id='Real_'+AGENT, clean_session=False)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host='104.248.53.140', port=1883)
        self.client.username_pw_set( "agent" ,  password = "789.123" ) 
        self.client.loop_start()
        
        self.FB=FIREBASE_CLASS()
        self.subproces_Hour_Irrig=Thread(target=self.FB.Hour_applied_S)
        self.subproces_Hour_Irrig.daemon=True
        self.subproces_Hour_Irrig.start()

        self.SD= Sens_Data()
        self.subproces_Sens=Thread(target=self.SD.run)
        self.subproces_Sens.daemon=True
        self.subproces_Sens.start()
        self.FB.refCrop.set(CROP_DEFAULT)
        self.FB.refCultive_days.set(CONT_DAYS)
        self.FB.reFild_Cap.set(FIELD_CAPACITY)
        self.FB.refId.set(LOTE)
        self.FB.refPwp.set(PWP)
        self.FB.refPrescMethod.set(PRESC_MODE)
        self.FB.refSeedtime.set(str(STAR_DATE))

    #------------------------FUNCIONES MQTT-----------------------------------
    def on_connect(self,client, userdata, flags, rc):
        print('connected (%s)' % client._client_id)
        #suscripcion al agente Source

        self.client.subscribe(topic='PmS/SanRafael/Ag', qos=0)
        self.client.unsubscribe("Ag/#")

    def on_message(self,client, userdata, message):
        global Date_R,Fl_Irr,Fl_IrrN,NEW_PRESC,Fl_petp
        data=str(message.payload).split("'")[1].split(":")  #split mensaje con ":"
        topic=str(message.topic).split("/")[0]
        if topic=="PmS":
            print('------------------------------')
            print('received: ')
            print('topic: %s' % message.topic)
            print('payload: %s' % message.payload)
            print('qos: %d' % message.qos)
            if data[0]=="Rp":                               #si el mensaje inicia como Rp 
                Date_R=data[1].split(';')[0]     
                today = str(date.today()).split()[0]         
                print(Date_R)
                if Date_R== today:
                    Fl_petp=True                                #se activa bandera de peticcion   
            elif data[0]=="Irr":                            #si el mensaje inicia como Irr=Riego    
                if data[1]=="Cont":                         #si la accion es continuar    
                    Fl_Irr=True                             #activa bandera de reigo por prescripcion local
                elif data[1].split(";")[0]=="Neg":          #si es Neg
                    if  NUM_LOTE== int(data[1].split(";")[1]):
                        NEW_PRESC=int(data[1].split(";")[2])      #se guarda el dato del nuevo valor de prescipcion 
                        Fl_IrrN=True                            #se activa bandera de riego por negociacion
                pass 

    def Init_Menu(self): 
        global PWP,STAR_DATE,CROP_DEFAULT,FIELD_CAPACITY,NUM_LOTE
        try:
            print("TIPO DE CULTIVO :")
            crops={1:"Maize",2:"Potato",3:"Tomato",4:"Barley",5:"Wheat",6:"Quinoa",7:"Onion"}
            for i in range(len(crops)):
                print(str(i+1)+". "+str(crops[i+1]))
            print("TIPO DE CULTIVO :" , end="")    
            sel=input()
            print("continuar")
            CROP_DEFAULT=crops[int(sel)]
            print("cultivo:" + CROP_DEFAULT) 
            print("DIA DE INICIO: ", end="")
            day=input()
            print("MES DE INCIO: ", end="")
            month=input()
            print("AÑO DE INCIO: ", end="")
            year=input()
            STAR_DATE=date(int(year),int(month),int(day))
            print("DAY START CROP: "+ str(STAR_DATE))
            print("MODO DE PRESCRIPCION")
            prespc={1:"Moisture_Sensors",2:"Weather_Station",3:"Fuzzy_System"}
            for i in range(len(prespc)):
                print(str(i+1)+". "+str(prespc[i+1]))
            print("INGRESE MODO DE PRESCRIPCION: ", end="")
            sel=input()
            PRESC_MODE=prespc[int(sel)]
            print("INGRESE PUNTO DE MARCHITEZ PERMANENTE: ")
            PWP=float(input())
            print("INGRESE CAPACIDAD DE CAMPO %: ")
            FIELD_CAPACITY=float(input())
        except:
            print("error ingreso erroneo de datos....")
        return

    #------------------------------------------------------------------------- 
    def Princip_Funcion(self):
        global Date_R,Fl_Irr,Fl_IrrN,New_pr,Fl_petp,Fl_Pres
        global CROP_DEFAULT,PRESC_MODE,CONT_DAYS,NEW_PRESC,HOUR_IRRIG,LOTE,NUM_LOTE
        global device
        global IRR_SPEED
        print("init")

        while True:     
            today = str(date.today()).split()[0]
            now=datetime.now()
            today = date(now.year,now.month,now.day)
            CONT_DAYS=abs(today-STAR_DATE).days
            CONT_WEEK=int(CONT_DAYS/7)+1
            hour_now=[datetime.now().hour,datetime.now().minute]
            if  hour_now==HOUR_PRESC:  
                if Fl_Pres==False:
                    if PRESC_MODE=='Moisture_Sensors':
                        presc=self.Moisture_Sensor_Presc(CONT_DAYS)
                    elif PRESC_MODE=='Weather_Station':            
                        presc=self.Weather_Station_presc(CONT_DAYS)
                    elif PRESC_MODE=='Fuzzy_System':
                        file_SeD= open(Path_Data+'/Sensors_Data.txt', 'r',errors='ignore')
                        data = file_SeD.read().splitlines()
                        VWC=float(data[-1].split(';')[2])      
                        file_SeD.close
                        presc=self.Fuzzy_Metod_Presc(VWC,25,35)
                        
                    print(f"""HORA DE PRESCRIPCION: {HOUR_PRESC[0]}:{HOUR_PRESC[1]}
                            PRESCIPCION={presc} mm """)    
                    Fl_Pres=True      
            if  Fl_petp==True:
                if Fl_Pres==False:
                    if PRESC_MODE=='Moisture_Sensors':
                        presc=self.Moisture_Sensor_Presc(CONT_DAYS)
                    elif PRESC_MODE=='Weather_Station':            
                        presc=self.Weather_Station_presc(CONT_DAYS)
                    elif PRESC_MODE=='Fuzzy_System':
                        file_SeD= open(Path_Data+'/Sensors_Data.txt', 'r',errors='ignore')
                        data = file_SeD.read().splitlines()
                        VWC=float(data[-1].split(';')[2])      
                        file_SeD.close
                        print(f'vwc: {VWC}')
                        presc=self.Fuzzy_Metod_Presc(VWC,25,35)    
                    Fl_Pres=True    
                else:
                    pass
                print(f"IRRIGATION PRECRIPTION= {presc}")
                date_report=str(datetime.now()).split()[0]
                hour_report=str(datetime.now()).split()[1]
                file_SeD= open(Path_Data+'/Sensors_Data.txt', 'r',errors='ignore')
                data = file_SeD.read().splitlines()
                VWC=float(data[-1].split(';')[2])      
                file_SeD.close

                file_HiD= open(Path_Data+"/History_Data.txt", 'r',errors='ignore')
                data = file_HiD.read().splitlines()
                Kc=float(data[-1].split(';')[5])
                root_depth=data[-1].split(';')[6]
                Taw=data[-1].split(';')[7] 
                Mae=data[-1].split(';')[8]
                Ks=float(data[-1].split(';')[10])
                deple=data[-1].split(';')[4]
                file_HiD.close()
                if PRESC_MODE=='Moisture_Sensors':
                    PRESC_MODE_send='VWC'
                elif  PRESC_MODE=='Weather_Station':
                    PRESC_MODE_send='ET0'

                Report_Agent=f"{LOTE};{CROP_DEFAULT}.CRO;{str(STAR_DATE)};{presc};{Kc};{Ks};{CONT_DAYS};{CONT_WEEK};{root_depth};{Taw};{Mae};{PRESC_MODE_send};{VWC};{deple};{date_report};{hour_report}"
                self.client.publish(f"Ag/SanRafael/Bloque_1/{NUM_LOTE}",f"{Report_Agent}",qos=2) 
                print('report')
                Fl_petp=False

            if Fl_Pres==True:
                
                hour_now=[datetime.now().hour,datetime.now().minute]
                #print(str(HOUR_IRRIG))
                #hour_now=HOUR_IRRIG
                if hour_now==HOUR_IRRIG:
                    #print(".")
                    if Fl_Irr==True:
                        Irr_time=presc/IRR_SPEED
                        print("enviar riego: "+str(presc))
                        self.Send_irr_order(CONT_DAYS,"NO",Path_Data+"/History_Data.txt",Irr_time)
                        self.FB.refIrrig_aplied.set(presc)
                        Fl_Irr=False
                        Fl_Pres=False
                    elif Fl_IrrN==True:    
                        Irr_time=NEW_PRESC/IRR_SPEED
                        print("enviar riego: "+str(Irr_time))
                        self.Send_irr_order(CONT_DAYS,"SI",Path_Data+"/History_Data.txt",Irr_time)
                        self.FB.refIrrig_aplied.set(NEW_PRESC)
                        Fl_IrrN=False
                        Fl_Pres=False
                    else:
                        pass

                   
    def Send_irr_order(self,day,neg,dir_file,presc):
        global CONT_DAYS,Fl_Pres,Fl_Irr,Fl_IrrN,Xbees_properties,AGENT
        try:             
            print(".....................")
            print("...enviando riego...")
            print('device', device) 
            remote_device=RemoteXBeeDevice(device,XBee64BitAddress.from_hex_string(Xbees_properties[AGENT][0]))     
            device.send_data(remote_device,'SITASK;'+'1;'+str(presc))
        
        except:
            remote_device=RemoteXBeeDevice(device,XBee64BitAddress.from_hex_string(Xbees_properties[AGENT][0]))     
            device.send_data(remote_device,'SITASK;'+'1;'+str(presc))
            print('Troubles in the communication')
            #device.close()

                
        file_HiD= open(dir_file, 'a',errors='ignore')
        file_HiD.write(f"{day};{neg};$;")
        file_HiD.close()    
        Fl_Irr=False 
        Fl_petp=False   
        Fl_Pres=False

    def Moisture_Sensor_Presc(self,n):
        global PWP,CROP_DEFAULT,Sens_Lev,FIELD_CAPACITY  
        crop=CROP_DEFAULT    
        PWP=PWP #punto de marchitez  
        Kc=self.f_cropcoeff(n,crop)
        sp_rootdepth,sp_mae=self.rootDepth(n,crop) 

        L1=Sens_Lev[crop][0]
        L2=Sens_Lev[crop][1] 
        L3=Sens_Lev[crop][1] 
        L4=Sens_Lev[crop][1] 

        file_SeD= open(Path_Data+'/Sensors_Data.txt', 'r',errors='ignore')
        data = file_SeD.read().splitlines()
        WC1=float(data[-1].split(';')[2]) 
        WC2=float(data[-1].split(';')[3]) 
        WC3=float(data[-1].split(';')[4]) 
        WC4=float(data[-1].split(';')[5])     
        file_SeD.close
 
        if sp_rootdepth <=  L1:
            deficit=(FIELD_CAPACITY-WC1)*(sp_rootdepth/100)*1000
            d_TAW=((FIELD_CAPACITY-PWP)/100)*sp_rootdepth*1000
        elif (sp_rootdepth > L1) and (sp_rootdepth<=L2):  
            deficit=(((FIELD_CAPACITY-WC1)*(L1/100))+((FIELD_CAPACITY-WC2)*((sp_rootdepth-L1)/100)))*1000
            d_TAW=((FIELD_CAPACITY-PWP)/100)*L1*1000  + ((FIELD_CAPACITY-PWP)/100)*(sp_rootdepth-L1)*1000

        deficit=round(deficit,4)  
        if deficit<0:
            deficit=0
        else:
            pass    
        d_MAD=d_TAW*sp_mae  
        if  deficit>= d_MAD:   
            irr_pres_net = deficit # (mm)
        else:
            irr_pres_net =0.0
        if n>=130 and crop=='Onion':
            irr_pres_net=0.0
        
        
        today = str(datetime.now()).split()[0]
        hour  = str(datetime.now()).split()[1]

        file_HiD= open(Path_Data+"/History_Data.txt", 'a',errors='ignore')
        file_HiD.write(f"Moisture_Sensors;{today};{hour};{irr_pres_net};{deficit};{Kc};{sp_rootdepth};{d_TAW};{0};{0};{0};{0};") 
        #las ultimas 4 no aplican para este metodo de prescripcion
        file_HiD.close()
        return irr_pres_net

    def Weather_Station_presc(self,n):

        global PWP,CROP_DEFAULT,FIELD_CAPACITY   
        crop=CROP_DEFAULT    
        PWP=PWP #punto de marchitez  
        Kc=self.f_cropcoeff(n,crop)
        sp_rootdepth,sp_mae=self.rootDepth(n,crop) 
        file_met= open('Req_data_met.txt', 'r',errors='ignore')
        data = file_met.read().splitlines()
        EToD=float(data[-1].split(";")[2])
        RainD=float(data[-1].split(";")[3])
        TeMax=float(data[-1].split(";")[4])
        TeMin=float(data[-1].split(";")[5])
        file_met.close
        ETc=EToD*Kc #ETC

        if n!=0:
            file_HiD= open(Path_Data+"/History_Data.txt", 'r',errors='ignore')
            data = file_HiD.read().splitlines()
            Irr=float(data[-1].split(';')[3]) #toma el riego de el dia anterior
            depl=float(data[-1].split(';')[4])  #toma la deplecion de el dia anterior  cuento ha disminuido 
            file_HiD.close
        else:
            Irr=0		
            depl=0

        if RainD!=0:
            ET_rain=ET/rainD #lluvia efectiva
            k=1.011*math.exp(-0.001143*ET_rain)-1.011*math.exp(-0.5208*ET_rain)
        else:
            k=0.0  
        eff_
        rain=RainD*k
                                                       
        d_TAW=((FIELD_CAPACITY -PWP)/100)*sp_rootdepth*1000  #conversion a metros
        d_MAD=d_TAW*sp_mae  #coeficiente 
        ETcadj=Ks*ETc  #etc ajustado	

        if  Irr + eff_rain > depl+ETc:            
            deficit = 0.0
        else:
            deficit = (depl - Irr - eff_rain + ETc)
        if deficit<0:
            deficit=0.0
        else:
            pass    
        if  deficit>= d_MAD:
            irr_pres_net = depl - Irr - eff_rain + ETc # (mm)             
        else:
            irr_pres_net=0.0
        if n>=130 and crop=='Onion' : #se deja de regar 20 dias antes 
            irr_pres_net=0.0    
        
        depl=deficit
        ks= (d_TAW-depl)/(d_TAW*(1-sp_mae))

        today = str(datetime.now()).split()[0]
        hour  = str(datetime.now()).split()[1]
        
        file_HiD= open(Path_Data+"/History_Data.txt", 'a',errors='ignore')
        file_HiD.write(f"Moisture_Sensors;{today};{hour};{irr_pres_net};{deficit};{Kc};{sp_rootdepth};{d_TAW};{d_MAD};{Ks};{ETcadj};{eff_rain};{ETc};")
        file_HiD.close()    

        return irr_pres_net

    def Fuzzy_Metod_Presc(self,Moisture_A,Temperature_A,Radiation_A):
        Moisture = ctrl.Antecedent(np.arange(0, 52.56, 1), 'Moisture')  #  (np.arange(0, 60, 1), 'Moisture')
        Temperature = ctrl.Antecedent(np.arange(0, 25, 1), 'Temperature')
        Radiation = ctrl.Antecedent(np.arange(0, 3500, 1), 'Radiation')
        IrrTime = ctrl.Consequent(np.arange(0, 32, 1), 'IrrTime')

        Moisture['LowM'] = fuzz.trapmf(Moisture.universe, [-20, -20, 15.0, 30.0])   # [-20, -20, 15.92, 36.60])
        Moisture['MediumM'] = fuzz.trimf(Moisture.universe, [15, 30, 45])    # [15.92, 36.60, 52.56])
        Moisture['HighM'] = fuzz.trapmf(Moisture.universe, [30, 45, 65, 65])    # [36.60, 52.56, 65, 65])

        Temperature['LowT'] = fuzz.trapmf(Temperature.universe, [- 2, -2, 10, 15])
        Temperature['MediumT'] = fuzz.trimf(Temperature.universe, [10, 15, 20])
        Temperature['HighT'] = fuzz.trapmf(Temperature.universe, [15, 20, 25, 25])

        Radiation['LowR'] = fuzz.trapmf(Radiation.universe, [-10, -10, 10, 200])
        Radiation['MediumR'] = fuzz.trapmf(Radiation.universe, [10, 200, 1000, 1400])
        Radiation['HighR'] = fuzz.trapmf(Radiation.universe, [1000, 1400, 3550, 3550])

        IrrTime['Nothing'] = fuzz.trapmf(IrrTime.universe, [-20, -20, 0, 8])
        IrrTime['VeryLittle'] = fuzz.trimf(IrrTime.universe, [0, 8, 16])
        IrrTime['Little'] = fuzz.trimf(IrrTime.universe, [8, 16, 24])
        IrrTime['Long'] = fuzz.trimf(IrrTime.universe, [16, 24, 32])
        IrrTime['VeryLong'] = fuzz.trapmf(IrrTime.universe, [24, 32, 40, 40])

        rule1 = ctrl.Rule(Moisture['LowM'] & Temperature['LowT'] & Radiation['LowR'], IrrTime['VeryLong'])
        rule2 = ctrl.Rule(Moisture['LowM'] & Temperature['LowT'] & Radiation['MediumR'], IrrTime['VeryLong'])
        rule3 = ctrl.Rule(Moisture['LowM'] & Temperature['LowT'] & Radiation['HighR'], IrrTime['VeryLong'])
        rule4 = ctrl.Rule(Moisture['LowM'] & Temperature['MediumT'] & Radiation['LowR'], IrrTime['Long'])
        rule5 = ctrl.Rule(Moisture['LowM'] & Temperature['MediumT'] & Radiation['MediumR'], IrrTime['Long'])
        rule6 = ctrl.Rule(Moisture['LowM'] & Temperature['MediumT'] & Radiation['HighR'], IrrTime['Little'])
        rule7 = ctrl.Rule(Moisture['LowM'] & Temperature['HighT'] & Radiation['LowR'], IrrTime['VeryLong'])
        rule8 = ctrl.Rule(Moisture['LowM'] & Temperature['HighT'] & Radiation['MediumR'], IrrTime['VeryLittle'])
        rule9 = ctrl.Rule(Moisture['LowM'] & Temperature['HighT'] & Radiation['HighR'], IrrTime['Nothing'])
        rule10 = ctrl.Rule(Moisture['MediumM'] & Temperature['LowT'] & Radiation['LowR'], IrrTime['Little'])
        rule11 = ctrl.Rule(Moisture['MediumM'] & Temperature['LowT'] & Radiation['MediumR'], IrrTime['Little'])
        rule12 = ctrl.Rule(Moisture['MediumM'] & Temperature['LowT'] & Radiation['HighR'], IrrTime['Little'])
        rule13 = ctrl.Rule(Moisture['MediumM'] & Temperature['MediumT'] & Radiation['LowR'], IrrTime['Little'])
        rule14 = ctrl.Rule(Moisture['MediumM'] & Temperature['MediumT'] & Radiation['MediumR'], IrrTime['Little'])
        rule15 = ctrl.Rule(Moisture['MediumM'] & Temperature['MediumT'] & Radiation['HighR'], IrrTime['VeryLittle'])
        rule16 = ctrl.Rule(Moisture['MediumM'] & Temperature['HighT'] & Radiation['LowR'], IrrTime['Long'])
        rule17 = ctrl.Rule(Moisture['MediumM'] & Temperature['HighT'] & Radiation['MediumR'], IrrTime['VeryLittle'])
        rule18 = ctrl.Rule(Moisture['MediumM'] & Temperature['HighT'] & Radiation['HighR'], IrrTime['Nothing'])
        rule19 = ctrl.Rule(Moisture['HighM'] & Temperature['LowT'] & Radiation['LowR'], IrrTime['Nothing'])
        rule20 = ctrl.Rule(Moisture['HighM'] & Temperature['LowT'] & Radiation['MediumR'], IrrTime['Nothing'])
        rule21 = ctrl.Rule(Moisture['HighM'] & Temperature['LowT'] & Radiation['HighR'], IrrTime['Nothing'])
        rule22 = ctrl.Rule(Moisture['HighM'] & Temperature['MediumT'] & Radiation['LowR'], IrrTime['Nothing'])
        rule23 = ctrl.Rule(Moisture['HighM'] & Temperature['MediumT'] & Radiation['MediumR'], IrrTime['Nothing'])
        rule24 = ctrl.Rule(Moisture['HighM'] & Temperature['MediumT'] & Radiation['HighR'], IrrTime['Nothing'])
        rule25 = ctrl.Rule(Moisture['HighM'] & Temperature['HighT'] & Radiation['LowR'], IrrTime['Nothing'])
        rule26 = ctrl.Rule(Moisture['HighM'] & Temperature['HighT'] & Radiation['MediumR'], IrrTime['Nothing'])
        rule27 = ctrl.Rule(Moisture['HighM'] & Temperature['HighT'] & Radiation['HighR'], IrrTime['Nothing'])

        IrrTimeping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10, rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20, rule21, rule22, rule23, rule24, rule25, rule26, rule27])
        IrrTimeping = ctrl.ControlSystemSimulation(IrrTimeping_ctrl)
        #
        #
        ## Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
        ## Note: if you like passing many inputs all at once, use .inputs(dict_of_data)
        IrrTimeping.input['Moisture'] = Moisture_A
        IrrTimeping.input['Temperature'] = Temperature_A
        IrrTimeping.input['Radiation'] = Radiation_A

        IrrTimeping.compute()
        print (IrrTimeping.output['IrrTime'])
        return IrrTimeping.output['IrrTime']


    #fucnion para determinar el coeficionete de cultivo dependiendo del dia 
    def f_cropcoeff(self,day,model):
        global Crop,cropcoeff
        parameters=Crop[model]
        if model=='Onion':
            temp=0
            for i in range(len(cropcoeff)):
                for j in range (7):
                    if day+1==temp:
                        Kc=cropcoeff[i]
                        return Kc
                    temp=temp+1    
        d_1=parameters[0]
        d_2=parameters[1]
        d_3=parameters[2]
        d_4=parameters[3]
        Kc_ini=parameters[4]
        Kc_mid=parameters[5]
        Kc_end=parameters[6]
        Kc=0
        if day<=d_1:
            Kc=Kc_ini
        elif day>d_1 and day<= (d_1+d_2):
            m=(Kc_mid-Kc_ini)/d_2
            Kc=m*(day-d_1)+Kc_ini
        elif day>d_1+d_2 and day<= (d_1+d_2+d_3):
            Kc=Kc_mid
        elif day> (d_1+d_2+d_3) and day<= (d_1+d_2+d_3+d_4):
            m=(Kc_end-Kc_mid)/d_4
            Kc=m*(day-(d_1+d_2+d_3))+Kc_mid
        return Kc 

    def rootDepth(self,t,crop_s):
        global Crop 
        z0=Crop[crop_s][7]
        zx=Crop[crop_s][8]
        t0=Crop[crop_s][9]
        tx=Crop[crop_s][10]
        mad=Crop[crop_s][11]
        nn=1
        z=z0+(zx-z0) *(((t-(t0/2))/(tx-(t0/2)))**(1/nn))   
        z=z.real
        if z>=zx:
            z=zx 
        elif z<=0:
            z=0.0001
        return z,mad 



#clase de sensores
class Sens_Data():
    def __init__(self): 
        self._running = True
    def terminate(self): 
        self._running = False    
    def run(self): 
        global device
        self.xbee_data() 
    def xbee_data(self):
        global device
        try: 
            device.add_data_received_callback(self.data_receive_callback)
            print("Waiting for data...\n")
            input()
        finally:                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               
            if device is not None and device.is_open():
                device.close()     

    def data_receive_callback(self, xbee_message):
        global flag_seD,Fl_Irr_Conf


        source=xbee_message.remote_device.get_64bit_addr()
        source1=str(source)  
        message=str(xbee_message.data.decode())
        print(str(datetime.now()).split()[1])
        print(str(xbee_message.data.decode()))
        message=message.split(":")
        if message[0]=="IRRIG":
            print(message[1])   
            if message[1].split(";")[0]=="COMPLETE":
                print("END IRRIGATION ")
                dir_file=Path_Data+"/History_Data.txt"
                valve=str(message[1].split(";")[1])
                time_apl=str(message[1].split(";")[2])   #time en seconds
                Sensor_pulses=float(message[1].split(";")[3].replace('\x00',''))
                End_H_Ap=[datetime.now().hour,datetime.now().minute]
                file_HiD= open(dir_file, 'a',errors='ignore')
                file_HiD.write(f"{End_H_Ap[0]}:{End_H_Ap[1]};{valve};{time_apl};{Sensor_pulses};#\n")
                file_HiD.close()

            else:
                print("IRRIGATION START")
                dir_file=Path_Data+"/History_Data.txt"
                hour_Irr=[datetime.now().hour,datetime.now().minute]
                file_HiD= open(dir_file, 'a',errors='ignore')
                file_HiD.write(f"{hour_Irr[0]}:{hour_Irr[1]};")
                file_HiD.close()
                

        elif message[0]=="SENSORS":
                WCs=[float(message[1].split(";")[0]),float(message[1].split(";")[1]),
                float(message[1].split(";")[2]),float(message[1].split(";")[3])]
                Relative_Hum=float(message[1].split(";")[4])
                Canopy_Tem=float(message[1].split(";")[5])
                Relative_Tem=float(message[1].split(";")[6])

                Hour_Rc=str(datetime.now()).split()[1]
                Date_Rc=str(datetime.now()).split()[0]
                for i in range(len(WCs)):
                    #falta definir la curva de sensores calibrada
                    WCs[i]=round(((WCs[i]*100)/1023),2)

                dir_file=Path_Data+"/Sensors_Data.txt"
                file_HiD= open(dir_file, 'a',errors='ignore')                
                file_HiD.write(f"{Date_Rc};{Hour_Rc};{WCs[0]};{WCs[1]};{WCs[2]};{WCs[3]};{Relative_Hum};{Canopy_Tem};{Relative_Tem};\n")
                file_HiD.close()  

                


def main():
    print ('START !')
    PS= PumpStation()
    time.sleep(5)
    subproces_PrincF=Thread(target=PS.Princip_Funcion)
    subproces_PrincF.start()
    while True:
        pass
    #signal.pause()


if __name__ == '__main__':
    main()
sys.exit(0)


