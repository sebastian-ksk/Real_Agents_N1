from datetime import datetime, date, time, timedelta
class Crop():

    def __init__(self, crop,pwp,fieldCapacity,prescMode,prescription,dateInit,Irrighour,PrescHour):
        self._Cropcoef={"Maize": [25,37,40,30,   0.30,1.2,0.5,   0,0.4572,    5,108,0.55 ],
        "Potato":      [25,30,36,30,   0.5,1.15,0.75,  0,0.3048,     6,100,0.25],
        "Tomato":      [25,30,30,25,   0.60,1.15,0.8,  0.04,0.3048,  7,55,0.50],
        "Barley":      [40,60,60,40,   0.30,1.15,0.25, 0,0.498,      11,93,0.55],
        "Wheat":       [40,60,60,37,   0.30,1.15,0.4,  0,0.519,      14,60,0.55],
        "Quinoa":      [25,60,60,35,   0.30,1.2,0.5,   0,0.4645,     9,83,0.50],
        "Onion":       [0.36,0.36,0.39,0.43,0.43,0.43,0.53,0.59,0.77,0.77,0.8,
            0.9,0.73,0.66,0.7,0.6,0.34,0.36,0.35,0.35,0.35,0.35,0.35]} 
        self._now=datetime.now()
        self._today = date(self._now.year,self._now.month,self._now.day)
        self.__DateInit=dateInit
        self.__daysCrop=abs(self._today-self.__DateInit).days
        self._weeksCrop=int(self.__daysCrop/7)+1
        self.__crop=crop
        self._CropCoefient=self._Cropcoef[crop]
        self.__prescMode=prescMode
        self.__prescription=prescription
        self.__IrrigHour=Irrighour
        self.__PrescriptionHour=PrescHour
        self.__pwp = pwp
        self.__fieldCapacity=fieldCapacity


    @property
    def pointWp(self):
        return self.__pwp

    @pointWp.setter
    def pointWp(self,point):
        self.__pwp = point   

    @property
    def FieldCap(self):
        return self.__fieldCapacity

    @FieldCap.setter
    def FieldCap(self,FC):
        self.__fieldCapacity = FC

    @property
    def typeCrop(self):
        return self.__crop

    @typeCrop.setter
    def typeCrop(self,typecrop):
        self.__crop = typecrop


    @property
    def seedTime(self):
        return self.__DateInit

    @seedTime.setter
    def seedTime(self,dateSeed):
        self.__DateInit = dateSeed

        
    @property
    def dayscrop(self):
        return self.__daysCrop

    @dayscrop.setter
    def dayscrop(self,daysCrop):
        self.__daysCrop = daysCrop

    @property
    def prescMode(self):
        return self.__prescMode

    @prescMode.setter
    def prescMode(self,prescMode):
        self.__prescMode = prescMode

    @property
    def prescription(self):
        return self.__prescription

    @prescription.setter
    def prescription(self,prescription):
        self.__prescription = prescription



    @property
    def irrigationtime(self):
        return self.__IrrigHour

    @irrigationtime.setter
    def irrigationtime(self,Irrigtime):
        self.__IrrigHour = Irrigtime        

    @property
    def presctime(self):
        return self.__PrescriptionHour

    @presctime.setter
    def presctime(self,Irrigtime):
        self.__PrescriptionHour = Irrigtime           
    


