# coding: utf8

from microbit import *
import radio
from time import *

# testing msg : 22 caractères max on s'assure toujours que le message est inférieur a 176 bits (22 caractères)
msg = "(1,1,1)(2,2,2)(3,3,3)(4,4,4)(5,5,5)(6,6,6)(7,7,7)(8,8,8)"

PACKET_MAX_LENGTH = 29
SENSOR_PIN = '01'

uart.init(baudrate=115200, bits=8, parity=None, stop=1)

radio.on()
radio.config(channel=1)
radio.config(power=7)

def init_connection():
    packet = SENSOR_PIN + '00SYN######################' 
    print("init radio : " , packet)
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

def radio_send(msg): # split the msg into packets of defined length
    packet_id = 0
    flag = 'PSH'
    for i in range(0, len(msg)-1, 22):
        subMsg = msg[i:i+22]
        while len(subMsg) < 22 :
            subMsg+='#' # padding
            flag = 'FIN'
            packet = SENSOR_PIN + (str(packet_id) if packet_id > 9 else '0' + str(packet_id)) + flag + subMsg
        if (len(packet) <= PACKET_MAX_LENGTH):    
            try:
                print(packet)
                radio.send(packet)
            except ValueError:
                print("Error : There is a problem with sending radio messages.")
        else:
            print("Error : Packet segmentation.")
        packet_id += 1

while True:
    
    if button_a.is_pressed(): # test sending packet then display in gateway
        init_connection()

        # we suggest the sensor only listen if it is awaiting an ACK
        packet_received = radio.receive()

        if (packet_received != None):
            if (packet_received == 'ACK'): # broken check condition -> should be improved
                radio_send(msg)
            else :
                print('Error : Unauthorized connection')
    sleep(1)

    if uart.any(): # check if there is anything to be read
        uart_handle()
    
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
    