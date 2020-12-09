SENSOR_PIN = '98'   
   
packet = SENSOR_PIN + '99' + '00' + '00' + 'SYN' + '######################' # 99 for broadcast
   
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

