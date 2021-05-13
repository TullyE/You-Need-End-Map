import gspread # pip install gspread
import json

import os

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

#with open('credentials1.json', 'w') as f:
#    json.dump(json.loads(os.environ.get('credentials')), f, indent=2)

gc = gspread.service_account_from_dict(json.loads(os.environ.get('credentials'))) 
sh = gc.open_by_key('1Y5YxgrpTuVgS_fkC4Te1ouMQbr7koCUIhVgJVBYsb-0')
worksheet = sh.sheet1




import discord
from discord.ext import commands

import numpy as np 
import math 

import string
alphabets = string.ascii_lowercase
bot = commands.Bot(command_prefix='$')
chars = ['/',',']

def player_input_one_coord(coord):
    error = False
    for letter in alphabets:
        if letter in coord:
            error = True
            break
    if error:
        return
    coord = coord.split([c for c in chars if c in coord][0]) #splits the message
    if '' in coord:
        return
    if len(coord) > 3 or len(coord) == 1:
        return
    if len(coord) == 3:
        del coord[1]
    return [int(c) for c in coord]

def player_input_two_coords(p_input):
    coords = p_input
    indexpos = 0
    error = False
    for letter in alphabets:
        if letter in coords:
            error = True
            break
    if error:
        return
    coord = coords.split(' ')
    for nums in coord:
        if indexpos < len(coord):
            coord[indexpos] = nums.split([c for c in chars if c in coords][0])
            indexpos += 1
    del coord[0]
    if len(coord[0]) != 2 or len(coord[1]) != 2:
        return
    ###coord = i.split([c for c in chars if c in i][0]) #original list comprehension
    if len(coord) > 2 or len(coord) < 2:
        return
    final = []
    final.append(coord[0][0])
    final.append(coord[0][1])
    final.append(coord[1][0])
    final.append(coord[1][1])
    return [int(c) for c in final]

def degree(num):
    return num*(180/math.pi)

@bot.event
async def on_message(message):

    #Variables
    TheMessage = message.content
    channel = message.channel

    if message.channel.name == '🔢》end-coords': #Channel you want bot to read

        if message.author.bot:
            return

        if message.content == '.help':
            await channel.send(".close returns the nearest end city to the coords you pass in \nTyping in coords adds them to the map")
            return


        ## downloads everything from the google sheets and runs the distance formula and saves the lowest distance and returns the coords of that distance
        if message.content.startswith('.close'):
            
            TheMessage = TheMessage[7:]

            try:
                playercord = player_input_one_coord(TheMessage)
            except:
                await channel.send("That's the wrong format! Try again!")
                return
            if not playercord:
                await channel.send("That's the wrong format! Try again!")
                return
            
            lowD = 1000000 
            x1 = playercord[0]
            z1 = playercord[1]
            TheValues = worksheet.get_all_values()
            del TheValues[0]
            for i in TheValues:
                x2 = int(i[0])
                z2 = int(i[1])
                #Distance Formula
                curD = math.sqrt(((x2-x1)**2) + ((z2-z1)**2))
                if curD < lowD:
                    lowD = curD
                await channel.send(f'{i[0]}/{i[1]} is the closest KNOWN end city to you!')
                return
        ## end of the .close command

        ## whenever a message is sent check if it's a coord... if it is upload to the map
        try:
            coord = player_input_one_coord(TheMessage)
        except:
            await channel.send("That's the wrong format! Try again!")
            return
        
        if not coord:
            await channel.send("That's the wrong format! Try again!")
            return
        else:
            worksheet.insert_row(coord, 2)
            embed = discord.Embed()
            embed.description = "Click [here](https://docs.google.com/spreadsheets/d/1Y5YxgrpTuVgS_fkC4Te1ouMQbr7koCUIhVgJVBYsb-0/edit#gid=0) to view the map.\n Made by: 3va and Pandarocket"
            await channel.send("Successfully added to the map!\n", embed=embed)
        ## end of the upload function

#New Text Channel

    ## check a different txt channel now
    if message.channel.name == '🌉》ingame-bridge':
        ## the .angle takes in messages checks if there are two coords and then returns the angle using trig.
        if '.angle' in message.content:
            ## Variables
            TheMessage = TheMessage.split('.angle')
            TheMessage = TheMessage[1]
            
            try:
                playercord = player_input_two_coords(TheMessage)
            except:
                await channel.send("That's the wrong format! Try again!")
                return
            if not playercord:
                await channel.send("That's the wrong format! Try again!")
                return
            
            #Sets vars to the numbers the user inputs for use in a math equation
            x1 = playercord[0]
            y1 = playercord[1]
            x2 = playercord[2]
            y2 = playercord[3]
            ydif = y2-y1
            xdif = x2-x1

            if x1 == x2 and y1 == y2:
                await channel.send("Go away! Don't talk to me again!")
                return

            if x1 == x2:
                if y2 - y1 > 0:
                    finaldeg = 0
                    await channel.send(f'Face South "{finaldeg}" for optimal travel path!')
                    return
                else:
                    finaldeg = 180
                    await channel.send(f'Face North "{finaldeg}" for optimal travel path!')
                    return

            if y1 == y2:
                if x2 - x1 > 0:
                    finaldeg = -90
                    await channel.send(f'Face East "{finaldeg}" for optimal travel path!')
                    return
                else:
                    finaldeg = 90
                    await channel.send(f'Face West "{finaldeg}" for optimal travel path!')
                    
            ####-MATH-####
            refangle = degree(np.arctan(abs(ydif)/abs(xdif))) - 90
            ####-MATH-####

            #the math returns some crazy numbers so the following code adjusts the angles and makes them reasonable.

            #Minecraft also uses some strange angles and so this code accounts for that as well
            finaldeg = 0
            if ydif > 0 and xdif > 0:
                finaldeg = refangle 
            if ydif > 0 and xdif < 0: 
                incompleteangle = 180-(180 - refangle)
                finaldeg = incompleteangle * -1
            if ydif < 0 and xdif < 0:
                finaldeg = 180 + refangle
            if ydif < 0 and xdif > 0:
                incompleteangle = -90 - refangle
                finaldeg = -90 + incompleteangle

            #sends final message and calculates what cardinal direction it is facing
            dirs = ['North-East', 'East', 'South-East', 'South', 'South-West', 'West', 'North-West']
            dirvar1 = -157.5
            dirvar2 = -112.5
            actdir = 0
            notmsg = True
            finaldeg = round(finaldeg, 1)
            while notmsg:
                if (finaldeg >= 157.5 and finaldeg <= 180) or (finaldeg >= -180 and finaldeg <= -157.5):
                    await channel.send(f'Face North "{finaldeg} for optimal travel path!')
                    return
                if finaldeg >= dirvar1 and finaldeg <= dirvar2:
                    await channel.send(f'Face {dirs[actdir]} "{finaldeg} for optimal travel path!')
                    notmsg = False
                    return
                else:
                    dirvar1 += 45
                    dirvar2 += 45
                    actdir += 1
        if '.add' in message.content:
            ## Variables
            TheMessage = TheMessage.split('.add')
            TheMessage = TheMessage[1]
            try:
                playercord = player_input_one_coord(TheMessage)
            except:
                await channel.send("That's the wrong format! Try again!")
                return
            if not playercord:
                await channel.send("That's the wrong format! Try again!")
                return
            else:
                worksheet.insert_row(playercord, 2)
                await channel.send("Successfully added to the map!\n ")
        if '.OWPortal' in message.content:
            TheMessage = TheMessage.split('.OWPortal')
            TheMessage = TheMessage[1]
            try:
                playercord = player_input_one_coord(TheMessage)
            except:
                await channel.send("That's the wrong format! Try again!")
                return
            if not playercord:
                await channel.send("That's the wrong format! Try again!")
                return
            else:
                await channel.send(f'Put a portal in the nether at {round(playercord[0]/8)}/{round(playercord[1]/8)}')
        if '.NPortal' in message.content:
            TheMessage = TheMessage.split('.NPortal')
            TheMessage = TheMessage[1]
            try:
                playercord = player_input_one_coord(TheMessage)
            except:
                await channel.send("That's the wrong format! Try again!")
                return
            if not playercord:
                await channel.send("That's the wrong format! Try again!")
                return
            else:
                await channel.send(f'Put a portal in the Overworld at {round(playercord[0]*8)}/{round(playercord[1]*8)}')
        return
                
bot.run(os.environ.get('DiscordToken')) 