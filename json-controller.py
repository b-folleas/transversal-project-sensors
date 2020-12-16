# coding: utf8
  
import json 

FILENAME = "./data.json"

def display_data():
    with open(FILENAME,) as json_file:
        data = json.load(json_file)
        for i in data['sensors']:
            print(i)
            
if __name__ == '__main__' :
    # display json file
    display_data()
    