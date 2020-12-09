from microbit import *
import radio

radio.on()
radio.config(channel=1)  # Setting channel for communication
radio.config(power=7)
SENSOR_PIN = '98'
FULL_MESSAGE = ""

def radio_handle(packet):
    print(packet)
    source_pin = packet[0:1]
    destination_pin = packet[1:2]
    communication_id = packet[2:3]
    packet_id = packet[5:6]
    flag = packet[7:10]
    data = packet[10:]
    global FULL_MESSAGE
    
    if flag == 'SYN':
        response = SENSOR_PIN + source_pin + '00' + '00' + 'ACK' + '##################' # 99 for broadcast
        radio.send(response) # packet sending process continue
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
     
    # stop while
    if button_a.is_pressed() and button_b.is_pressed():
        print('Execution stopped')
        break 
        



















        
