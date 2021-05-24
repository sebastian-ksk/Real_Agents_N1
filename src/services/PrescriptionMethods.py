from datetime import datetime
import math 

class prescriptionMethods():
    def __init__(self,crop,sensors,prescriptionResult):
        self.pathStorage = '/home/pi/Desktop/Real_Agents_N1/src/storage/Prescription_History.txt'
        self.directoryWeatherStation = '/home/pi/Desktop/Real_Agents_N1/src/storage/WheatherStationData.txt'
        self.crop = crop
        self.sensors = sensors
        self.prescriptionResult = prescriptionResult
    #fucnion para determinar el coeficionete de cultivo dependiendo del dia 
    def f_cropcoeff(self,day,model,cropCoefficients):
        if model=='Onion':
            self.temp=0
            for self.i in range(len(cropCoefficients)):
                for self.j in range (7):
                    if day+1==self.temp:
                        self.Kc=cropCoefficients[self.i]
                    self.temp=+1 
        else:          
            self.d_1,self.d_2,self.d_3,self.d_4=cropCoefficients[0],cropCoefficients[1],cropCoefficients[2],cropCoefficients[3]
            self.Kc_ini,self.Kc_mid,self.Kc_end=cropCoefficients[4],cropCoefficients[5],cropCoefficients[6]
            self.Kc=0
            if day<=self.d_1:
                self.Kc=self.Kc_ini
            elif day>self.d_1 and day<= (self.d_1+self.d_2):
                self.m=(self.Kc_mid-self.Kc_ini)/self.d_2
                self.Kc=self.m*(day-self.d_1)+self.Kc_ini
            elif day>self.d_1+self.d_2 and day<= (self.d_1+self.d_2+self.d_3):
                self.Kc=self.Kc_mid
            elif day> (self.d_1+self.d_2+self.d_3) and day<= (self.d_1+self.d_2+self.d_3+self.d_4):
                self.m=(self.Kc_end-self.Kc_mid)/self.d_4
                self.Kc=self.m*(day-(self.d_1+self.d_1+self.d_3))+self.Kc_mid
        return self.Kc 

    def rootDepth(self,days,cropCoefficients):
        self.Zo,self.Zx,self.to,self.tx,self.mad=cropCoefficients[7],cropCoefficients[8],cropCoefficients[9],cropCoefficients[10],cropCoefficients[11]
        self.nn=1
        self.z=self.Zo+(self.Zx-self.Zo) *(((days-(self.to/2))/(self.tx-(self.to/2)))**(1/self.nn))   
        self.z=self.z.real
        if self.z>=self.Zx:
            self.z=self.Zx 
        elif self.z<=0:
            self.z=0.0001
        return self.z,self.mad     

    def saveDataPrescription(self,directory,message):
        self.dir_file = directory
        self.SaveData = str(message).split('[')[1].split(']')[0].replace(',',';').replace("'",'')
        self.SaveFile = open(self.dir_file, 'a',errors='ignore')
        self.SaveFile.write(f'{self.SaveData};\n')
        self.SaveFile.close()


    def Moisture_Sensor_Presc(self):
        self.Levels = self.sensors._SensorsLevels
        self.pwp=self.crop.pointWp #punto de marchitez  
        self.fieldCapacity = self.crop.FieldCap
        self.Kc=self.f_cropcoeff(self.crop.dayscrop,self.crop.typeCrop ,self.crop._CropCoefient)
        self.sp_rootdepth,self.sp_mae=self.rootDepth(self.crop.dayscrop,self.crop._CropCoefient ) 
        self.L1,self.L2,self.L3,self.L4=self.Levels[0],self.Levels[1],self.Levels[1],self.Levels[1] 
        self.WC1,self.WC2,self.WC3,self.WC4=self.sensors.allSensors[0:4]
        if self.sp_rootdepth <=  self.L1:
            self.deficit=(self.fieldCapacity-self.WC1)*(self.sp_rootdepth/100)*1000
            self.dTaw=((self.fieldCapacity-self.pwp)/100)*self.sp_rootdepth*1000
        elif (self.sp_rootdepth > self.L1) and (self.sp_rootdepth<=self.L2):  
            self.deficit=(((self.fieldCapacity-self.WC1)*(self.L1/100))+((self.fieldCapacity-self.WC2)*((self.sp_rootdepth-self.L1)/100)))*1000
            self.dTaw=((self.fieldCapacity-self.pwp)/100)*self.L1*1000  + ((self.fieldCapacity-self.pwp)/100)*(self.sp_rootdepth-self.L1)*1000
        self.deficit=round(self.deficit,4)  
        if self.deficit<0:
           self.deficit=0
        else:
            pass    
        self.mad=self.dTaw*self.sp_mae  
        if self.deficit>= self.mad:   
            self.irr_pres_net =self.deficit # (mm)
        else:
            self.irr_pres_net =0.0
        if self.crop.dayscrop >=130 and self.crop.typeCrop=='Onion':
            self.irr_pres_net=0.0
       
        today = str(datetime.now()).split()[0]
        hour  = str(datetime.now()).split()[1]
        self.prescriptionResult.allDataPrescription = ['VWC-Moisture_Sensor_Presc',today,hour,self.irr_pres_net,self.deficit,self.Kc,self.sp_rootdepth,self.dTaw,0,0,0,0,0]
        self.saveDataPrescription(self.pathStorage,self.prescriptionResult.allDataPrescription)

        return self.irr_pres_net

    def Weather_Station_presc(self,daysCrop):  
        self.pwp=self.crop.pointWp #punto de marchitez  
        self.fieldCapacity = self.crop.FieldCap
        self.Kc=self.f_cropcoeff(self.crop.dayscrop,self.crop.typeCrop ,self.crop._CropCoefient)
        self.sp_rootdepth,self.sp_mae=self.rootDepth(self.crop.dayscrop,self.crop._CropCoefient )
        self.file_met= open(self.directoryWeatherStation, 'r',errors='ignore')
        self.file_met.close
        self.data = self.file_met.read().splitlines()
        self.EToD, self.RainD  = float(self.data[-1].split(";")[2]),float(self.data[-1].split(";")[3])
        self.TeMax ,self.TeMin = float(self.data[-1].split(";")[4]),float(self.data[-1].split(";")[2])
        self.ETc=self.EToD*self.Kc #self.ETc
        if daysCrop != 0:
            self.file_HiD= open(self.pathStorage, 'r',errors='ignore')
            self.data = self.file_HiD.read().splitlines()
            self.file_HiD.close
            self.Irrigation=float(self.data[-1].split(';')[3]) #toma el riego de el dia anterior
            self.depletion=float(self.data[-1].split(';')[4])  #toma la self.depletionecion de el dia anterior  cuento ha disminuido 
            
        else:
            self.Irrigation=0		
            self.depletion=0

        if self.RainD!=0:
            self.ET_Rain=self.ET/self.RainD #lluvia efectiva
            self.k=1.011*math.exp(-0.001143*self.ET_Rain)-1.011*math.exp(-0.5208*self.ET_Rain)
        else:
            self.k=0.0  

        self.effectiveRain=self.RainD*self.k
                                                        
        self.dTaw=((self.fieldCapacity -self.pwp)/100)*self.sp_rootdepth*1000  #conversion a metros
        self.mad=self.dTaw*self.sp_mae  #coeficiente 
        self.Ks= (self.dTaw-self.depletion)/(self.dTaw*(1-self.sp_mae))
        self.ETcadj=self.Ks*self.ETc  #self.ETc ajustado	

        if  self.Irrigation + self.effectiveRain > self.depletion+self.ETc:            
            self.deficit = 0.0
        else:
            self.deficit = (self.depletion - self.Irrigation - self.effectiveRain + self.ETc)
        if self.deficit<0:
            self.deficit=0.0
        else:
            pass    
        if self.deficit>= self.mad:
            self.Irrigation_pres_net = self.depletion - self.Irrigation - self.effectiveRain + self.ETc # (mm)             
        else:
            self.Irrigation_pres_net=0.0

        if self.crop.dayscrop >=130 and self.crop.typeCrop=='Onion':
            self.irr_pres_net=0.0   
        
        self.depletion=self.deficit
        self._today, self._hour = str(datetime.now()).split()[0],str(datetime.now()).split()[1]
        self.prescriptionResult.allDataPrescription = ['ET0-Moisture_Sensors',self._today,self._hour,self.irr_pres_net,self.deficit,
        self.Kc,self.sp_rootdepth,self.dTaw,self.mad,self.Ks,self.ETcadj,self.effectiveRain,self.ETc]
        self.saveDataPrescription(self.pathStorage,self.prescriptionResult.allDataPrescription) 
        return self.Irrigation_pres_net
