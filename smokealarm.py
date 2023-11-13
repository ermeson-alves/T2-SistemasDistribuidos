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

#smoke global variables
SAflagOverwrite = False
smoke = False
count_time = 0


def SmokeReading():
    global smoke, SAflagOverwrite, count_time

    # sensor aguardando fumaca
    if SAflagOverwrite == False:
        # Smoke persiste até overwrite
        if smoke == True:
            x = 1
        else:
            x = 0

        smoke = bool(math.floor(random.uniform(x, 1.04)))

    # sensor detectou fumaca
    else:
        if count_time < 10:
            count_time += 1
        else:
            smoke = False
            count_time = 0

    # retorna true(alerta) ou false(normal)
    return smoke


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
        global SAflagOverwrite

        on_reply = sis_dist_pb2.OnReply()

        if request.on:
            print('Smoke Alarm is now on')
            on_reply.codigo = 'smoke alarm on'
            SAflagOverwrite = True
        else:
            print('Smoke Alarm is now off')
            on_reply.codigo = 'smoke alarm off'
            SAflagOverwrite = False

        return on_reply

def serve():

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    sis_dist_pb2_grpc.add_AtuadorServicer_to_server(AtuadorServicer(), server)
    server.add_insecure_port("localhost:50052")
    server.start()

    Publisher('SmokeSensor', SmokeReading, 'Smoke')

if __name__ == "__main__":
    serve()
