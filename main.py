import discord
import os

import sorry

client = discord.Client()

channel_id = 815809705695117323

colorEmoteDict = {
    0: "🔴",
    1: "🟢",
    2: "🔵",
    3: "🟡"
}

numberEmoteDict = {
    -1: "👨‍👩‍👧‍👦",
    0: "1️⃣",
    1: "2️⃣",
    2: "3️⃣",
    3: "4️⃣",
    4: "5️⃣",
    5: "6️⃣",
    6: "7️⃣",
    7: "8️⃣",
    8: "9️⃣",
    9: "🔟",
    10: "🕚",
    11: "🕛"
}

familyEmoteDict = {
    0: "⚪",
    1: "🙍‍♂️",
    2: "👩‍👦",
    3: "👨‍👩‍👦",
    4: "👨‍👩‍👧‍👦"
}


#global variables:
numReady = 0
g1 = sorry.Game()

gameStarted = False
gameOver = False
isFirstPhase = True
canMove = True
card = 0

#type $clear to clear all messages in channel
@client.event
async def on_message(message):
    if message.content == "$clear":
        await message.channel.purge()

    

    for guild in client.guilds:
        roleDict = {
            0: discord.utils.get(guild.roles, name="RED"),
            1: discord.utils.get(guild.roles, name="GREEN"),
            2: discord.utils.get(guild.roles, name="BLUE"),
            3: discord.utils.get(guild.roles, name="YELLOW")
        }


        for member in guild.members:
            print(member)
            for x in range(4):
                await member.remove_roles(roleDict[x])

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    channel = client.get_channel(channel_id)
    descr = "React to this message to choose a color and start playing!"
    embedStart = discord.Embed(title="MY BAD", description=descr, color=0x00ff00)
    message = await channel.send(embed=embedStart)

    global msg_id
    msg_id = message.id


    await message.add_reaction(emoji='🔴') 
    await message.add_reaction(emoji='🟢')
    await message.add_reaction(emoji='🔵')
    await message.add_reaction(emoji='🟡')
    await message.add_reaction(emoji='✅')



@client.event
async def on_raw_reaction_add(payload):

    channel = client.get_channel(channel_id)
    message_id = payload.message_id
    global msg_id
    if message_id != msg_id:
        return


    global gameStarted
    global isFirstPhase
    global card
    global canMove

    guild_id = payload.guild_id
    guild = discord.utils.find(lambda g : g.id == guild_id, client.guilds)

    roleDict = {
        0: discord.utils.get(guild.roles, name="RED"),
        1: discord.utils.get(guild.roles, name="GREEN"),
        2: discord.utils.get(guild.roles, name="BLUE"),
        3: discord.utils.get(guild.roles, name="YELLOW")
    }

    userRole = discord.utils.get(guild.roles,name="sorrybot")
    member = payload.member

    if gameStarted:
        if roleDict[g1.turn] not in member.roles:
            return

    if userRole in member.roles:
        return

    if gameStarted and isFirstPhase and canMove:
        if card == 0:
            for x in range(12):
                if payload.emoji.name == numberEmoteDict[x]:
                    g1.pushbackSorry(g1.turn, x)
                    break
        else:
            for x in range(5):
                if payload.emoji.name == numberEmoteDict[x-1]:
                    g1.movePiece(g1.turn, card, x-1)
                    break
    canMove = True

    if not gameStarted:

        roleReaction = True

        if payload.emoji.name == '🔴':
            role = roleDict[0]
        elif payload.emoji.name == '🟢':
            role = roleDict[1]
        elif payload.emoji.name == '🔵':
            role = roleDict[2]
        elif payload.emoji.name == '🟡':
            role = roleDict[3]
        elif payload.emoji.name == '✅':
            roleReaction = False
            global numReady
            numReady += 1
        else:
            roleReaction = False

        if roleReaction:
            await member.add_roles(role)

    if numReady >= 1:
        gameStarted = True

    if gameStarted:
        if isFirstPhase:
            if card != 2:
                g1.changeTurn()
            await channel.send(roleDict[g1.turn].mention)
            await colorTurnPhase(channel, payload)
        else:
            await optionsPhase(channel, payload)
        if g1.isGameOver():
            await printGameOverMessage(channel)

    
async def colorTurnPhase(channel, payload):
    descr = printBoard(0)
    global g1
    colCircle = colorEmoteDict[g1.turn]
    turnTitle = colCircle + " " + sorry.colorsDict[g1.turn] + " Turn! " + colCircle
    embedVar = discord.Embed(title=turnTitle, description=descr[0], color=0x00ff00)
    embedVar.add_field(name=descr[1], value="React with ✅ to pickup a card", inline=False)
    message = await channel.send(embed=embedVar)
    global msg_id
    msg_id = message.id

    await message.add_reaction(emoji='✅')

    global isFirstPhase
    isFirstPhase = False

async def optionsPhase(channel, payload):
    global g1 #these globals not needed?
    global card
    card = g1.pickupCard()
    choices = g1.getChoices(card)
    
    cardStr = str(card)
    if card == 0:
        cardStr = "My Bad!"
        descr = printBoard(-1)
    else:
        descr = printBoard(1)
    
    embedVar = discord.Embed(title="Card: " + cardStr, description=descr[0], color=0x00ff00)
    nm = "Options:"
    if not choices:
        nm = "Unable to move"
        global canMove
        canMove = False
    embedVar.add_field(name=descr[1], value=nm, inline=False)
    message = await channel.send(embed=embedVar)
    global msg_id
    msg_id = message.id
    for x in choices:
        await message.add_reaction(emoji=numberEmoteDict[x]) 
    if not canMove:
        await message.add_reaction(emoji='✅')

    global isFirstPhase
    isFirstPhase = True


async def printGameOverMessage(channel):
    winColor = "@" + sorry.colorsDict(g1.turn) + " Wins!"
    embedVar = discord.Embed(title="MY BAD", description=winColor, color=0x00ff00)
    await channel.send(embed=embedVar)

#returns hashcode of the space on the board
def hash(isSafe, x, y):
    if isSafe:
        return (x * 5 + y) * -1
    else:
        return x * 15 + y

#prints a list of size 2 containing a string of the first 13 line and a string of the last 2 lines
#showOptions: -1 if sorry, 0 if not moving, 1 if normal move of own pieces
def printBoard(showOptions):
    
    global g1
    g1.textPrint()
    sfr=sfg=sfb=sfy=r=g=b=yl=0
    
    str1 = ""
    str2 = ""

    if showOptions != 0:
        optionsDict = { }
        numInDict=0

    board = [[0 for x in range(15)] for y in range(4)]

    safes = [[0 for x in range(5)] for y in range(4)]

    for x in range(4):
      for y in range(len(g1.colorPieces[x])):
        psn = g1.colorPieces[x][y].posn
        if (psn > 14):
            newX = x
            newY = psn - 15
            safes[newX][newY] = x + 1
        else:
            newX = g1.colorPieces[x][y].colorSide
            newY = psn
            board[newX][newY] = x + 1
        if (showOptions == -1 and g1.turn != x and psn < 15) or (showOptions == 1 and g1.turn == x):
            optionsDict[hash(psn > 14, newX, newY)] = numInDict
            numInDict += 1

    for x in range(16):
        line = ""
        for y in range(16):
            #edge space
            if x==0 or x==15 or y==0 or y==15:
                if (y>2 and x==0) or (y==15 and x<3):
                    row = 0
                    col = r
                    c = board[row][col]
                    if c > 0:
                        key = hash(False, row, col)
                        if showOptions != 0 and key in optionsDict:
                            line+=numberEmoteDict[optionsDict[key]]
                        else:
                            line+=colorEmoteDict[c-1]
                    else:
                        line+="🟪"      #"r" + str(r)
                    r+=1
                elif y==15 or (x==15 and y>12):
                    
                    #pt.1 need to reverse these bc im printing left to right
                    swp = 0
                    if g == 14:
                        swp = -2
                    elif g == 12:
                        swp = 2
                    row = 1
                    col = g + swp
                    c = board[row][col]
                    if c > 0:
                        key = hash(False, row, col)
                        if showOptions != 0 and key in optionsDict:
                            line+=numberEmoteDict[optionsDict[key]]
                        else:
                            line+=colorEmoteDict[c-1]
                    else:
                        line+="🟪"      #"g" + str(g+swp)
                    #pt.2 need to reverse these back bc im printing left to right
                    g+=1
                elif x==15 or (y==0 and x>12):
                    c = board[2][14 - b]
                    row = 2
                    col = 14 - b
                    c = board[row][col]
                    if c > 0:
                        key = hash(False, row, col)
                        if showOptions != 0 and key in optionsDict:
                            line+=numberEmoteDict[optionsDict[key]]
                        else:
                            line+=colorEmoteDict[c-1]
                    else:
                        line+="🟪"      #"b" + str(14-b)
                    b+=1
                else:
                    swp = 0
                    if yl == 0:
                        swp = -2
                    elif yl == 2:
                        swp = 2
                    row = 3
                    col = 14 - yl + swp
                    c = board[row][col]
                    if c > 0:
                        key = hash(False, row, col)
                        if showOptions != 0 and key in optionsDict:
                            line+=numberEmoteDict[optionsDict[key]]
                        else:
                            line+=colorEmoteDict[c-1]
                    else:
                        line+="🟪"      #"y" + str(14-yl+swp)
                    yl+=1

            #safe zones
            elif y==2 and x<6:
                row = 0
                col = sfr
                c = safes[row][col]
                if c > 0:
                    key = hash(True, row, col)
                    if showOptions != 0 and key in optionsDict:
                        line+=numberEmoteDict[optionsDict[key]]
                    else:
                        line+=colorEmoteDict[c-1]
                else:
                    line+="🟥"
                sfr+=1
            elif x==2 and y>9:
                row = 1
                col = 4 - sfr
                c = safes[row][col]
                if c > 0:
                    key = hash(True, row, col)
                    if showOptions != 0 and key in optionsDict:
                        line+=numberEmoteDict[optionsDict[key]]
                    else:
                        line+=colorEmoteDict[c-1]
                else:
                    line+="🟩"
                sfg+=1
            elif y==13 and x>9:
                row = 2
                col = 4 - sfb
                c = safes[row][col]
                if c > 0:
                    key = hash(True, row, col)
                    if showOptions != 0 and key in optionsDict:
                        line+=numberEmoteDict[optionsDict[key]]
                    else:
                        line+=colorEmoteDict[c-1]
                else:
                    line+="🟦"
                sfb+=1
            elif x==13 and y<6:
                row = 3
                col = sfy
                c = safes[row][col]
                if c > 0:
                    key = hash(True, row, col)
                    if showOptions != 0 and key in optionsDict:
                        line+=numberEmoteDict[optionsDict[key]]
                    else:
                        line+=colorEmoteDict[c-1]
                else:
                    line+="🟨"
                sfy+=1

            #home or start
            elif x==1 and y==4:
                line+=familyEmoteDict[g1.startHomeData[0]]
            elif x==4 and y==14:
                line+=familyEmoteDict[g1.startHomeData[1]]
            elif x==14 and y==11:
                line+=familyEmoteDict[g1.startHomeData[2]]
            elif x==11 and y==1:
                line+=familyEmoteDict[g1.startHomeData[3]]
            elif x==6 and y==2:
                line+=familyEmoteDict[g1.startHomeData[4]]
            elif x==2 and y==9:
                line+=familyEmoteDict[g1.startHomeData[5]]
            elif x==9 and y==13:
                line+=familyEmoteDict[g1.startHomeData[6]]
            elif x==13 and y==6:
                line+=familyEmoteDict[g1.startHomeData[7]]

            else:
                line+="⬛"
        if x != 15:
            line+="\n"
        if x<12:
            str1 += line
        else:
            str2 += line
    return [str1, str2]


client.run(os.getenv('TOKEN'))
