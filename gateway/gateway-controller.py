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

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)
radio.config(address=DEFAULT_ADDRESS)


def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))


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
    data = packet[11:]
    if (destination_pin == (BROADCAST_PIN or GATEWAY_PIN)):
        if (flag == 'SYN'):  # response from gateway is ACK
            # each ACK sent creates COMMUNICATION_ID
            COMMUNICATION_ID = (COMMUNICATION_ID + 1) % 100
            # New address for unicast is sent in DATA of ACK

            # Find right pool for random address
            address = random.randint(75626970, 75626980)

            response = GATEWAY_PIN + source_pin + \
                id_2_char(COMMUNICATION_ID) + '00' + 'ACK' + str(address)
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
                PACKET_ID += 1
            else:
                print('Error : Wrong Communication ID :', communication_id,
                      'should be :', id_2_char(COMMUNICATION_ID) + '@')
                     
        elif (flag == 'FIN'):
            if (id_2_char(COMMUNICATION_ID) == communication_id):

                if (packet_id == id_2_char(PACKET_ID)):
                    # check communication_id & packet_id = packet_id +1
                    FULL_MESSAGE = FULL_MESSAGE + data
                    # delete padding
                    print(FULL_MESSAGE.strip('#') + '@')
                    FULL_MESSAGE = ""
                    
                    PACKET_ID = 0

                    # fin de la communication, on repasse sur l'adresse par défaut
                    radio.config(address=int(DEFAULT_ADDRESS))
                else:
                    print('Error : Wrong Packet ID :', packet_id,
                          'should be :', PACKET_ID, '@')
                    # keep the previous COMMUNICATION_ID
                    response = GATEWAY_PIN + source_pin + \
                        id_2_char(COMMUNICATION_ID) + '00' + \
                        'RST' + '##################'
                    radio.send(response)  # RST sent
                    PACKET_ID = 0
                    radio.config(address=DEFAULT_ADDRESS)
            else:
                print('Error : Wrong Communication ID :', communication_id,
                      'should be :', id_2_char(COMMUNICATION_ID) + '@')
    else:
        print('Error : Unauthorized Flag.')


if __name__ == '__main__':

    print('I am gateway@')

    while not STOP_BOOL:
        msg = radio.receive()

        if (msg != None):
            radio_handle(msg)
            

        if button_a.is_pressed():
            print("Gateway is alive !@")

        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            STOP_BOOL = True
