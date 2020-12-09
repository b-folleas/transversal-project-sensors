from microbit import *
import radio

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)

def radio_handle(msg):
    sensor_pin = msg[0:1]
    packet_id = msg[2:3]
    flag = msg[4:7]
    data = msg[8:]

    if flag == 'SYN':
        radio.send('ACK') # packet sending process continue
    elif flag == 'PSH':
        display.scroll(data)
        # continuer communication avec sensor -> check sensor_pin
    elif flag == 'FIN':
        display.scroll(data)
        # arreter communication avec sensor -> pret à accepter un nouveau syn
    elif flag == 'RST':
        radio.send('RST')
        # arreter communication avec sensor -> n'écrit pas en base le message de la derniere communication du sensor qui a envoyé le reset
    else:
        print('Error : Unauthorized Flag.')

while True:
    msg = radio.receive()
    try:
        radio_handle(msg)
    except ValueError:
        display.scroll('Error : No message received.')