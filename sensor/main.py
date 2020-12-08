# coding: utf8

from microbit import *
import radio
from time import *

# 22 caractères max on s'assure toujours que le message est inférieur a 176 bits (22 caractères)
msg = "(1,1,1)(2,2,2)(3,3,3)(4,4,4)(5,5,5)(6,6,6)(7,7,7)(8,8,8)"

lenMsg = len(msg)

print('Msg fait ', lenMsg, 'caractères') 

radio.on()
while not button_b.is_pressed():
    if button_a.is_pressed():
        for i in range(0, len(msg)-1, 22):
            subMsg = msg[i:i+22]
            while len(subMsg) < 22 :
                subMsg+='#' # padding
            sleep(1)
            print(subMsg)
            print('subMsg fait ', len(subMsg), 'caractères') 
