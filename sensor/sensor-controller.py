# coding: utf8

from microbit import *
import radio
from time import *

# testing msg : 22 caractères max on s'assure toujours que le message est inférieur a 176 bits (22 caractères)
msg = "F/1,1,1/2,2,2/3,3,3&I/4,4,4/6,6,6"

PACKET_MAX_LENGTH = 29
SENSOR_PIN = '01'
BROADCAST_PIN = '99'
GATEWAY_PIN = None

uart.init(baudrate=115200, bits=8, parity=None, stop=1)

radio.on()
radio.config(channel=1)
radio.config(power=7)

def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))

def init_connection(flag):

    global SENSOR_PIN
    global BROADCAST_PIN
    # for the SYN packet, the communication_id is '00', it value will be sent by gateway
    packet = SENSOR_PIN + BROADCAST_PIN + '00' + '00' + flag + '######################' # 99 for broadcast
    print("init radio : " , packet) # debug
    try:
        radio.send(packet)
    except ValueError:
        print("Error : Connection failure.")
    sleep(1)  # sleep 1s before trying new connection
   
def uart_handle():
    data_bytes = (uart.read())
    data = str(data_bytes, 'UTF-8') # encoding 
    # so far, do nothing

def uart_send(msg):
    print(msg)

def radio_handle(packet): # response from gateway

    global GATEWAY_PIN

    print('Got message', packet) # debug to check if the packet
    source_pin = packet[0:2]
    destination_pin = packet[2:4]
    communication_id = packet[4:6]
    packet_id = packet[6:8]
    flag = packet[8:11]
    data = packet[11:]

    if flag == 'ACK': # can communicate with gateway
        GATEWAY_PIN = source_pin
    
def radio_send(msg): # split the msg into packets of defined length
    packet_id = 0
    flag = 'PSH'
    for i in range(0, len(msg)-1, 18):
        subMsg = msg[i:i+18]
        while len(subMsg) < 18 :
            subMsg+='#' # padding
            flag = 'FIN'
        packet = SENSOR_PIN + GATEWAY_PIN + communication_id + id_2_char(packet_id) + flag + subMsg
        if (len(packet) <= PACKET_MAX_LENGTH):    
            try:
                radio.send(packet)
            except ValueError:
                print("Error : There is a problem with sending radio messages.")
        else:
            print("Error : Packet segmentation.")
        packet_id += 1

if __name__ == '__main__' :

    print('I am sensor')

    while (GATEWAY_PIN == None):
        # keep asking for a connection
        if button_a.is_pressed():
            init_connection('SYN')

        # reset connection
        if button_b.is_pressed():
            init_connection('RST')

        # then sensor keep waiting for a gateway
        packet_received = radio.receive()

        if (packet_received != None):
            radio_handle(packet_received) # expecting ACK to continue communication
            if (GATEWAY_PIN != None): # ACK set GATEWAY_PIN
                print('GATEWAY:',GATEWAY_PIN)
                radio_send(msg)           
            else :
                print('Error : Connection refused')
        
        sleep(1)

        if uart.any(): # check if there is anything to be read
            uart_handle()
            if (data != None):
                init_connection('SYN')

        
        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            break
        