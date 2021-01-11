# coding: utf8

from microbit import *
import radio
import random

GATEWAY_PIN = '98'
BROADCAST_PIN = '99'
FULL_MESSAGE = ''
COMMUNICATION_ID = 0  # From 0 to 100, set the link between gateway and sensor
PACKET_ID = 0  # Checked by gateway
LAST_PACKET_RECEIVED = None
STOP_BOOL = False
DEFAULT_ADDRESS = 75626974
MSG_MAX_LENGTH = 17
KEY = 1436  # shared by sensor and gateway

# Configuration

radio.on()
radio.config(channel=1)  # Setting channel for communication
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


def caesar_encrypt(plain, key):  # only applied to data field
    cipher = bytearray(plain)
    for i, c in enumerate(plain):
        cipher[i] = (ord(c) + key) & 0xff
    bytes_to_return = bytes(cipher)
    return bytes_to_return
    

def caesar_decrypt(cipher, key):
    plain = bytearray(len(cipher)) # at most, len(plain) <= len(cipher)
    for i, c in enumerate(bytes(cipher)):
        plain[i] = (c - key) & 0xff
    return str(bytes(plain), 'utf-8')


def reset_connection():
    subMsg = ''
    subMsg_bytes = bytes(subMsg, 'utf-8')
    parity = getParity(int.from_bytes(subMsg_bytes, 2))
    # Sending response
    response = GATEWAY_PIN + source_pin + \
        id_2_char(COMMUNICATION_ID) + '00' + \
        'RST' + str(parity) + subMsg
    radio.send(response)  # RST sent
    # Reset default configuration
    PACKET_ID = 0
    radio.config(address=DEFAULT_ADDRESS)


def radio_handle(packet):
    
    global FULL_MESSAGE
    global BROADCAST_PIN
    global GATEWAY_PIN
    global COMMUNICATION_ID
    global PACKET_ID

    source_pin = packet[0:2]
    destination_pin = packet[2:4]
    communication_id = packet[4:6]
    packet_id = packet[6:8]
    flag = packet[8:11]
    parity = packet[11:12]
    data = packet[12:]

    print('Message received from sensor :' + packet)

    # Checking parity bit for data integrity
    data_bytes = bytes(data, 'utf-8')
    if (int(parity) == getParity(int.from_bytes(data_bytes, 2))):
    

        if (destination_pin == (BROADCAST_PIN)): # Asking for synchronisation from sensor

                if (flag == 'SYN'):
                # each ACK sent creates COMMUNICATION_ID
                    COMMUNICATION_ID = (COMMUNICATION_ID + 1) % 100
                    # New address for unicast is sent in DATA of ACK

                    # Find right pool for random address
                    address = random.randint(75626970, 75626980)
                    # debug
                    print(';Adress to configure :', str(address), ';')
                    print(';Caesar encrypt :', caesar_encrypt(str(address), KEY), ';')
                    print(';Caesar encrypt hex :',str(bytes(caesar_encrypt(str(address), KEY)), 'utf-8'), ';')

                    subMsg_bytes = bytes(caesar_encrypt(str(address), KEY))
                    subMsg = str(subMsg_bytes, 'utf-8') # msg is address encrypted and encoded in hex to be < MSG_MAX_LENGTH
                    parity = getParity(int.from_bytes(subMsg_bytes, 2))

                    # Sending response
                    response = GATEWAY_PIN + source_pin + \
                        id_2_char(COMMUNICATION_ID) + '00' + 'ACK' + str(parity) + subMsg
                    radio.send(response)  # ACK sent, packet sending process continue

                    # Setting address for communication after sending packet (because sensor is still on old adress)
                    try:
                        radio.config(address=address)
                    except ValueError:
                        print(';Error : Wrong address setting;')     

        elif (destination_pin == GATEWAY_PIN):
            # data_bytes = bytes(data, 'utf-8')
            msg = caesar_decrypt(bytes(data, 'utf-8'), KEY)

            # debug
            print(';data =', data, ';')
            print(';data bytes =', bytes(data, 'utf-8'), ';')
            print(';data bytes decrypted =', caesar_decrypt(bytes(data, 'utf-8'), KEY), ';')
            # decrypt msg

            if (flag == 'PSH'):
                # check le communication_id
                if (id_2_char(COMMUNICATION_ID) == communication_id):
                    FULL_MESSAGE = FULL_MESSAGE + msg
                    PACKET_ID += 1
                else:
                    print(';Error : Wrong Communication ID :', communication_id,
                        'should be :', id_2_char(COMMUNICATION_ID) + ';')
                        
            elif (flag == 'FIN'):
                if (id_2_char(COMMUNICATION_ID) == communication_id):

                    if (packet_id == id_2_char(PACKET_ID)):
                        # check communication_id & packet_id = packet_id +1
                        FULL_MESSAGE = FULL_MESSAGE + msg
                        # delete padding
                        print('Full message :' + FULL_MESSAGE + '@')
                        FULL_MESSAGE = ''
                        
                        PACKET_ID = 0

                        # fin de la communication, on repasse sur l'adresse par défaut
                        radio.config(address=int(DEFAULT_ADDRESS))
                    else:
                        print(';Error : Wrong Packet ID :', packet_id,
                            'should be :', PACKET_ID, ';')
                        reset_connection()
                        # keep the previous COMMUNICATION_ID
                else:
                    print(';Error : Wrong Communication ID :', communication_id,
                        'should be :', id_2_char(COMMUNICATION_ID) + ';')
            else:
                print(';Error : Unauthorized Flag.;')
                reset_connection()
        # if the destination_pin is neither the gateway or broadcast, then the packet is for another potential gateway
    else:
        print(';Error : Parity Bit Error ;')
        reset_connection()
        # keep the previous COMMUNICATION_ID


if __name__ == '__main__':

    print(';I am gateway;')

    while not STOP_BOOL:

        # Gateway keep listening for sensors
        LAST_PACKET_RECEIVED = radio.receive()

        if (LAST_PACKET_RECEIVED != None):
            radio_handle(LAST_PACKET_RECEIVED)
            
        if button_b.is_pressed():
            print(';Gateway is alive !;')

        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print(';Execution stopped;')
            STOP_BOOL = True
