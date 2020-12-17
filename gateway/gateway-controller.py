# coding: utf8

from microbit import *
import radio
import random
import rsa import *

GWY_PIN = '98'
BCT_PIN = '99'
FULL_MESSAGE = ''
COM_ID = 0  # From 0 to 100, set the link between gateway and sensor
PCK_ID = 0  # Last packet got on gateway
STP_BOL = False
DFT_ADD = 75626974
N = 10515
C = 739
D = 3859
private_key = [N,C]
public_key = [N,D]

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)
radio.config(address=DFT_ADD)

def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))

def radio_handle(packet):

    global FULL_MESSAGE
    global BCT_PIN
    global GWY_PIN
    global COM_ID
    global PCK_ID

    print('Incoming packet :', packet)

    src_pin = packet[0:2]
    dst_pin = packet[2:4]
    com_id = packet[4:6]
    pck_id = packet[6:8]
    flag = packet[8:11]
    data = packet[11:]
    if (dst_pin == (BCT_PIN or GWY_PIN)):
        if (flag == 'SYN'):  # response from gateway is ACK
            # each ACK sent creates COM_ID
            COM_ID = (COM_ID + 1) % 100
            # New address for unicast is sent in DATA of ACK

            # Find right pool for random address
            address = random.randint(75626970, 75626980)
            print('Set New address :', address)  # debug

            response = GWY_PIN + src_pin + \
                id_2_char(COM_ID) + '00' + 'ACK' + str(address)
            radio.send(response)  # ACK sent, packet sending process continue

            # Setting address for communication after sending packet (because sensor is still on old adress)
            try:
                radio.config(address=address)
            except ValueError:
                print('Error : Wrong address setting')
    elif (dst_pin == GWY_PIN):
        if (flag == 'PSH'):
            # check le com_id
            if (id_2_char(COM_ID) == com_id):
                FULL_MESSAGE = FULL_MESSAGE + data
                print(data)
            else:
                print('Error : Wrong Communication ID :', com_id,
                      'should be :', id_2_char(COM_ID))
        elif (flag == 'FIN'):
            if (id_2_char(COM_ID) == com_id):
                if (pck_id == id_2_char(PCK_ID + 1)):
                    # check com_id & pck_id = pck_id +1
                    FULL_MESSAGE = FULL_MESSAGE + data
                    # delete padding
                    print('Message :', decrypt(private_key[0],private_key[1],FULL_MESSAGE.strip('#')))
                    FULL_MESSAGE = ""
                    PCK_ID = pck_id

                    # fin de la communication, on repasse sur l'adresse par défaut
                    print('Back to default address :',
                          int(DFT_ADD))  # debug
                    radio.config(address=int(DFT_ADD))
                else:
                    print('Error : Wrong Packet ID :', pck_id,
                          'should be :', PCK_ID + 1)
                    # keep the previous COM_ID
                    response = GWY_PIN + src_pin + \
                        id_2_char(COM_ID) + '00' + \
                        'RST' + '##################'
                    radio.send(response)  # RST sent
                    radio.config(address=DFT_ADD)
            else:
                print('Error : Wrong Communication ID :', com_id,
                      'should be :', id_2_char(COM_ID))
    else:
        print('Error : Unauthorized Flag.')

if __name__ == '__main__':

    print('gateway')

    while not STP_BOL:
        msg = radio.receive()

        if (msg != None):
            radio_handle(msg)

        if button_a.is_pressed():
            print("gateway")

        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            STP_BOL = True
