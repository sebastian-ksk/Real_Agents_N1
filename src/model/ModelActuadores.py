from datetime import datetime

class Actuators:

    def __init__(self, numberValvs,directionXbee):
        self._directionXbee=directionXbee
        self._StateValv_1=False  
        self._StateValv_2=False
        self._timeValv_1=0
        self._timeValv_2=0
        self.__timeReport = datetime.now()
        
    @property
    def timeReport(self):
        return self.__timeReport

    @timeReport.setter
    def prescMode(self,timeReport):
        self.__timeReport = timeReport

    @property
    def StateValv_1(self):
        return self.__StateValv_1

    @StateValv_1.setter
    def StateValv_1(self,StateValv_1):
        self.__StateValv_1= StateValv_1    

    @property
    def StateValv_2(self):
        return self.__StateValv_2

    @StateValv_1.setter
    def StateValv_1(self,StateValv_2):
        self.__StateValv_2= StateValv_2   

    @property
    def timeValv_1(self):
        return self.__timeValv_1

    @timeValv_1.setter
    def timeValv_1(self,timeValv_1):
        self.__timeValv_1= timeValv_1

    @property
    def timeValv_2(self):
        return self.__timeValv_2

    @timeValv_2.setter
    def timeValv_2(self,timeValv_2):
        self.__timeValv_2 = timeValv_2         