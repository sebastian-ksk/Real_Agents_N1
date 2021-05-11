from datetime import datetime, date, time, timedelta

class PrescriptionResults():
    def __init__(self,PrescriptionMethod,date,hour,irr_pres_net,deficit,Kc,sp_rootdepth,dTaw,mad,Ks,ETcadj,eff_rain,ETc ):
        self._PrescriptionMethod = PrescriptionMethod
        self._date = date
        self._hour = hour
        self._irr_pres_net = irr_pres_net
        self._deficit = deficit
        self._Kc = Kc
        self._sp_rootdepth = sp_rootdepth
        self._dTaw = dTaw
        self._mad = mad
        self._Ks = Ks
        self._ETcadj = ETcadj
        self._eff_rain = eff_rain
        self._ETc = ETc  
        self.__allDataPrescription = [self._PrescriptionMethod,self._date,self._hour,self._irr_pres_net,self._deficit,self._Kc,self._sp_rootdepth,self._dTaw,self._mad,self._Ks,self._ETcadj,self._eff_rain,self._ETc ]

    @property
    def allDataPrescription(self):
        return self.__allDataPrescription

    @allDataPrescription.setter
    def allDataPrescription(self,alldataPrescription):
        self.__allDataPrescription = alldataPrescription
