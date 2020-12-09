from microbit import *
import radio

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)
FULL_MESSAGE = ""

def radio_handle(msg):
    print(msg)
    sensor_pin = msg[0:1]
    packet_id = msg[2:3]
    flag = msg[4:7]
    data = msg[7:]
    global FULL_MESSAGE
    
    if flag == 'SYN':
        radio.send('ACK') # packet sending process continue
    elif flag == 'PSH':
        FULL_MESSAGE = FULL_MESSAGE + data
        print(data)
        # continuer communication avec sensor -> check sensor_pin
    elif flag == 'FIN':
        FULL_MESSAGE = FULL_MESSAGE + data
        print(data.strip('d'))
        print(FULL_MESSAGE.strip('#'))
        FULL_MESSAGE = ""
        # arreter communication avec sensor -> pret à accepter un nouveau syn
    elif flag == 'RST':
        radio.send('RST')
        # arreter communication avec sensor -> n'écrit pas en base le message de la derniere communication du sensor qui a envoyé le reset
    else:
        print('Error : Unauthorized Flag.')

while True:
    msg = radio.receive()

    if (msg != None):
        radio_handle(msg)

    if button_a.is_pressed():
        print("Gateway test")
        
        



















        
