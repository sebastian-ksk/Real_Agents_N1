from datetime import datetime, date, time, timedelta
class Crop():

    def __init__(self, crop,prescMode,prescription,dateInit,IrrigHour,PrescriptionHour):
        self._Cropcoef={"Maize": [25,37,40,30,   0.30,1.2,0.5,   0,0.4572,    5,108,0.55 ],
        "Potato":      [25,30,36,30,   0.5,1.15,0.75,  0,0.3048,     6,100,0.25],
        "Tomato":      [25,30,30,25,   0.60,1.15,0.8,  0.04,0.3048,  7,55,0.50],
        "Barley":      [40,60,60,40,   0.30,1.15,0.25, 0,0.498,      11,93,0.55],
        "Wheat":       [40,60,60,37,   0.30,1.15,0.4,  0,0.519,      14,60,0.55],
        "Quinoa":      [25,60,60,35,   0.30,1.2,0.5,   0,0.4645,     9,83,0.50],
        "Onion":       [21,42,49,38,   0.40,0.85,0.35, 0.04,0.165,   7,105,0.25]} 
        self._now=datetime.now()
        self._today = date(self._now.year,self._now.month,self._now.day)
        self.DateInit=dateInit
        self._daysCrop=abs(self._today-self.DateInit).days
        self._weeksCrop=int(self._daysCrop/7)+1
        self._crop=crop
        self._CropCoefient=self._Cropcoef[crop]
        self.__prescMode=prescMode
        self.__prescription=prescription
        self.IrrigHour=IrrigHour
        self.PrescriptionHour=PrescriptionHour
        
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

