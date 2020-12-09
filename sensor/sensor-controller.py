# coding: utf8

from microbit import *
import radio
from time import *

# testing msg : 22 caractères max on s'assure toujours que le message est inférieur a 176 bits (22 caractères)
msg = "(1,1,1)(2,2,2)(3,3,3)(4,4,4)(5,5,5)(6,6,6)(7,7,7)(8,8,8)"


PACKET_MAX_LENGTH = 29
SENSOR_PIN = '01'
GATEWAY_PIN = ''

uart.init(baudrate=115200, bits=8, parity=None, stop=1)

radio.on()
radio.config(channel=1)
radio.config(power=7)

def init_connection():
    packet = SENSOR_PIN + '99' + '00' + '00' + 'SYN' + '######################' # 99 for broadcast
    print("init radio : " , packet) # debug
    try :
        radio.send(packet)
    except ValueError:
        print("Error : Connection failure.")
    sleep(0.1)  # sleep 100 ms
   
   
def uart_handle():
    msg_bytes = (uart.read())
    msg_str = str(msg_bytes, 'UTF-8') # encoding 
    # so far, do nothing


def uart_send(msg):
    print(msg)

def radio_handle(packet): # response from gateway
    print('Got message', packet) # debug to check if the packet
    source_pin = packet[0:1]
    destination_pin = packet[2:3]
    communication_id = packet[4:5]
    packet_id = packet[5:6]
    flag = packet[7:10]
    data = packet[10:]

    if flag == 'ACK':
        GATEWAY_PIN = source_pin
    
def radio_send(msg): # split the msg into packets of defined length
    packet_id = 0
    flag = 'PSH'
    for i in range(0, len(msg)-1, 18):
        subMsg = msg[i:i+18]
        while len(subMsg) < 18 :
            subMsg+='#' # padding
            flag = 'FIN'
        packet = SENSOR_PIN + GATEWAY_PIN + '00' + (str(packet_id) if packet_id > 9 else '0' + str(packet_id)) + flag + subMsg
        if (len(packet) <= PACKET_MAX_LENGTH):    
            try:
                print(packet)
                radio.send(packet)
            except ValueError:
                print("Error : There is a problem with sending radio messages.")
        else:
            print("Error : Packet segmentation.")
        packet_id += 1

print('Hello')

while True:

    init_connection()

    # we suggest the sensor only listen if it is awaiting an ACK
    packet_received = radio.receive()

    if (packet_received != None):
        if (packet_received == 'ACK'):
            radio_send(msg)
        else :
            print('Error : Connection refused')
       
    sleep(1)

    if uart.any(): # check if there is anything to be read
        uart_handle()
     
    # stop while
    if button_a.is_pressed() and button_b.is_pressed():
        print('Execution stopped')
        break
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    