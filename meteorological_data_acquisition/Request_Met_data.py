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

Path_Data="/home/pi/Desktop/Real_Agents_N1/Data"
Path_Document='/Req_data_met.txt'

DID="001D0A0117A4"
ownerpass="multiagent"
tokenID="6BA678C3A1844C6B9B9767F9543331A1"
# api="https://api.weatherlink.com/v1/StationStatus.json?user="+DID+"&pass="+ownerpass+"&apiToken="+tokenID
api="https://api.weatherlink.com/v1/NoaaExt.json?user="+DID+"&pass="+ownerpass+"&apiToken="+tokenID

'''=====================================================================================================================
        consulta de datos a las 12 de la noche para toma de datos diarios de la estacion
   =====================================================================================================================
'''
def request_station():
    try:
        with urllib.request.urlopen(api) as Url_Data:
            Data_Json = json.loads(Url_Data.read().decode())
            fecha=str(Data_Json["observation_time"]).split(',')[0].split("on")[1]
            hora=str(Data_Json["observation_time"]).split(',')[1]
            observation_davis=Data_Json["davis_current_observation"]
            EToD=str(observation_davis["et_day"])
            RainD=str(observation_davis["rain_day_in"])
            TeMax=round((float(observation_davis["temp_day_high_f"])-32) * (5/9),2)
            TeMin=round((float(observation_davis["temp_day_low_f"])-32) * (5/9),2) 
            print("write.....")
            file=open(Path_Data+Path_Document,'a')
            print( f'{fecha};{hora};{EToD};{RainD};{TeMax};{TeMin};\n') 
            file.write(f'{fecha};{hora};{EToD};{RainD};{TeMax};{TeMin};\n')  
            file.close()
            print("write complete.....")
    except:
        print("ERROR EN ADQUISICION DE DATOS")    
        

def main():
    request_station()

if __name__ == '__main__':
    main()
 
sys.exit(0) 





# with urllib.request.urlopen("http://104.248.53.140/SeverGet.php/?hour=1") as url:
#     data = json.loads(url.read().decode())
#     file=open('/home/pi/Desktop/Agent_N1/Data/Req_data_met.txt','a')  
#     for i in range(4):    
#         fecha=str(data[i]["Seedtime"]).split()[0]
#         hora=str(data[i]["Seedtime"]).split()[1]
#         EToD=str(data[i]["ET_daily"])
#         RainD=str(data[i]["Rain_daily"])
#         TeMax=str(data[i]["Temperature_Max"])
#         TeMin=str(data[i]["Temperature_Min"])
#         print(fecha+';'+hora+';'+EToD+';'+RainD+';'+TeMax+';'+TeMin+';\n') 
#         file.write(fecha+';'+hora+';'+EToD+';'+RainD+';'+TeMax+';'+TeMin+';\n')
#     file.close()