from microbit import *
import radio
import time

#29 caractères max on s'assure toujours que le message est inférieur a 232 bit (29 caractères )
msg = "(1,1,1)(2,2,2)(3,3,3)(4,4,4)(5,5,5)(6,6,6)(7,7,7)(8,8,8)"


radio.on()
while True:
    if button_a.is_pressed():
        subMsgStartIndex = 0
        
        # message decomposition
        
        nbMsg = len(msg)//28
        print("nbMsg", nbMsg )
        
        for i in range(nbMsg):
            subMsgEndIndex = (i + 1) * 28
            print(subMsgStartIndex)
            print(subMsgEndIndex)
            

            subMsg = msg[subMsgStartIndex:subMsgEndIndex]
            print(subMsg)
            subMsgStartIndex = subMsgEndIndex
            

    # Ajout dun entete au message 
    sleep(2)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        