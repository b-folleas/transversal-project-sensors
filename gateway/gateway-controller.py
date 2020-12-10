# coding: utf8

from microbit import *
import radio

GATEWAY_PIN = '98'
BROADCAST_PIN = '99'
FULL_MESSAGE = ''
COMMUNICATION_ID = 0
PACKET_ID = 0

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)

def id_2_char(id):
    return (str(id) if id > 9 else '0' + str(id))

def radio_handle(packet):

    global FULL_MESSAGE
    global BROADCAST_PIN
    global GATEWAY_PIN
    global COMMUNICATION_ID
    global PACKET_ID

    print('New packet')
    print(packet)

    source_pin = packet[0:2]
    print('Source pin : ' , source_pin)

    destination_pin = packet[2:4]
    print('destination_pin : ' , destination_pin)

    communication_id = packet[4:6]
    print('communication_id : ' , communication_id)

    packet_id = packet[6:8]
    print('packet_id : ' , packet_id)

    flag = packet[8:11]
    print('flag : ' , flag)

    data = packet[11:]
    print('data : ' , data)
    if (destination_pin == (BROADCAST_PIN or GATEWAY_PIN)):
        if (flag == 'SYN'): # réponds ACK
            response = GATEWAY_PIN + source_pin + id_2_char(COMMUNICATION_ID) + '00' + 'ACK' + '##################'
            radio.send(response) # ACK sent, packet sending process continue
            COMMUNICATION_ID = (COMMUNICATION_ID + 1)%100 # each ACK sent creates indent COMMUNICATION_ID
         else (flag == 'RST'):
            response = GATEWAY_PIN + source_pin + communication_id + packet_id + 'RST' + '##################'
            radio.send('RST')
            # arreter communication avec sensor -> n'écrit pas en base le message de la derniere communication du sensor qui a envoyé le reset
    elif (destination_pin == GATEWAY_PIN):
        if (flag == 'PSH'):
            # check le communication_id
            if (id_2_char(COMMUNICATION_ID) == communication_id):
                FULL_MESSAGE = FULL_MESSAGE + data
                print(data)
            else:
                print('Error : Wrong Communication ID :', communication_id, 'should be :', id_2_char(COMMUNICATION_ID))
        elif (flag == 'FIN'):
            if (id_2_char(COMMUNICATION_ID) == communication_id):
                if (packet_id == str(PACKET_ID + 1)):
                    # check communication_id & packet_id = packet_id +1
                    FULL_MESSAGE = FULL_MESSAGE + data
                    print('Message :', FULL_MESSAGE.strip('#')) # delete padding
                    FULL_MESSAGE = ""
                    PACKET_ID = packet_id
                else:
                    print('Error : Wrong Packet ID :', packet_id, 'should be :', PACKET_ID + 1)
            else:
                print('Error : Wrong Communication ID :', communication_id, 'should be :', id_2_char(COMMUNICATION_ID))
    else:
        print('Error : Unauthorized Flag.')

if __name__ == '__main__' :

    print('I am gateway')

    while True:
        msg = radio.receive()

        if (msg != None):
            radio_handle(msg)

        if button_a.is_pressed():
            print("Gateway test")
        
        # stop while
        if button_a.is_pressed() and button_b.is_pressed():
            print('Execution stopped')
            break 
            