# coding: utf8

from microbit import *
import radio
import random

GATEWAY_PIN = '98'
BROADCAST_PIN = '99'
FULL_MESSAGE = ''
COMMUNICATION_ID = 0  # From 0 to 100, set the link between gateway and sensor
PACKET_ID = 0  # Last packet got on gateway
STOP_BOOL = False
DEFAULT_ADDRESS = 75626974
KEY = 1436  # shared by sensor and gateway

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)
radio.config(address=DEFAULT_ADDRESS)


def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))


def caesar_encrypt(plain, key):  # only applied to data field
    plain = plain.encode('utf-8')
    cipher = bytearray(plain)
    for i, c in enumerate(plain):
        cipher[i] = (c + key) & 0xff
    bytes_to_return = bytes(cipher)
    return bytes_to_return.hex()
    

def caesar_decrypt(cipher, key):
    plain = bytearray(len(cipher))    # at most, len(plain) <= len(cipher)
    for i, c in enumerate(bytes.fromhex(cipher)):
        plain[i] = (c - key) & 0xff
    return plain.decode('utf-8')


def radio_handle(packet):

    global FULL_MESSAGE
    global BROADCAST_PIN
    global GATEWAY_PIN
    global COMMUNICATION_ID
    global PACKET_ID

    print('Incoming packet :', packet)

    source_pin = packet[0:2]
    destination_pin = packet[2:4]
    communication_id = packet[4:6]
    packet_id = packet[6:8]
    flag = packet[8:11]
    data = packet[11:]

    if (destination_pin == (BROADCAST_PIN or GATEWAY_PIN)):
        if (flag == 'SYN'):  # response from gateway is ACK
            # each ACK sent creates COMMUNICATION_ID
            COMMUNICATION_ID = (COMMUNICATION_ID + 1) % 100
            # New address for unicast is sent in DATA of ACK

            # Find right pool for random address
            address = random.randint(75626970, 75626980)
            print('Set New address :', address)  # debug

            # In ACK, data is encrypted as address is defined on 8 bytes and we have 18 bytes for data
            response = GATEWAY_PIN + source_pin + \
                id_2_char(COMMUNICATION_ID) + '00' + 'ACK' + \
                caesar_encrypt(str(address), KEY)
            radio.send(response)  # ACK sent, packet sending process continue

            # Setting address for communication after sending packet (because sensor is still on old adress)
            try:
                radio.config(address=address)
            except ValueError:
                print('Error : Wrong address setting')
    elif (destination_pin == GATEWAY_PIN):
        if (flag == 'PSH'):
            # check le communication_id
            if (id_2_char(COMMUNICATION_ID) == communication_id):
                FULL_MESSAGE = FULL_MESSAGE + data
                print(data)
            else:
                print('Error : Wrong Communication ID :', communication_id,
                      'should be :', id_2_char(COMMUNICATION_ID))
        elif (flag == 'FIN'):
            if (id_2_char(COMMUNICATION_ID) == communication_id):
                if (packet_id == id_2_char(PACKET_ID + 1)):
                    # check communication_id & packet_id = packet_id +1
                    FULL_MESSAGE = FULL_MESSAGE + data
                    # delete padding
                    print('Message decrypté :', caesar_decrypt(FULL_MESSAGE.strip('#'), KEY))
                    
                    # Here send message via UART to web server
                    
                    FULL_MESSAGE = ""
                    PACKET_ID = packet_id

                    # fin de la communication, on repasse sur l'adresse par défaut
                    print('Back to default address :',
                          int(DEFAULT_ADDRESS))  # debug
                    radio.config(address=int(DEFAULT_ADDRESS))
                else:
                    print('Error : Wrong Packet ID :', packet_id,
                          'should be :', PACKET_ID + 1)
                    # keep the previous COMMUNICATION_ID
                    response = GATEWAY_PIN + source_pin + \
                        id_2_char(COMMUNICATION_ID) + '00' + \
                        'RST' + '##################'
                    radio.send(response)  # RST sent
                    radio.config(address=DEFAULT_ADDRESS)
            else:
                print('Error : Wrong Communication ID :', communication_id,
                      'should be :', id_2_char(COMMUNICATION_ID))
    else:
        print('Error : Unauthorized Flag.')


if __name__ == '__main__':

    print('I am gateway')

    while not STOP_BOOL:
        msg = radio.receive()

        if (msg != None):
            radio_handle(msg)

        if button_a.is_pressed():
            print("Gateway is alive !")

        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            STOP_BOOL = True
