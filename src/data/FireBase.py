#=======LIBRERIAS DELSDK PARA EL ACCESO A LOS DATOS DE firebase DESDE EL MODULO ADMINISTRADOR
import firebase_admin 
from firebase_admin import credentials #ACCESO A LAS LLAVES PRIVADAS DEL MODULO DE ADMIN O DATOS DE ALMACVENAMIENTO
from firebase_admin import db  #ACCESO A LA BASE DE DATOS
from firebase_admin import firestore  #ACCESO A LA BASE DE DATOS
import threading
from datetime import datetime, date, time, timedelta

'''https://googleapis.dev/python/firestore/latest/document.html'''

class FIREBASE_CLASS():
    def __init__(self,AgentName,cropModel):
        self.cropModel = cropModel
        self.PathCredentials = '/home/pi/Desktop/Real_Agents_N1/src/data/ClaveFirebase.json'
        self.urlDatabase = 'https://manageragents-2a3f6-default-rtdb.firebaseio.com/'
        self.AgentName = AgentName
        cred=credentials.Certificate(self.PathCredentials)
        firebase_admin.initialize_app(cred,{
            'databaseURL': self.urlDatabase
        })  
        firestoreDb = firestore.client()
        self.doc_ref = firestoreDb.collection(u'Agents').document(u''+f'{self.AgentName}')

        doc = self.doc_ref.get()
        if doc.exists:
            self.completeModel = doc.to_dict()
            self.Crop = self.completeModel['Crop']
            self.Irrig_Presc = self.completeModel['Irrigation/Prescription']    
            #fecha de siembra/seed time
            self._dateseed = str(self.Crop['SeedDate']).split('/')
            self.cropModel.seedTime = date(int(self._dateseed[2]),int(self._dateseed[1]),int(self._dateseed[0]))
            #Crop/cultivo
            self.cropModel.typeCrop =  self.Crop['TypeCrop'] 
            #pwp
            self.cropModel.pointWp =  float(self.Crop['pwp'])
            #capacidad de campo / fiel capacity
            self.cropModel.FieldCap = float(self.Crop['field_capacity'])
            #riego-prescripcion/ irrigation-prescription
            self.cropModel.prescMode = self.Irrig_Presc['PrescriptionMethod']
            self.cropModel.presctime = self.Irrig_Presc['PrescriptionTime']
            self.cropModel.irrigationtime = self.Irrig_Presc['IrrigationTime']

        else:
            print(u'No such document!')
            self.doc_ref.set({
                u'Crop':{
                    u'TypeCrop' : '',
                    u'pwp' : 0,
                    u'field_capacity':0,
                    u'SeedDate': '0/0/0',
                },
                u'Irrigation/Prescription':{
                    u'IrrigationMethod': 'drip',
                    u'constanFlow': 1,
                    u'PrescriptionTime': '00:00',
                    u'IrrigationTime': '00:00',
                    u'PrescriptionMethod' : 'WeatherStation',
                    u'manualValves' : "OFF"
                },
                u'ResultsIrrig/Prescript':{
                    u'PrescriptionData':{
                        u'LastPrescriptionDate': '0/0/0/',
                        u'NetPrescription':0
                    },
                    u'IrrigationData': {
                        u'LastIrrigationDate': '0/0/0/',
                        u'irrigationApplied' : 0,
                        u'IrrigationState' : 'off'
                    },
                u'SensorsStaus': {
                    u'VWC1' :00,
                    u'VWC1' :00,
                    u'VWC1' :00,
                    u'VWC1' :00,
                    u'temperature' :00,
                    u'CanopyTemperature':00,
                    u'RH' : 00
                }    
                }
            })
        
    

        #changes to movil APP
        self.docRefview = firestoreDb.collection(u'Agents').document(u''+f'{self.AgentName}')
        self.IrrigationPrescription = self.docRefview.get().to_dict()['Irrigation/Prescription']
        self.callback_done = threading.Event() 
        doc_watch = self.docRefview.on_snapshot(self.on_snapshot) 

    def on_snapshot(self,doc_snapshot, changes, read_time):
        for change in changes:
            if change.type.name == 'ADDED':
                pass
            elif change.type.name == 'MODIFIED':
                #print(f' paht: {change.document.to_dict()}')
                self.changeData = change.document.to_dict()
                print('change data ================== : ')
                self.compare(self.IrrigationPrescription,self.changeData['Irrigation/Prescription'])
                self.IrrigationPrescription = self.changeData['Irrigation/Prescription']
            elif change.type.name == 'REMOVED':
                pass
        self.callback_done.set()    


    def compare(self,first, second):
        self.sharedKeys = set(first.keys()).intersection(second.keys())
        for self.key in self.sharedKeys:
            if first[self.key] != second[self.key]:
                print("Key: {}, Value 1: {}, Value 2: {}".format(self.key, first[self.key], second[self.key]))  
                if (self.key == 'PrescriptionMethod') :
                    self.cropModel.prescMode  = second[self.key]
                elif (self.key == 'PrescriptionTime') :
                    self.cropModel.presctime = second[self.key] 
                elif (self.key == 'IrrigationTime') :
                    self.cropModel.irrigationtime  = second[self.key]     