from datetime import datetime

class Sensors:

    def __init__(self, crop,directionXbee):
        self._directionXbee=directionXbee
        self._Sens_Lev={
        "Maize":   [0.23,0.46,0.69,0.92,2.30],
        "Potato":  [0.15,0.31,0.45,0.61,1.50],
        "Tomato":  [0.15,0.31,0.45,0.61,1.00],
        "Barley":  [0.26,0.52,0.78,1.04,1.50],
        "Wheat":   [0.25,0.50,0.75,1.00,1.30],
        "Quinoa":  [0.23,0.47,0.69,0.92,1.00],
        "Onion":   [0.10,0.20,0.20,0.20,0.20]} 
        self._SensorsLevels=self._Sens_Lev[crop]
        self._SensorVwc_1=0
        self._SensorVwc_2=0
        self._SensorVwc_3=0
        self._SensorVwc_4=0
        self._TempR=0
        self._TempCanopy=0
        self._HumR=0
        self.__allSensors=[self._SensorVwc_1,self._SensorVwc_2,self._SensorVwc_3,self._SensorVwc_4,self._TempR, self._TempCanopy,self._HumR]
        self.__timeReport=datetime.now()


    @property
    def timeReport(self):
        return self.__timeReport

    @timeReport.setter
    def prescMode(self,timeReport):
        self.__timeReport = timeReport

    @property
    def allSensors(self):
        return self.__allSensors

    @allSensors.setter
    def allSensors(self,allSensors):
        self.__allSensors= allSensors