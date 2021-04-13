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




class ApiServiceEstacionMet():
    def __init__(self):
        print('init ')
        self.url = "https://api.weatherlink.com/v1/NoaaExt.json?user=001D0A0117A4&pass=multiagent&apiToken=6BA678C3A1844C6B9B9767F9543331A1"
    '''=====================================================================================================================
            consulta de datos a las 12 de la noche para toma de datos diarios de la estacion
    =====================================================================================================================
    '''
    def request_station(self):
        try:
            payload={}
            headers = {}
            print('get request')
            response = requests.request("GET", self.url, headers=headers, data=payload)
            return response.json()   

        except:
            print("ERROR EN ADQUISICION DE DATOS")    
            


