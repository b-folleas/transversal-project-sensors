# coding: utf8

from microbit import *
import radio

GATEWAY_PIN = '98'
BROADCAST_PIN = '99'
FULL_MESSAGE = ""

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)

def radio_handle(packet):

    global FULL_MESSAGE
    global BROADCAST_PIN
    global GATEWAY_PIN

    print('New packet')
    print(packet)

    source_pin = packet[0:2]
    print("Source pin : " , source_pin)

    destination_pin = packet[2:4]
    print("destination_pin : " , destination_pin)

    communication_id = packet[4:6]
    print("communication_id : " , communication_id)

    packet_id = packet[6:8]
    print("packet_id : " , packet_id)

    flag = packet[8:11]
    print("flag : " , flag)

    data = packet[11:]
    print("data : " , data)
    
    if (destination_pin == GATEWAY_PIN or destination_pin == BROADCAST_PIN):
        if (flag == 'SYN'):
            response = GATEWAY_PIN + source_pin + '00' + '00' + 'ACK' + '##################'
            radio.send(response) # packet sending process continue
        elif flag == 'PSH':
            FULL_MESSAGE = FULL_MESSAGE + data
            print(data)
            # continuer communication avec sensor -> check sensor_pin
        elif flag == 'FIN':
            FULL_MESSAGE = FULL_MESSAGE + data
            print('Message :', FULL_MESSAGE.strip('#')) # delete padding
            FULL_MESSAGE = ""
            # arreter communication avec sensor -> pret à accepter un nouveau syn
        elif flag == 'RST':
            radio.send('RST')
            # arreter communication avec sensor -> n'écrit pas en base le message de la derniere communication du sensor qui a envoyé le reset
        else:
            print('Error : Unauthorized Flag.')
    else:
        print('Error : Wrong destination')

if __name__ == "__main__" :

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
            