# coding: utf8

from microbit import *
import radio
from time import *
from rsa import *

# testing msg : 22 char max (< 176 bits (22 char))
DATA = "coucou"

PCK_LEN = 29
SSR_PIN = '01'  # hardcode
BCT_PIN = '99'  # hardcode => broadcast pin, can be anything as long as shared between gateway and sensor
GWY_PIN = None
COM_ID = 0  # Set by gateway
PCK_ID = 0
LAST_PCK_RCV = None
STP_BOL = False
DFT_ADD = 75626974
N = 10515
D = 3859
public_key = [N,D]

# The address is generated and given by gateway during ACK
uart.init(baudrate=115200, bits=8, parity=None, stop=1)

radio.on()
radio.config(channel=1)
radio.config(power=7)
radio.config(address=DFT_ADD)

def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))

def init_connection(flag):
    global SSR_PIN
    global BCT_PIN
    packet = SSR_PIN + BCT_PIN + id_2_char(COM_ID) + id_2_char(
        PCK_ID) + flag + '######################'
    print("Init connection packet : ", packet)  # debug
    try:
        radio.send(packet)
    except ValueError:
        print("Error : Connection failure.")
    sleep(1)  # sleep 1s 

def uart_handle():
    data_bytes = (uart.read())
    data = str(data_bytes, 'UTF-8')

def radio_handle(packet):  # response from gateway

    global GWY_PIN
    global COM_ID

    print('Received message from Gateway :', packet)
    src_pin = packet[0:2]
    dst_pin = packet[2:4]
    com_id = packet[4:6]
    pck_id = packet[6:8]
    flag = packet[8:11]
    data = packet[11:]

    if flag == 'ACK':  # can communicate with gateway
        GWY_PIN = src_pin
        COM_ID = int(com_id)
        
        # Set new address
        print('New address :', int(data)) # debug
        radio.config(address=int(data))

def radio_send(msg):  # split the msg into packets of defined length
    PCK_ID = 0
    flag = 'PSH'
    for i in range(0, len(msg)-1, 18):
        subMsg = msg[i:i+18]
        while len(subMsg) < 18:
            subMsg += '#'  # padding
            flag = 'FIN'
        # check if they were no RST meanwhile
        if (LAST_PCK_RCV[8:11] != 'RST'):
            packet = SSR_PIN + GWY_PIN + \
                id_2_char(COM_ID) + \
                id_2_char(PCK_ID) + flag + subMsg
            if (len(packet) <= PCK_LEN):
                try:
                    radio.send(packet)
                    if (flag == 'FIN'):
                        # Back to default address for new communications
                        print('Set default address (FIN) :',
                              int(DFT_ADD))  # debug
                        radio.config(address=int(DFT_ADD))
                except ValueError:
                    print("Error : Problem sending radio.")
            else:
                print("Error : Packet segmentation.")
            PCK_ID += 1
        else:
            print('Reset connection.')
            PCK_ID = 0
            init_connection('RST')

if __name__ == '__main__':

    print('sensor')

    DATA = encrypt(public_key[0],public_key[1],DATA)

    while not STP_BOL:
        # Press button A to send messages
        if button_a.is_pressed():
            init_connection('SYN')

            # Sensor keep waiting for a gateway
            LAST_PCK_RCV = radio.receive()

            if (LAST_PCK_RCV != None):
                # expecting ACK to continue communication
                radio_handle(LAST_PCK_RCV)

                # GWY_PIN is set by ACK of gateway
                if (GWY_PIN != None):
                    radio_send(DATA)
                else:
                    print('Error : Connection refused')
            else:
                print('Error : No response Timeout')

        if uart.any():
            uart_handle()

        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            STP_BOL = True
