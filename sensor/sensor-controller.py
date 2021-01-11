# coding: utf8

from microbit import *
import radio
from time import *


PACKET_MAX_LENGTH = 29
MSG_MAX_LENGTH = 17
SENSOR_PIN = '01'  # hardcode => similar as a MAC address
# hardcode => broadcast pin, can be anything as long as shared between gateway and sensor
BROADCAST_PIN = '99'
GATEWAY_PIN = None
COMMUNICATION_ID = 0  # Set by gateway
PACKET_ID = 0
LAST_PACKET_RECEIVED = None
STOP_BOOL = False
DEFAULT_ADDRESS = 75626974  # Parameter that can change
KEY = 1436  # shared by sensor and gateway
DATA_ARRAY = []

# The address is generated and given by gateway during ACK

# Configuration
uart.init(baudrate=115200, bits=8, parity=None, stop=1)

radio.on()
radio.config(channel=1)
radio.config(power=7)
radio.config(address=DEFAULT_ADDRESS)


def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))


def getParity(n):  # return 0 if even, 1 if odd
    parity = 0
    while n:
        parity = ~parity
        n = n & (n - 1)
    return abs(parity)


def caesar_encrypt(plain, key):  # only applied to data field
    # plain = plain.encode('utf-8')
    cipher = bytearray(plain)
    for i, c in enumerate(plain):
        cipher[i] = (ord(c) + key) & 0xff
    bytes_to_return = bytes(cipher)
    return bytes_to_return


def caesar_decrypt(cipher, key):
    plain = bytearray(len(cipher))    # at most, len(plain) <= len(cipher)
    for i, c in enumerate(bytes(cipher)):
        plain[i] = (c - key) & 0xff
    return str(bytes(plain), 'utf-8')


def init_connection():
    global SENSOR_PIN
    global BROADCAST_PIN

    subMsg = ''
    # Converting String to binary
    subMsg_bytes = bytes(subMsg, 'utf-8')
    parity = getParity(int.from_bytes(subMsg_bytes, 2))

    packet = SENSOR_PIN + BROADCAST_PIN + id_2_char(COMMUNICATION_ID) + id_2_char(
        PACKET_ID) + 'SYN' + str(parity) + subMsg
    print(';Init connection packet : ', packet, ';')  # debug
    print(';Current address: ', DEFAULT_ADDRESS, ';')  # debug
    try:
        radio.send(packet)
    except ValueError:
        print(';Error : Connection failure.;')
    sleep(1)  # sleep 1s before trying new connection


def uart_handle():
    global DATA
    global DATA_ARRAY

    data_bytes = (uart.read())
    DATA = caesar_encrypt(str(data_bytes, 'utf-8'), KEY)  # encoding & encrypting
    DATA_ARRAY.append(DATA)
    # radio_send(DATA)


def reset_connection_sensor():
    PACKET_ID = 0
    radio.config(address=DEFAULT_ADDRESS)
    init_connection('SYN')


def radio_handle(packet):  # response from gateway

    global GATEWAY_PIN
    global COMMUNICATION_ID

    # debug to check the packet from gateway
    print(';Received message from Gateway :', packet, ';')
    source_pin = packet[0:2]
    destination_pin = packet[2:4]
    communication_id = packet[4:6]
    packet_id = packet[6:8]
    flag = packet[8:11]
    parity = packet[11:12]
    data = packet[12:]
    data_bytes = bytes(data, 'utf-8')

    # debug
    print(';data =', data, ';')
    print(';data_bytes =', data_bytes, ';')

    if (int(parity) == getParity(int.from_bytes(data_bytes, 2))):

        if flag == 'ACK':  # can communicate with gateway
            GATEWAY_PIN = source_pin
            COMMUNICATION_ID = int(communication_id)

            # Set new address sent from gateway
            # debug DELETE print('New address :', int(data)) # debug
            print(';caesar decrypt data bytes (new address):', bytes(
                caesar_decrypt(data_bytes, KEY), 'utf-8'), ';')
            radio.config(address=int(
                bytes(caesar_decrypt(data_bytes, KEY), 'utf-8')))
        
        elif flag == 'RST':
            print(';Reset : Gateway asked to reset connection.;')
            reset_connection_sensor()
            
    else:
        print(';Error : Parity Bit Error ;')
        reset_connection_sensor()


def radio_send(msg):  # split the msg into packets of defined length
    PACKET_ID = 0
    flag = 'PSH'
    for i in range(0, len(msg)-1, MSG_MAX_LENGTH):
        # msg F1,1,....

        subMsg = msg[i:i+MSG_MAX_LENGTH]
        if len(subMsg) < MSG_MAX_LENGTH:
            flag = 'FIN'
        print(';subMsg = ', subMsg, ';') # debug

        parity = getParity(int.from_bytes(subMsg, 2))
        print(';parity = ', parity, ';')

        # check if they were no RST meanwhile
        packet = SENSOR_PIN + GATEWAY_PIN + \
            id_2_char(COMMUNICATION_ID) + \
            id_2_char(PACKET_ID) + flag + \
            str(parity) + str(subMsg, 'utf-8')
        if (len(packet) <= PACKET_MAX_LENGTH):
            try:
                radio.send(packet)
                if (flag == 'FIN'):
                    # Back to default address for new communications
                    print(';Back to default address (FIN) :',int(DEFAULT_ADDRESS), ';')  # debug
                    radio.config(address=int(DEFAULT_ADDRESS))
            except ValueError:
                print(';Error : There is a problem with sending radio messages.;')
        else:
            print(';Error : Packet segmentation.;')
        PACKET_ID += 1            

i = 0

if __name__ == '__main__':

    print(';I am sensor;')

    while not STOP_BOOL:

        DATA = caesar_encrypt('F/1,1,1/2,2,6/1,5,3/4,5,3/2,1,1/3,3,3/2,3,1&I/4,4,4/6,6,6', KEY) # Local TEST
        if uart.any():  # check if there is anything to be read
            uart_handle()
            DATA = caesar_encrypt(DATA_ARRAY[i] , KEY)

        # Press button A to send messages
        if button_a.is_pressed():
            init_connection()

            # Sensor keep waiting for a gateway
            LAST_PACKET_RECEIVED = radio.receive()

            if (LAST_PACKET_RECEIVED != None):
                # expecting ACK to continue communication
                radio_handle(LAST_PACKET_RECEIVED)

                # GATEWAY_PIN is set by ACK of gateway
                if (GATEWAY_PIN != None):
                    radio_send(DATA)
                    i += 1
                else:
                    print(';Error : Connection refused;')
            else:
                print(';Error : No response Timeout;')

        if button_b.is_pressed():
            print(';Sensor is alive !;')

        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print(';Execution stopped;')
            STOP_BOOL = True
            