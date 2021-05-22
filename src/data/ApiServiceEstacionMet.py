"""=====================================================================================================================
 En este scrpit se plante  la consulta de los dastos metereologicos del servidor a traves del metodo get de protocolo http. 
 Esta consulta se realiza a la base de datos de waterlink.
 NOTA:
 >> Es necesario contener un token privado que se obtiene del servidsor privado.
 ========================================================================================================================
"""
import sys
import requests
import json
import urllib
import sys

from requests.models import Response

class ApiServiceEstacionMet():
    def __init__(self,modelWeather):
        self.url = "https://api.weatherlink.com/v1/NoaaExt.json?user=001D0A0117A4&pass=multiagent&apiToken=6BA678C3A1844C6B9B9767F9543331A1"
        self.modelWeather = modelWeather
        self.directory = '/home/pi/Desktop/Real_Agents_N1/src/storage/WheatherStationData.txt'
    '''=====================================================================================================================
            consulta de datos a las 12 de la noche para toma de datos diarios de la estacion
    =====================================================================================================================
    '''
    def request_station(self):
        try:
            self.payload={}
            self.headers = {}
            self.response = requests.request("GET", self.url, headers=self.headers, data=self.payload)
            return self.response.json()   

        except:
            print("ERROR EN ADQUISICION DE DATOS")    
            

    def checkStation(self):
        self.response = self.request_station()
        self.infoStation = self.modelWeather.from_dict(self.response)
        self.dir_file = self.directory
        self.SaveFile = open(self.dir_file, 'a',errors='ignore')
        self.SaveFile.write(f'{self.infoStation.date};{self.infoStation.hour};{self.infoStation.EToD};'+
        f'{self.infoStation.RainD};{self.infoStation.TeMax};{self.infoStation.TeMin} \n')
        self.SaveFile.close()
        print(self.infoStation)
        #return self.infoStation

