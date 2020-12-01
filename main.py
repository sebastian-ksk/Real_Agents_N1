# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 23:19:10 2020
@author: sebca
"""
import sys
import paho.mqtt.client
from pathlib import Path
import os
import time
import datetime
import signal
from threading import Thread
from datetime import datetime,timedelta
from datetime import date
from datetime import time as tm
import random
from digi.xbee.devices import XBeeDevice, RemoteXBeeDevice,XBee64BitAddress,OperatingMode,RemoteATCommandPacket
import pandas as pd 
import math


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
CROP_DEFAULT='Onion'
PRESC_MODE='Moisture_Sensors'
STAR_DATE=date(2020,2,1)
CONT_DAYS=0

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

class PumpStation():
    def __init__(self): 
        global device
        
        self.Init_Menu()
        print(".......")
        
        self.client =paho.mqtt.client.Client(client_id='Real_Agent', clean_session=False)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host='104.248.53.140', port=1883)
        self.client.username_pw_set( "agent" ,  password = "789.123" ) 
        self.client.loop_start()
        
        self.SD= Sens_Data()
        self.subproces_Sens=Thread(target=self.SD.run)
        self.subproces_Sens.daemon=True
        self.subproces_Sens.start()

    #------------------------FUNCIONES MQTT-----------------------------------
    def on_connect(self,client, userdata, flags, rc):
        print('connected (%s)' % client._client_id)
        #suscripcion al agente Source
        self.client.subscribe(topic='Pump_prueba/SanRafael', qos=0)

    def on_message(self,client, userdata, message):
        global Date_R,Fl_Irr,Fl_IrrN,NEW_PRESC,Fl_petp
        print('------------------------------')
        print('topic: %s' % message.topic)
        print('payload: %s' % message.payload)
        print('qos: %d' % message.qos)
        data=str(message.payload).split("'")[1].split(":")
        if data[0]=="Rp":                               #si el mensaje inicia como Rp 
            Date_R=data[1]              
            print(Date_R)
            Fl_petp=True                                   
        elif data[0]=="Irr":                            #si el mensaje inicia como Irr=Riego    
            if data[1]=="Cont":                         #si la accion es continuar    
                Fl_Irr=True                             #activa bandera de reigo por prescripcion local
            elif data[1].split(";")[0]=="Neg":          #si es Neg
                lote=int(data[1].split(";")[1])-1       #lote es el numero enviado - 1 para que arreglo comience desde cero
                NEW_PRESC=data[1].split(";")[2]      #se guarda el dato del nuevo valor de prescipcion 
                Fl_IrrN=True                            #se activa bandera de riego por negociacion
            pass 

    def Init_Menu(self): 
        global PWP,STAR_DATE,CROP_DEFAULT   
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
            print("MES DE INCIIO: ", end="")
            month=input()
            print("AÑO DE INCIIO: ", end="")
            year=input()
            STAR_DATE=date(int(year),int(month),int(day))
            print("DAY START CROP: "+ str(STAR_DATE))
            print("MODO DE PRESCRIPCION")
            prespc={1:"Moisture_Sensors",2:"Weather_Station"}
            for i in range(len(prespc)):
                print(str(i+1)+". "+str(prespc[i+1]))
            print("INGRESE MODO DE PRESCIPCION: ", end="")
            sel=input()
            PRESC_MODE=prespc[int(sel)]
            print("INGRESE PUNTO DE MARCHITEZ PERMANENTE: ")
            PWP=float(input())
        except:
            print("error ingreso erroneo de datos....")
        return

    #------------------------------------------------------------------------- 
    def Princip_Funcion(self):
        global Date_R,Fl_Irr,Fl_IrrN,New_pr,Fl_petp,Fl_Pres
        global CROP_DEFAULT,PRESC_MODE,CONT_DAYS,NEW_PRESC
        global device
        print("init")

        while True:
            today = str(date.today()).split()[0]
            if(Date_R=="2020-11-03"):
                if Fl_Pres==False and Fl_petp==True:
                    if PRESC_MODE=='Moisture_Sensors':
                        presc=self.Moisture_Sensor_Presc(CONT_DAYS)
                    elif PRESC_MODE=='Weather_Station':            
                        presc=self.Weather_Station_presc(CONT_DAYS)
                        
                    print("prescripcion= "+str(presc))
                    self.client.publish("Ag/SanRafael/Block22","Rp:"+str(presc),qos=2) 
                    Fl_Pres=True 
                    
                if Fl_Pres==True:
                    if Fl_Irr==True:
                        print("enviar riego: "+str(presc))
                        self.Send_irr_order(CONT_DAYS,"NO","History_Data.txt",presc)
                        Fl_Irr=False

                    if Fl_IrrN==True:    
                        presc=NEW_PRESC
                        print("enviar riego: "+str(presc))
                        self.Send_irr_order(CONT_DAYS,"SI","History_Data_PS.txt",presc)

                        Fl_Irr=False

    def Send_irr_order(self,day,neg,dir_file,presc):
        global CONT_DAYS
        try:             
            print(".....................")
            print("...enviando riego...")
            print('device', device) 
            remote_device=RemoteXBeeDevice(device,XBee64BitAddress.from_hex_string('0013A20040BE17CE'))
            device.send_data(remote_device,'SITASK='+str(presc)+'; \n')
            file_HiD= open(dir_file, 'a',errors='ignore')
            file_HiD.write(neg+";"+str(datetime.now()).split()[1]+'\n')
            file_HiD.close()
            CONT_DAYS+=1

        except:
            print('Troubles in the communication')
            device.close()
        Fl_Irr=False 
        Fl_petp=False   
        Fl_Pres=False



    def Moisture_Sensor_Presc(self,n):
        global PWP,CROP_DEFAULT,Sens_Lev  
        crop=CROP_DEFAULT    
        pwp1010=PWP #punto de marchitez  
        Kc=self.f_cropcoeff(n,crop)
        sp_rootdepth,sp_mae=self.rootDepth(n,crop) 
        L1=Sens_Lev[crop][0]
        L2=Sens_Lev[crop][1] 
        L3=Sens_Lev[crop][1] 
        L4=Sens_Lev[crop][1] 

        file_SeD= open('Sensors_Data.txt', 'r',errors='ignore')
        data = file_SeD.read().splitlines()
        WC1=float(data[-1].split(';')[2]) 
        WC2=float(data[-1].split(';')[3]) 
        WC3=float(data[-1].split(';')[4]) 
        WC4=float(data[-1].split(';')[5])     
        file_SeD.close
 
        if sp_rootdepth <=  L1:
            deficit=(Kc-WC1)*(sp_rootdepth/100)*1000
            d_TAW=((Kc-pwp1010)/100)*sp_rootdepth*1000
        elif (sp_rootdepth >  L1) and  (sp_rootdepth <=  L2):  

            deficit= (    ( (Kc-WC1)*(L1/100) ) + ( (Kc-WC2) * ( (sp_rootdepth-L1)/100) )    )*1000
            d_TAW=((Kc-pwp1010)/100)*L1*1000    +     ((Kc-pwp1010)/100)*(sp_rootdepth-L1)*1000

        deficit=round(deficit,4)  
        if deficit<0:
            deficit=0
        d_MAD=d_TAW*sp_mae  
        if  deficit>= d_MAD:   
            irr_pres_net = deficit # (mm)
        else:
            irr_pres_net =0.0
        if n>=130 and crop=='Onion':
            irr_pres_net=0.0
        today = str(datetime.now()).split()[0]
        hour  = str(datetime.now()).split()[1]
        file_HiD= open('History_Data_PS.txt', 'a',errors='ignore')
        file_HiD.write(today+';'+hour+';'+str(irr_pres_net)+';'+str(deficit)+';'+
        str(Kc)+';'+str(sp_rootdepth)+';'+str(d_TAW)+';'+str(d_MAD)+'Moisture_Sensors;')
        file_HiD.close()
        return irr_pres_net


    def Weather_Station_presc(self,n):
        global PWP,CROP_DEFAULT   
        crop=CROP_DEFAULT    
        pwp1010=PWP #punto de marchitez  
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
            file_HiD= open('History_Data.txt', 'r',errors='ignore')
            data = file_HiD.read().splitlines()
            Irr=float(data[-1].split(';')[2]) #toma el riego de el dia anterior
            depl=float(data[-1].split(';')[3])  #toma la deplecion de el dia anterior  cuento ha disminuido 
            file_HiD.close
        else:
            Irr=0		
            depl=0

        if RainD!=0:
            ET_rain=ET/rainD #lluvia efectiva
            k=1.011*math.exp(-0.001143*ET_rain)-1.011*math.exp(-0.5208*ET_rain)
        else:
            k=0.0  
        eff_rain=RainD*k
        d_TAW=((Kc-pwp1010)/100)*sp_rootdepth*1000  #conversion a metros
        d_MAD=d_TAW*sp_mae  #coeficiente 
        Ks= (d_TAW-depl)/(d_TAW-sp_mae)
        ETcadj=Ks*ETc  #etc ajustado	
        if  Irr + eff_rain > depl+ETc:            
            deficit = 0.0
        else:
            deficit = (depl - Irr - eff_rain + ETc)
        if  deficit>= d_MAD:
            irr_pres_net = depl - Irr - eff_rain + ETc # (mm)             
        else:
            irr_pres_net=0.0
        if n>=130 and crop=='Onion' : #se deja de regar 20 dias antes 
            irr_pres_net=0.0
        today = str(datetime.now()).split()[0]
        hour  = str(datetime.now()).split()[1]
        file_HiD= open('History_Data.txt', 'a',errors='ignore')
        file_HiD.write(today+';'+hour+';'+str(irr_pres_net)+';'+str(deficit)+';'+
        str(Ks)+';'+str(ETcadj)+';'+str(eff_rain)+';'+str(ETc)+';'+str(Kc)+';'+
        str(sp_rootdepth)+';'+str(d_TAW)+';'+str(d_MAD)+';Weather_Station;')
        file_HiD.close()
        return irr_pres_net



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
        global flag_seD
        source=xbee_message.remote_device.get_64bit_addr()
        source1=str(source)  
        print(str(xbee_message.data.decode()))
        print(source)



def main():
    print ('START !')
    PS= PumpStation()
    time.sleep(10)
    subproces_PrincF=Thread(target=PS.Princip_Funcion)
    subproces_PrincF.start()




    while True:
        pass
    #signal.pause()


if __name__ == '__main__':
    main()
sys.exit(0)


