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

#temperature global variables
ACsetTemp = 22          #Temperature setted by the ac
ACflag = False              #Status of the AC
temperature = 28
d = 1


def TempReading():
    global temperature, d, ACsetTemp, ACflag

    step = random.uniform(0.0, 2.0)*random.random()
    temperature += step * d

    #regular daytime temp escillation
    if ACflag == False:
        if temperature >= 33 + random.uniform(-2.0, 2.0):
            d = -1
        elif temperature <= 27 + random.uniform(-2.0, 2.0):
            d = 1

    #AC is on
    else:
        d = -1

    return temperature


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
        global ACsetTemp, ACflag

        on_reply = sis_dist_pb2.OnReply()

        if request.on:
            print('AC is now on')
            on_reply.codigo = 'ac on'
            ACflag = True
        else:
            print('AC is now off')
            on_reply.codigo = 'ac off'
            ACflag = False

        ACsetTemp = request.temperatura

        return on_reply


def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sis_dist_pb2_grpc.add_AtuadorServicer_to_server(AtuadorServicer(), server)
    server.add_insecure_port("localhost:50053")
    server.start()

    Publisher('TemperatureSensor', TempReading, 'Temperature')

if __name__ == "__main__":
    serve()
