#!/usr/bin/python
__author__ = 'Loto_Bak'
#
# lb_to_rcb V0.01 Alpha
# This program DELETES YOUR RCB DATABASE! YOU HAVE BEEN WARNED!
# This program might suck. Use at your own risk. Backup EVERYTHING.
# Converts LaunchBox XML to Rom Collection Browser sqlite database (overwrites it actually)
# Also copies LaunchBox Images to RCB compatable filenames.
#
# Edit the variables below to configure the tool
#
# Requirements:
#  All converted titles must have their corresponding emulator configured in RCB's config.xml
#  RCB database must exist
#  Windows (launchbox is windows anyways. This is mostly because the paths are windows style in my code. Should convert to *nix easily)
#
# Limitations
#  Only moves the first fanart and screenshot (RCB seems to only support 1 of each image type)
#  Regex for brackets likely needs some work
#  I ruin some utf8 encoding in an effort to keep sqlite happy. Should do a better job of this later. 
#
#
# Its quick and dirty. Dont expect much
# If you use the code give me credit.
# Feel free to update it or turn it into a command line tool.
# - Loto

import xml.etree.ElementTree as xmlize
from shutil import copy2 as cp
import os, re, sqlite3

launchbox_xml_path = "C:\\Users\\User\\LaunchBox\\LaunchBox.xml"
images_path = "C:\\Users\\User\\LaunchBox\\Images\\"
output_directory = "C:\\output\\"
sqllite_database_path = "C:\\Users\\User\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\script.games.rom.collection.browser\\MyGames.db"
RCB_config_path = "C:\\Users\\User\\AppData\\Roaming\\Kodi\\userdata\\addon_data\\script.games.rom.collection.browser\\config.xml"
add_rom_bracket_flags = True # add anything in () brackets back to the rom title. Helps with duplicate version identification
add_rom_square_bracket_flags = True # add anything in [] brackets back to rom title. Helps with duplicate version identification
remove_gooddump_flag = True # remove [!] from rom titles

conn = sqlite3.connect(sqllite_database_path)
c = conn.cursor()

c.execute('DELETE FROM Developer')
c.execute('DELETE FROM File')
c.execute('DELETE FROM Game')
c.execute('DELETE FROM Genre')
c.execute('DELETE FROM GenreGame')
c.execute('DELETE FROM Publisher')
c.execute('DELETE FROM Reviewer')
c.execute('DELETE FROM Year')
c.execute('VACUUM')
conn.commit()

collection_translation = {'3DO' : '3DO',
                            'Amiga' : 'Amiga',
                            'Amstrad CPC': 'Amstrad CPC',
                            'Atari 2600': 'Atari 2600',
                            'Atari 5200': 'Atari 5200',
                            'Atari 7800': 'Atari 7800',
                            'Colecovision': 'ColecoVision',
                            'Commodore 64': 'Commodore 64',
                            'Sega Dreamcast': 'Dreamcast',
                            'Nintendo Game Boy': 'Game Boy',
                            'Nintendo Game Boy Advance': 'Game Boy Advance',
                            'Nintendo Game Boy Color': 'Game Boy Color',
                            'Nintendo GameCube': 'GameCube',
                            'Sega Game Gear': 'Game Gear',
                            'Sega Genesis': 'Genesis',
                            'Sega Master System': 'SEGA Master System',
                            'Intellivision': 'Intellivision',
                            'Atari Jaguar': 'Jaguar',
                            'Mac OS': 'Macintosh',
                            'Arcade': 'MAME',
                            'MSX' : 'MSX',
                            'NeoGeo': 'Neo Geo',
                            'Nintendo Entertainment System (NES)': 'NES',
                            'Nintendo 64': 'Nintendo 64',
                            'Nintendo DS': 'Nintendo DS',
                            'Sony Playstation': 'PlayStation',
                            'Sony Playstation 2': 'PlayStation 2',
                            'Sony Playstation 3': 'PlayStation 3',
                            'Sony PSP': 'PSP',
                            'Sega 32X': 'SEGA 32X',
                            'Sega CD': 'SEGA CD',
                            'Sega Master System': 'SEGA Master System',
                            'Sega Saturn': 'SEGA Saturn',
                            'Super Nintendo (SNES)': 'SNES',
                            'TurboGrafx 16': 'TurboGrafx-16',
                            'Nintendo Virtual Boy': 'Virtual Boy',
                            'Nintendo Wii': 'Wii',
                            'PC': 'Windows',
                            'Microsoft Xbox': 'Xbox',
                            'Microsoft Xbox 360': 'Xbox 360',
                            'Sinclair ZX Spectrum': 'ZX Spectr'}

collection_ids = {}
rcb_config = xmlize.parse(RCB_config_path).getroot()
for romtype in rcb_config.findall('RomCollections')[0].findall('RomCollection'):
    collection_ids[romtype.get('name')] = romtype.get('id')

replaceable_characters = ["\\\\", ":", "'", "/"]
image_types = ['Back', 'Banner', 'Clear Logo', 'Fanart', 'Front', 'Screenshot', 'Steam Banner']
for type in image_types:
    if not os.path.isdir(output_directory + "\\" + type):
        os.makedirs(output_directory + "\\" + type)

xml = xmlize.parse(launchbox_xml_path).getroot()
limit1 = 10
count1 = 0
for row in xml.findall('Game'):
    try:
        title = row.findall('Title')[0].text.encode('charmap', 'replace').decode('utf8', 'replace').encode('ascii', 'replace')
        title_filename = title
        for c in replaceable_characters:
            title_filename = re.sub(c, "_", title_filename)
        path = row.findall('ApplicationPath')[0].text
        rom_filename = os.path.split(path)[-1]
        for c in replaceable_characters:
            rom_filename = re.sub(c, "_", rom_filename)
        try:
            notes = row.findall('Notes')[0].text.encode('charmap', 'replace').decode('utf8', 'replace').encode('ascii', 'replace')
        except:
            notes = ""
        platform = row.findall('Platform')[0].text
        #print platform
        if platform == "Arcade" or platform == None:
            continue
        print title_filename
        platform_path = platform
        for c in replaceable_characters:
            platform_path = re.sub(c, "_", platform_path)
        try:
            publisher = row.findall('Publisher')[0].text
        except:
            publisher = ""
        try:
            developer = row.findall('Developer')[0].text
        except:
            developer = ""
        try:
            rating = row.findall('Rating')[0].text 
        except:
            rating = ""
        try:
            releasedate = row.findall('ReleaseDate')[0].text
        except:
            releasedate = ""
        try:
            playmode = row.findall('PlayMode')[0].text
        except:
            playmode = ""
        try:
            genre = row.findall('Genre')[0].text
        except:
            genre = ""
    except:
        test = row
        print "failed" + row.findall('Title')[0].text
    c = conn.cursor()
    try:
        genre_list = genre.split(";")
    except:
        genre_list = []
    genre_ids = []
    for genre in genre_list:
        if genre != "" and genre != None:
            c = conn.cursor()
            a = c.execute('SELECT id FROM Genre WHERE name = ?', (genre,))
            data = c.fetchall()
            if len(data) < 1:
                a = c.execute('INSERT INTO Genre ("name") VALUES (?)', (genre,))
                conn.commit()
                a = c.execute('SELECT id FROM Genre WHERE name = ?', (genre,))
                genre_ids.append(c.fetchall()[0][0])
            else:
                genre_ids.append(data[0][0])
    c = conn.cursor()
    publisher_id = None
    if publisher != "" and publisher != None:
        a = c.execute('SELECT id FROM Publisher WHERE name = ?', (publisher,))
        data = c.fetchall()
        if len(data) < 1:
            a = c.execute('INSERT INTO Publisher ("name") VALUES (?)', (publisher,))
            conn.commit()
            a = c.execute('SELECT id FROM Publisher WHERE name = ?', (publisher,))
            publisher_id = c.fetchall()[0][0]
        else:
            publisher_id = data[0][0]
    c = conn.cursor()
    developer_id = None
    if developer != "" and developer != None:
        a = c.execute('SELECT id FROM Developer WHERE name = ?', (developer,))
        data = c.fetchall()
        if len(data) < 1:
            a = c.execute('INSERT INTO Developer ("name") VALUES (?)', (developer,))
            conn.commit()
            a = c.execute('SELECT id FROM Developer WHERE name = ?', (developer,))
            developer_id = c.fetchall()[0][0]
        else:
            developer_id = data[0][0]
    c = conn.cursor()
    try:
        year = releasedate[:4]
    except:
        year = None
    year_id = None
    if releasedate != "" and year != None:
        a = c.execute('SELECT id FROM Year WHERE name = ?', (year,))
        data = c.fetchall()
        if len(data) < 1:
            a = c.execute('INSERT INTO Year ("name") VALUES (?)', (year,))
            conn.commit()
            a = c.execute('SELECT id FROM Year WHERE name = ?', (year,))
            year_id = c.fetchall()[0][0]
        else:
            year_id = data[0][0]
        conn.commit()
    commited = False
    version = ""
    counter = 0
    title_addon = ""
    if add_rom_bracket_flags == True:
            try:
                title_addon = title_addon + " " + re.search('(\(.+\))', rom_filename).group(0)
            except:
                noop = 1
    if add_rom_square_bracket_flags == True:
            try:
                title_addon = title_addon + " " + re.search('(\[.+\])', rom_filename).group(0)
            except:
                noop = 1
    if remove_gooddump_flag:
        title_addon = title_addon.replace(" [!]", "")
        title_addon = title_addon.replace("[!]", "")
    while commited == False:
        try:
            a = c.execute('INSERT INTO Game ("name", "description", "romCollectionId", "publisherId", "yearId", "developerId") VALUES ( ?, ?, ?, ?, ?, ?)', (title + title_addon + version, notes, str(collection_ids[collection_translation[platform]]), publisher_id, year_id, developer_id))
            conn.commit()
            commited = True
        except:
            counter = counter + 1
            version = " (Copy " + str(counter) + ")"
            print "failed"
        if counter > 25:
            break
    a = c.execute('SELECT id FROM Game WHERE name = ? and romCollectionId = ?', (title + title_addon + version, str(collection_ids[collection_translation[platform]])))
    game_id = c.fetchall()[0][0]
    a = c.execute('INSERT INTO File ("name", "fileTypeId", "parentId") VALUES ( ?, ?, ?)', (os.path.abspath(path), 0, game_id))
    for genre_id in genre_ids:
        a = c.execute('INSERT INTO GenreGame ("genreId", "gameId") VALUES ( ?, ?)', (genre_id, game_id))
    conn.commit()
    if not os.path.isdir(output_directory + "\\"  + platform_path):
        os.makedirs(output_directory + "\\"  + platform_path)
    for type in image_types:
        if not os.path.isdir(output_directory + "\\"  + platform_path + "\\" + type):
            os.makedirs(output_directory + "\\"  + platform_path + "\\" + type)
        if type == "Screenshot" or type == "Fanart":
            modifier = "-01"
        else:
            modifier = ""
        if os.path.isfile(images_path + platform_path + "\\" + type + "\\" + title_filename + modifier + ".jpg"):
            cp(images_path + platform_path + "\\" + type + "\\" + title_filename + modifier + ".jpg", output_directory + platform_path + "\\" + type + "\\" + os.path.splitext(rom_filename)[0] + ".jpg")
        if os.path.isfile(images_path + platform_path + "\\" + type + "\\" + title_filename + modifier + ".png"):
            cp(images_path + platform_path + "\\" + type + "\\" + title_filename + modifier + ".png", output_directory + platform_path + "\\" + type + "\\" + os.path.splitext(rom_filename)[0] + ".png")

conn.close()
