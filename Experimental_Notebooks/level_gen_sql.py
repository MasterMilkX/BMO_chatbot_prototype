import mysql.connector
from PIL import Image
import random
import numpy as np
import os
import math


#CONNECT TO THE SQL DATABASE
mydb = mysql.connector.connect(
  host="localhost",
  user="aesth_bot",
  password="AR1Z0N4_iceD-T",
  database="aesthetic-bot"
)
mycursor = mydb.cursor()




# CLASS DEFINITION FOR TILESET/SPRITESHEET 
class Tileset:
	def __init__(self, tilesetLoc, num_tiles=16, tsize=8):
		self.tsize = tsize
		self.num_tiles = num_tiles
		self.tileFile = tilesetLoc
		self.spritesheet = self.createSpriteSheet("../tilesets/"+tilesetLoc+".png",tsize)


	# import the tileset to create levels from 
	def createSpriteSheet(self, tileset, ts=8):
		#break up the tilesheet by tile size
		tile_img = Image.open(tileset)
		w = tile_img.width/ts
		h = tile_img.height/ts
		self.num_tiles = (int(w * h) if self.num_tiles == 0 else self.num_tiles)

		#get all tiles and assign values (left to right, top to bottom)
		spr_sht = {}
		for t in range(self.num_tiles):
			x = t % w
			y = t // w
			spr_sht[t] = tile_img.crop((x*ts,y*ts,(x+1)*ts,(y+1)*ts))

		return spr_sht

# AN ASCII GAME MAP LEVEL OF USING TILES FROM A GIVEN GAME TILESET
class AsciiLevel:
	def __init__(self, tileset, mapDim):
		self.tileset = tileset
		self.map_dimensions = mapDim    #in the form (w,h)
		self.level = []

	#create a random map from the tileset given
	def generateRandomLevel(self):
		self.level = []
		for hi in range(self.map_dimensions[1]):
			row = []
			for wi in range(self.map_dimensions[0]):
				row.append(random.randint(0,self.tileset.num_tiles-1))
			self.level.append(row)
		self.level = np.array(self.level)
		return self.level

	#import a 2d ascii array or string as the level
	def importLevel(self,i):
		#raw database string
		if type(i) == str:
			i = i.replace('\r','')
			rows = i.split("\n")
			l = []
			for r in rows:
				l.append([int(x,16) for x in r])
			self.level = np.array(l)
		#already converted to numeric 2d array
		else:
			self.level = np.array(i)


	#creates an image of the ascii level using the tileset
	def makeLevelImg(self):
		if len(self.level) == 0:
			return None

		p = self.tileset.tsize

		#make a blank image
		wp = self.level.shape[0]*p
		hp = self.level.shape[1]*p
		levelIMG = Image.new("RGBA", (wp,hp))

		#make the map
		ss = self.tileset.spritesheet
		for hi in range(len(self.level)):
			for wi in range(len(self.level[0])):
				tp = (wi*p,hi*p,(wi+1)*p,(hi+1)*p)

				#get the tile and place on image at position
				tile = ss[self.level[hi][wi]]
				levelIMG.paste(tile,tp)

		return levelIMG

	#to string function of the level
	def __str__(self):
		s = ""
		for r in self.level:
			hex_tiles = [format(x,'x') for x in r]
			s += "".join(hex_tiles)
			s += "\n"

		return s.strip()

# CREATES A SQL ENTRY USING A TILESET, ASCII MAP, ID #, AND AUTHOR NAME
class SQLLevel:
	def __init__(self):
		self.dat = {}
		self.ascii_level = None

	#create a new JSON level
	def setLevel(self,tileset,asciimap,levelType,idNum=0,author=''):
		#set SQL data
		dat = {}
		dat['id'] = idNum
		dat['tileName'] = tileset.tileFile
		dat['levelType'] = levelType
		dat['author'] = author
		dat['ascii_map'] = asciimap
		dat['map_size'] = asciimap.level.shape[0]  #maps are square
		self.dat = dat

		#set other variables
		self.ascii_level = asciimap

	#export the level to a SQL entry in the database
	def exportSQLLevel(self):	
		levelType = self.dat['levelType']

		#ai generated level
		if levelType == 'gen':
			sql = "INSERT INTO gen_levels (ID, TILESET, ASCII_MAP, MAP_SIZE, MODEL_LOC, TIME_MADE) VALUES (null, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
			val = (self.dat['tileName'],str(self.dat['ascii_map']), str(self.dat['map_size']), self.dat['author'])
		#user made level
		else:
			sql = "INSERT INTO user_levels (ID, TILESET, ASCII_MAP, MAP_SIZE, AUTHOR, TIME_MADE) VALUES (null, %s, %s, %s, %s, CURRENT_TIMESTAMP)"
			val = (self.dat['tileName'],str(self.dat['ascii_map']), str(self.dat['map_size']), self.dat['author'])

		#run the command
		mycursor.execute(sql, val)
		mydb.commit()

		print(mycursor.rowcount, "record inserted.")
		

	#read in level data based on parameters 
	def importSQLLevel(self,levelType,idNum):
		if levelType == "gen":
			s = "SELECT ID, ASCII_MAP, MAP_SIZE, MODEL_LOC, TILESET FROM gen_levels WHERE ID = %s"
			v = (idNum,)
		else:
			s = "SELECT ID, ASCII_MAP, MAP_SIZE, AUTHOR, TILESET FROM user_levels WHERE ID = %s"
			v = (idNum,)

		#get the results from the command
		mycursor.execute(s,v)
		sqlRes = mycursor.fetchone()

		if sqlRes == None:
			print(f"** WARNING: Level ID [ {idNum} ] from [ {levelType} ] dataset not found! **")
			return False

		d = {}
		if levelType == "gen":
			d = dict(zip(["ID", "ASCII_MAP", "MAP_SIZE", "MODEL_LOC","TILESET"],sqlRes))
		else:
			d = dict(zip(["ID", "ASCII_MAP", "MAP_SIZE", "AUTHOR", "TILESET"],sqlRes))

		#setup the data
		ms = d['MAP_SIZE']
		t = Tileset(d['TILESET'])
		d_level = AsciiLevel(t,ms)
		d_level.importLevel(d['ASCII_MAP'])

		#set the level
		self.setLevel(t,d_level,levelType,d['ID'],(d['MODEL_LOC'] if levelType == 'gen' else d['AUTHOR']))

		return True

# SET OF SQL LEVELS IMPORTED FROM THE DATABASE FOR A GIVEN TILESET AND AUTHOR TYPE
class SQLLevelSet:
	def __init__(self,levelType,tileName=None):
		self.levelSet = []
		if tileName == None:
			self.importAllLevels(levelType)
		else:
			self.importTilesetLevels(levelType,tileName)

	#import a set of sql levels based on some criteria
	def importTilesetLevels(self,authorType,tileName):
		#get all ai levels
		if(authorType == "gen"):
			s = "SELECT ID, ASCII_MAP, MAP_SIZE, MODEL_LOC FROM gen_levels WHERE TILESET = %s"
			v = (tileName,)
		else:
			s = "SELECT ID, ASCII_MAP, MAP_SIZE, AUTHOR FROM user_levels WHERE TILESET = %s"
			v = (tileName,)

		#get the results from the command
		mycursor.execute(s,v)
		sqlRes = mycursor.fetchall()


		#remake data from results
		tiles = Tileset(tileName)
		for entry in sqlRes:
			#parse entry
			if (authorType == "gen"):
				d = dict(zip(["ID", "ASCII_MAP", "MAP_SIZE", "MODEL_LOC"],entry))
			else:
				d = dict(zip(["ID", "ASCII_MAP", "MAP_SIZE", "AUTHOR"],entry))


		  	#create new level from data
			ms = d['MAP_SIZE']
			d_level = AsciiLevel(tiles,ms)
			d_level.importLevel(d['ASCII_MAP'])

			#add the level
			new_level = SQLLevel()
			new_level.setLevel(tiles,d_level,authorType,d['ID'],(d['MODEL_LOC'] if authorType == 'gen' else d['AUTHOR']))
			self.levelSet.append(new_level)

	def importAllLevels(self,authorType):
		all_tilesets = ['zelda','pokemon','amongus','pacman','dungeon']

		#get all ai levels
		if(authorType == "gen"):
			s = "SELECT ID, ASCII_MAP, TILESET, MAP_SIZE, MODEL_LOC FROM gen_levels"
		else:
			s = "SELECT ID, ASCII_MAP, TILESET, MAP_SIZE, AUTHOR FROM user_levels"

		#get the results from the command
		mycursor.execute(s)
		sqlRes = mycursor.fetchall()


		#remake data from results
		tiles = {}
		for tilename in all_tilesets:
			tiles[tilename] = Tileset(tilename)

		for entry in sqlRes:
			#parse entry
			if (authorType == "gen"):
				d = dict(zip(["ID", "ASCII_MAP", "TILESET", "MAP_SIZE", "MODEL_LOC"],entry))
			else:
				d = dict(zip(["ID", "ASCII_MAP", "TILESET", "MAP_SIZE", "AUTHOR"],entry))


		  	#create new level from data
			ms = d['MAP_SIZE']
			d_level = AsciiLevel(tiles[d["TILESET"]],ms)
			d_level.importLevel(d['ASCII_MAP'])

			#add the level
			new_level = SQLLevel()
			new_level.setLevel(tiles[d["TILESET"]],d_level,authorType,d['ID'],(d['MODEL_LOC'] if authorType == 'gen' else d['AUTHOR']))
			self.levelSet.append(new_level)


MODE = "import"

# tester code
if __name__ == '__main__':
	#test all tilesheets
	for ts in ["zelda","amongus", "dungeon", "pacman", "pokemon"]:
		if MODE == "generate":
			#make the sprite tilesheet
			SS = Tileset(ts)
			print(SS.spritesheet)
			print(SS.num_tiles)

			#make a random level
			ASC_LEVEL = AsciiLevel(SS,[10,10])
			ASC_LEVEL.generateRandomLevel()
			al_img = ASC_LEVEL.makeLevelImg()
			al_img.show()
			print(str(ASC_LEVEL))

			#make a sql entry for the example
			S_FILE = SQLLevel()
			S_FILE.setLevel(SS,ASC_LEVEL,'gen')
			S_FILE.exportSQLLevel()
		else:
			
			print(f"# {ts} levels: {len(SQLS.levelSet)}")

			if len(SQLS.levelSet) > 0:
				level = random.choice(SQLS.levelSet)
				ASC_LEVEL = level.ascii_level
				al_img = ASC_LEVEL.makeLevelImg()
				print(f"\trandom level id: {level.dat['id']}")
				al_img.show()






