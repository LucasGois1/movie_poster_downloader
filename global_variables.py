from queue import Queue
from time import sleep

global fila

fila = Queue()

sleep(3)

fila.put(50)

sleep(7)

fila.put(1000)

sleep(2)
