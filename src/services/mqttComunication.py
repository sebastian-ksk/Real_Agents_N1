import paho.mqtt.client
#import src.util.globalVariables as gb



class MqttComunication():  
    FlagAuth = False 
    def __init__(self):
        self.nameClient='Real_Agent'
        self.client =paho.mqtt.client.Client(client_id=self.nameClient)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host='104.248.53.140', port=1883)
        self.client.username_pw_set( "agent" ,  password = "789.123" ) 
        self.client.loop_start()

    #------------------------FUNCIONES MQTT-----------------------------------
    def on_connect(self,client, userdata, flags, rc):
        print('connected (%s)' % client._client_id)
        self.client.subscribe(topic='PmS/SanRafael/Ag', qos=0)
        self.client.unsubscribe("Ag/#")

    def on_message(self,client, userdata, message):
        #global FlagAuth 
        #global Date_R,Fl_Irr,Fl_IrrN,NEW_PRESC,Fl_petp
        self.data=str(message.payload).split("'")[1].split(":")  #split mensaje con ":"
        self.topic=str(message.topic).split("/")[0]

        if self.topic=="PmS":
            print(f'bandera mqtt {self.FlagAuth}' )
            self.FlagAuth = True
            #print(self.Authorization)
            print('------------------------------')
            print('received: ')
            print('topic: %s' % message.topic)
            print('payload: %s' % message.payload)
            print('qos: %d' % message.qos)
            # if data[0]=="Rp":                               #si el mensaje inicia como Rp 
            #     Date_R=data[1].split(';')[0]     
            #     today = str(date.today()).split()[0]         
            #     print(Date_R)
            #     if Date_R== today:
            #         Fl_petp=True                                #se activa bandera de peticcion   
            # elif data[0]=="Irr":                            #si el mensaje inicia como Irr=Riego    
            #     if data[1]=="Cont":                         #si la accion es continuar    
            #         Fl_Irr=True                             #activa bandera de reigo por prescripcion local
            #     elif data[1].split(";")[0]=="Neg":          #si es Neg
            #         if  NUM_LOTE== int(data[1].split(";")[1]):
            #             NEW_PRESC=int(data[1].split(";")[2])      #se guarda el dato del nuevo valor de prescipcion 
            #             Fl_IrrN=True                            #se activa bandera de riego por negociacion
            #     pass 
