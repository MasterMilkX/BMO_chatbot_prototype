import mysql.connector
from PIL import Image
import random
import numpy as np
import os
import math


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
    count = 0
    
    for image_data in pico_sheets:
        if count == 10:
            break
        image_dict = {}
        hex_list = np.vectorize(hex)(image_data['img'])
        image_dict['hex_string'] = "".join([hex.split('x')[-1] for l in hex_list for hex in l]).upper()
        image_dict['pico_sheet_name'] = image_data['pico_sheet_name']
        image_dict['sprite_id'] = image_data['sprite_id']
        sql = f"INSERT INTO sprite_labels (PICO8_GAME_ID, SPRITE_INDEX, SPRITE_HEX) VALUES ('{image_dict['pico_sheet_name']}', {image_dict['sprite_id']}, '{image_dict['hex_string']}')"
        mycursor.execute(sql)
        count += 1

if __name__ == '__main__':
    filename = '../data/rip_data/good_pico_sheets.npy'
    # convert_sprite_to_hex(filename)
    
    s = "SELECT * FROM sprite_labels"
    mycursor.execute(s)
    sqlRes = mycursor.fetchall()
    print(sqlRes)
