import mysql.connector
from PIL import Image
import random
import numpy as np
import os
import math
import time


#CONNECT TO THE SQL DATABASE
def connect_to_db():
    mydb = mysql.connector.connect(
    host="us-cdbr-east-06.cleardb.net",
    user="b50281fd4181c6",
    password="12b4a1bb",
    database="heroku_2f2d25ae5fc707a"
    )

    mycursor = mydb.cursor()
    return mydb, mycursor

def convert_sprite_to_hex(filename):
    pico_sheets = np.load(filename, allow_pickle=True)
    mydb, mycursor = connect_to_db()
    CUR_SS_COUNT = 6001

    while CUR_SS_COUNT < len(pico_sheets):
        print(f"CURRENT SPRITE INDEX: {CUR_SS_COUNT}")
        image_data = pico_sheets[CUR_SS_COUNT]
        if CUR_SS_COUNT % 1500 == 0 and CUR_SS_COUNT != 0:
            print("sleeping")
            time.sleep(3600)
            print("done sleeping")
            mydb, mycursor = connect_to_db()
        image_dict = {}
        hex_list = np.vectorize(hex)(image_data['img'])
        image_dict['hex_string'] = "".join([hex.split('x')[-1] for l in hex_list for hex in l]).upper()
        image_dict['pico_sheet_name'] = image_data['pico_sheet_name'].split('.spritesheet.png')[0]
        image_dict['sprite_id'] = image_data['sprite_id']
        sql = f"INSERT INTO sprite_labels (PICO8_GAME_ID, SPRITE_INDEX, SPRITE_HEX) VALUES ('{image_dict['pico_sheet_name']}', {image_dict['sprite_id']}, '{image_dict['hex_string']}')"
        mycursor.execute(sql)
        mydb.commit()
        CUR_SS_COUNT+=1

# render image from hex string
def render_hex(hex_string):
    hex_list = [hex_string[i:i+6] for i in range(0, len(hex_string), 6)]
    rgb_list = [tuple(int(hex_list[i][j:j+2], 16) for j in (0, 2, 4)) for i in range(len(hex_list))]
    img = Image.new('RGB', (8,8))
    pixels = img.load()
    for i in range(len(rgb_list)):
        x = i % 8
        y = math.floor(i / 8)
        pixels[x,y] = rgb_list[i]
    return img

if __name__ == '__main__':
    filename = '../data/rip_data/good_pico_sheets.npy'
    convert_sprite_to_hex(filename)
    
    # mydb, mycursor = connect_to_db()
    # s = "DELETE FROM sprite_labels"
    # mydb.commit()

    # print("display database")
    # s = "SELECT * FROM sprite_labels LIMIT 10"
    # s = "SELECT user_label, SPRITE_HEX FROM sprite_labels WHERE is_unknown = 1 OR user_label is NOT NULL"

    # mycursor.execute(s)
    # labelled_sprites = mycursor.fetchall()
    # print(labelled_sprites)
    
    # print(len(labelled_sprites))
    
    # for i in range(len(labelled_sprites)):
    #     print(labelled_sprites[i][0])
    #     render_hex(labelled_sprites[i][1]).show()
    
    
    
    
    
