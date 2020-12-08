from microbit import *
import radio

radio.on()
radio.config(channel=1)  # Choose your own channel number
radio.config(power=7)


while True:
    message = radio.receive()

    if (message != None):
        display.scroll(message)
