from microbit import *
import radio

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)

def radio_handle(packet):
    print(packet) # debug to check if the packet
    sensor_pin = packet[0:1]
    packet_id = packet[2:3]
    flag = packet[4:7]
    data = packet[8:]

    if flag == 'SYN':
        radio.send('ACK') # packet sending process continue
    elif flag == 'PSH':
        print(data)
        # continuer communication avec sensor -> check sensor_pin
    elif flag == 'FIN':
        print(data)
        # arreter communication avec sensor -> pret à accepter un nouveau syn
    elif flag == 'RST':
        radio.send('RST')
        # arreter communication avec sensor -> n'écrit pas en base le message de la derniere communication du sensor qui a envoyé le reset
    else:
        print('Error : Unauthorized Flag.')

while True:
    packet = radio.receive()

    if (packet != None):
        radio_handle(packet)













