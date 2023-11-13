from concurrent import futures
import time
import grpc
from protos import sis_dist_pb2
from protos import sis_dist_pb2_grpc
import random
import datetime
import math
import threading
import pika

#luminosity global variables
LampsetLum = 2200       #luminosidade da lampada
Lampflag = False            #Status da lampada
Dtime = datetime.datetime.now().time()
lumen = 0
dl = 1


def LumReading():
    global Dtime, lumen, LampsetLum, Lampflag

    hours = [0, 4, 6, 8, 14, 16, 18, 20]
    lumenValues = [0, 600, 1400, 2200, 2000, 1600, 600, 0]

    Dtime = datetime.datetime.now().time()
    hour = Dtime.hour

    #lamp is off
    if Lampflag == False:
        #gets a value from the current daytime light
        for i in range(len(hours)):
            if hour <= hours[i]:
                lumen = lumenValues[i]
                break
            else:
                lumen = 0

    #lamp is on
    else:
        for i in range(len(hours)):
            if hour <= hours[i]:
                lumen = lumenValues[i]
                break
            else:
                lumen = 0

        lumen += LampsetLum

    return lumen


def Publisher(qname, sensorFunction, sensorName):
    #Connection with rabbitmq server
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue=qname)

    # publishes a string
    # the string is converted as float, int and bool accondingly for each sensor
    # have not yet to find a way of passing numeric values directly
    # the conversion works though
    while True:
        sensorValue = sensorFunction()
        message = f"{sensorValue}"
        channel.basic_publish(exchange='', routing_key=qname, body=message)
        print(f"Published: {message}")
        time.sleep(1.25)


class AtuadorServicer(sis_dist_pb2_grpc.AtuadorServicer):
    def DeviceOn(self, request, context):
        global Lampflag

        on_reply = sis_dist_pb2.OnReply()

        if request.on:
            print('Lamp is now on')
            on_reply.codigo = 'lamp on'
            Lampflag = True
        else:
            print('Lamp is now off')
            on_reply.codigo = 'lamp off'
            Lampflag = False

        return on_reply


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sis_dist_pb2_grpc.add_AtuadorServicer_to_server(AtuadorServicer(), server)
    server.add_insecure_port("localhost:50051")
    server.start()

    Publisher('LuminositySensor', LumReading, 'Luminosity')

if __name__ == "__main__":
    serve()
