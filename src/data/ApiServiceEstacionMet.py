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
        # self.Path_Data="/home/pi/Desktop/Real_Agents_N1/Data"
        # self.Path_Document='/Req_data_met.txt'
        # self.DID="001D0A0117A4"
        # self.ownerpass="multiagent"
        # self.tokenID="6BA678C3A1844C6B9B9767F9543331A1"
        # # api="https://api.weatherlink.com/v1/StationStatus.json?user="+DID+"&pass="+ownerpass+"&apiToken="+tokenID
        # self.api="https://api.weatherlink.com/v1/NoaaExt.json?user="+self.DID+"&pass="+self.ownerpass+"&apiToken="+self.tokenID

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
            #print(response.text)    

            # with urllib.request.urlopen(self.api) as Url_Data:
            #     Data_Json = json.loads(Url_Data.read().decode())
        
            #     print("write.....")
                # file=open(Path_Data+Path_Document,'a')
                # print( f'{fecha};{hora};{EToD};{RainD};{TeMax};{TeMin};\n') 
                # file.write(f'{fecha};{hora};{EToD};{RainD};{TeMax};{TeMin};\n')  
                # file.close()
                # print("write complete.....")
            return response.json()   

        except:
            print("ERROR EN ADQUISICION DE DATOS")    
            


