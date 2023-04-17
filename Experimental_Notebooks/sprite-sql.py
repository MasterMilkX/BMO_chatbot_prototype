import mysql.connector
from PIL import Image
import random
import numpy as np
import os
import math
import time


#CONNECT TO THE SQL DATABASE
mydb = mysql.connector.connect(
  host="us-cdbr-east-06.cleardb.net",
  user="b50281fd4181c6",
  password="12b4a1bb",
  database="heroku_2f2d25ae5fc707a"
)

mycursor = mydb.cursor()

def convert_sprite_to_hex(filename):
    pico_sheets = np.load(filename, allow_pickle=True)
    CUR_SS_COUNT = 1386

    while CUR_SS_COUNT < len(pico_sheets):
        print(f"CURRENT SPRITE INDEX: {CUR_SS_COUNT}")
        image_data = pico_sheets[CUR_SS_COUNT]
        if CUR_SS_COUNT % 3000 == 0 and CUR_SS_COUNT != 0:
            print("sleeping")
            time.sleep(3600)
            print("done sleeping")
        image_dict = {}
        hex_list = np.vectorize(hex)(image_data['img'])
        image_dict['hex_string'] = "".join([hex.split('x')[-1] for l in hex_list for hex in l]).upper()
        image_dict['pico_sheet_name'] = image_data['pico_sheet_name'].split('.spritesheet.png')[0]
        image_dict['sprite_id'] = image_data['sprite_id']
        sql = f"INSERT INTO sprite_labels (PICO8_GAME_ID, SPRITE_INDEX, SPRITE_HEX) VALUES ('{image_dict['pico_sheet_name']}', {image_dict['sprite_id']}, '{image_dict['hex_string']}')"
        mycursor.execute(sql)
        mydb.commit()
        CUR_SS_COUNT+=1
        

if __name__ == '__main__':
    filename = '../data/rip_data/good_pico_sheets.npy'
    convert_sprite_to_hex(filename)
    
    # print("display database")
    # s = "SELECT * FROM sprite_labels LIMIT 10"
    # s = "DELETE FROM sprite_labels"

    # mycursor.execute(s)
    # mydb.commit()
    # sqlRes = mycursor.fetchall()
    # print(sqlRes)
