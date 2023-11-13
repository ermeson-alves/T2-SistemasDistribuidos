import pika
import grpc
from protos import sis_dist_pb2
from protos import sis_dist_pb2_grpc
import threading
import time
import socket

#configurações do servidor TCP para comunicação com o cliente
TCP_SERVER_IP = 'localhost'
TCP_SERVER_PORT = 7578

#status dos atuadores, se estao ligados ou desligados
lampstatus = False
smokestatus = False
acstatus = False

#comando do cliente para o arcondicionado ligar (automaticamente) ou desligar
accommand = False

#comando do cliente para a lampada ligar (automaticamente) ou desligar
lampcommand = False

#temperatura alvo do arcondicionado
targettemp = 24

#comando para desativar o alarme de fumaça
#o comando é setado de volta para FALSE apos desligar o alarme
deactivatesmoke = False

#variaveis dos sensores
smoke = None
temperature = None
lumen = None

def rungrpc(host, on, temperatura):
    with grpc.insecure_channel(host) as channel:
        stub = sis_dist_pb2_grpc.AtuadorStub(channel)
        on_request = sis_dist_pb2.OnRequest(on=on, temperatura=temperatura)
        on_reply = stub.DeviceOn(on_request)
        print(on_reply)

#/////////////
#functions that will process the incomming transit from rabbitmq queue consumption
#/////////////

#Function to process temperature data
def TemperatureHandle(channel, method, properties, body):
        global temperature
        temperature = float(body)
        print(f"Received Temperature Data: {temperature:.2f}")

        global acstatus, targettemp, accommand
        print(targettemp)

        #automatic action of the home assistant
        if accommand:
            if temperature >= targettemp + 2:
                if not acstatus:
                    rungrpc('localhost:50053', True, targettemp)
                    acstatus = True
            elif temperature <= targettemp - 2:
                if acstatus:
                    rungrpc('localhost:50053', False, targettemp)
                    acstatus = False


#Function to process luminosity data
def LuminosityHandle(channel, method, properties, body):
    global lumen
    lumen = int(body) 
    print(f"Received Luminosity Data: {lumen}")

    global lampstatus, lampcommand

    #automatic action of the home assistant
    if lampcommand:
        if lampstatus:
            if lumen > 3400:
                rungrpc('localhost:50051', False, 1)
                lampstatus = False
        else:
            if lumen <= 1200:
                rungrpc('localhost:50051', True, 1)
                lampstatus = True

    else:
        if lampstatus:
            rungrpc('localhost:50051', False, 1)
            lampstatus = False


#Function to process smoke data
def SmokeHandle(channel, method, properties, body):
    global smoke
    if body.decode("utf-8") == 'True':
        smoke = True
    else:
        smoke = False
    print(f"Received Smoke Data: {smoke}")

    global smokestatus, deactivatesmoke

    if smoke:
        if not smokestatus:
            rungrpc('localhost:50052', True, 1)
            smokestatus = True

    if deactivatesmoke:
        rungrpc('localhost:50052', False, 1)
        deactivatesmoke = False
        smokestatus = False


def main():
    #Connection with rabbitmq server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    #dictionary mapping queue names to processingFunctions
    HandlequeueFunctions = {
        'TemperatureSensor': TemperatureHandle,
        'LuminositySensor': LuminosityHandle,
        'SmokeSensor': SmokeHandle,
    }

    #Declare queues and set up the respective callback functions | Subscribe
    for qname, processingFunction in HandlequeueFunctions.items():
        channel.queue_declare(queue=qname)
        channel.basic_consume(queue=qname, on_message_callback=processingFunction, auto_ack=True)


    print("Waiting...")
    channel.start_consuming()
    

#Comunicação com o cliente ===========================================================================================================================

def tcp_server(ip = TCP_SERVER_IP, port = TCP_SERVER_PORT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip, port))
    s.listen(1)
    print(f"TCP server listening in {TCP_SERVER_PORT} port...")
    while True:
        conn, addr = s.accept()
        data = conn.recv(65536).decode("utf-8")
        print(f"Client msgn: {data}") # [int] atuador
        # Enviar valores dos sensores:
        if data.split(' ')[0]=='[1]': 
            sensor_value = send_sensor_value(data.split(' ')[-1])
            conn.sendall(sensor_value.encode("utf-8"))

        # Ligar atuadores, via cliente:
        elif data.split(' ')[0] == '[2]':
            resp = ligar_atuador(data.split(' ')[-1])
            conn.sendall(resp.encode("utf-8"))

        # Desligar atuadores, via cliente:
        elif data.split(' ')[0] == '[3]':
            sensor_value = desligar_atuador(data.split(' ')[-1])
            conn.sendall(sensor_value.encode("utf-8"))
        # Mudar temp do ar-condicionado, via cliente:
        elif data.split(' ')[0] == '[4]':
            resp = set_temp(int(data.split(' ')[-2]))
            conn.sendall(resp.encode("utf-8"))
        # # Ligar atuadores, via cliente:
        # elif data.split(' ')[0] == '[2]':
        #     sensor_value = ligar_atuador(data.split(' ')[1])
        #     conn.sendall(sensor_value.encode("utf-8"))


def send_sensor_value(atuador: str):
    global temperature, lumen, smoke
    if atuador == "ar":
        if temperature != None: return f"Temperatura: {temperature:.4f}"
        else:                   return f"O sensor de temperatura e o ar-condicionado estão desligados."

    elif atuador == "lamp":
        if lumen != None:       return f"Luminosidade: {lumen}"
        else:                   return f"O sensor de luminosidade e a lâmpada estão desligados."
    elif atuador == "sis":
        if smoke != None:       return f"Smoke: {smoke}"
        else:                   return f"O sensor de fumaça e Sistema de controle de incendio estão desligados."

    elif atuador == "alarm":
        if smoke != None:       return f"Alame ligado: {smokestatus}"
        else:                   return f"O sensor de fumaça e Sistema de controle de incendio estão desligados."


def ligar_atuador(atuador: str):
    global acstatus, lampstatus, smokestatus
    global accommand, lampcommand, deactivatesmoke, targettemp
    if atuador == "ar":
        if acstatus:            
            return f"O ar-condicionado já está ligado!"
        else:
            accommand = True
            return f"Ar-condicionado ligado (target: {targettemp:.2f})!"
        
    elif atuador == "lamp":
        if lampstatus:            
            return f"A lâmpada já está ligada!"
        else:
            lampcommand = True
            return f"Lampada ligada!"
        
    elif atuador == "sis":
        if smokestatus:            
            return f"O Sistema Controlador de Incêncdio já está ligado!"
        else:
            deactivatesmoke = False
            return f"Sistema Controlador de Incêncdio ligado!"


def desligar_atuador(atuador: str):
    global acstatus, lampstatus, smokestatus
    global accommand, lampcommand, deactivatesmoke

    if atuador == "ar":
        if not acstatus:            
            return f"O ar-condicionado já está desligado!"
        else:
            accommand = False
            return f"Ar-condicionado desligado!"
        
    elif atuador == "lamp":
        if not lampstatus:            
            return f"A lâmpada já está desligada!"
        else:
            lampcommand = False
            return f"Lâmpada desligada!"
        
    elif atuador == "sis":
        if not smokestatus:            
            return f"O alarme já está desligado!"
        else:
            deactivatesmoke = True
            return f"Alarme desligado!"


def set_temp(temp: int):
    '''Permite mudar a temperatura do ar-condicionado'''
    global targettemp
    targettemp = temp
    return f"Temperatura alterada para {temp}"



if __name__ == '__main__':
    main_th = threading.Thread(target=main)
    main_th.start()
    time.sleep(1)
    tcp_server_th = threading.Thread(target=tcp_server)
    tcp_server_th.start()
    