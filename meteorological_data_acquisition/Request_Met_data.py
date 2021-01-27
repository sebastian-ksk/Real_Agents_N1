import urllib.request, json 
import sys

with urllib.request.urlopen("http://104.248.53.140/SeverGet.php/?hour=1") as url:
    data = json.loads(url.read().decode())
    file=open('/home/pi/Desktop/Agent_N1/Data/Req_data_met.txt','a')  
    for i in range(4):    
        fecha=str(data[i]["Seedtime"]).split()[0]
        hora=str(data[i]["Seedtime"]).split()[1]
        EToD=str(data[i]["ET_daily"])
        RainD=str(data[i]["Rain_daily"])
        TeMax=str(data[i]["Temperature_Max"])
        TeMin=str(data[i]["Temperature_Min"])
        print(fecha+';'+hora+';'+EToD+';'+RainD+';'+TeMax+';'+TeMin+';\n') 
        file.write(fecha+';'+hora+';'+EToD+';'+RainD+';'+TeMax+';'+TeMin+';\n')
    file.close()