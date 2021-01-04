# coding: utf8

from microbit import *
import radio
from time import *

DATA = ""

PACKET_MAX_LENGTH = 29
MSG_MAX_LENGTH = 17
SENSOR_PIN = '01'  # hardcode => similar as a MAC address
BROADCAST_PIN = '99'  # hardcode => broadcast pin, can be anything as long as shared between gateway and sensor
GATEWAY_PIN = None
COMMUNICATION_ID = 0  # Set by gateway
PACKET_ID = 0
LAST_PACKET_RECEIVED = None
STOP_BOOL = False
DEFAULT_ADDRESS = 75626974  # Parameter that can change

# The address is generated and given by gateway during ACK

uart.init(baudrate=115200, bits=8, parity=None, stop=1)

radio.on()
radio.config(channel=1)
radio.config(power=7)
radio.config(address=DEFAULT_ADDRESS)


def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))


def getParity(n): # return 0 if even, 1 if odd 
	parity = 0
	while n: 
		parity = ~parity 
		n = n & (n - 1) 
	return abs(parity) 


def init_connection(flag):
    global SENSOR_PIN
    global BROADCAST_PIN

    subMsg = ''
    while len(subMsg) < MSG_MAX_LENGTH:
        subMsg += '#'  # padding
    # Converting String to binary 
    subMsg_bytes = bytes(subMsg, "utf-8")
    parity = getParity(int.from_bytes(subMsg_bytes, 2))

    packet = SENSOR_PIN + BROADCAST_PIN + id_2_char(COMMUNICATION_ID) + id_2_char(
        PACKET_ID) + flag + str(parity) + subMsg
    print("Init connection packet : ", packet)  # debug
    print("Current address: ", DEFAULT_ADDRESS)  # debug
    try:
        radio.send(packet)
    except ValueError:
        print("Error : Connection failure.")
    sleep(1)  # sleep 1s before trying new connection


def uart_handle():
    global DATA
    data_bytes = (uart.read())
    DATA = str(data_bytes, 'UTF-8')  # encoding
    radio_send(DATA)


def radio_handle(packet):  # response from gateway

    global GATEWAY_PIN
    global COMMUNICATION_ID

    # debug to check the packet from gateway
    print('Received message from Gateway :', packet)
    source_pin = packet[0:2]
    destination_pin = packet[2:4]
    communication_id = packet[4:6]
    packet_id = packet[6:8]
    flag = packet[8:11]
    parity = packet[11:12]
    data = packet[12:]
    data_bytes = bytes(data, "utf-8")
    if (int(parity) == getParity(int.from_bytes(data_bytes, 2))):
        if flag == 'ACK':  # can communicate with gateway
            GATEWAY_PIN = source_pin
            COMMUNICATION_ID = int(communication_id)
            
            # Set new address sent from gateway
            print('New address :', int(data)) # debug
            radio.config(address=int(data))
    else:
        print('Error : Parity Bit Error @')


def radio_send(msg):  # split the msg into packets of defined length
    PACKET_ID = 0
    flag = 'PSH'
    for i in range(0, len(msg)-1, MSG_MAX_LENGTH):
        subMsg = msg[i:i+MSG_MAX_LENGTH]
        while len(subMsg) < MSG_MAX_LENGTH:
            subMsg += '#'  # padding
            flag = 'FIN'
        subMsg_bytes = bytes(subMsg, "utf-8")
        parity = getParity(int.from_bytes(subMsg_bytes, 2))
        # check if they were no RST meanwhile
        if (LAST_PACKET_RECEIVED[8:11] != 'RST'):
            packet = SENSOR_PIN + GATEWAY_PIN + \
                id_2_char(COMMUNICATION_ID) + \
                id_2_char(PACKET_ID) + flag + str(parity) + subMsg
            if (len(packet) <= PACKET_MAX_LENGTH):
                try:
                    radio.send(packet)
                    if (flag == 'FIN'):
                        # Back to default address for new communications
                        print('Back to default address (FIN) :',
                              int(DEFAULT_ADDRESS))  # debug
                        radio.config(address=int(DEFAULT_ADDRESS))
                except ValueError:
                    print("Error : There is a problem with sending radio messages.")
            else:
                print("Error : Packet segmentation.")
            PACKET_ID += 1
        else:
            print('Reset : Reset connection and sending message again.')
            PACKET_ID = 0
            init_connection('RST')


if __name__ == '__main__':

    print('I am sensor')

    while not STOP_BOOL:
        # Press button A to send messages
        if button_a.is_pressed():
            init_connection('SYN')

            # Sensor keep waiting for a gateway
            LAST_PACKET_RECEIVED = radio.receive()

            if (LAST_PACKET_RECEIVED != None):
                # expecting ACK to continue communication
                radio_handle(LAST_PACKET_RECEIVED)

                # GATEWAY_PIN is set by ACK of gateway
                if (GATEWAY_PIN != None):
                    radio_send(DATA)
                else:
                    print('Error : Connection refused')
            else:
                print('Error : No response Timeout')

        if uart.any():  # check if there is anything to be read
            uart_handle()

        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            STOP_BOOL = True
