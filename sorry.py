import random
#print random.randint(0, 5)

colorsDict = {
  0: "Red",
  1: "Green",
  2: "Blue",
  3: "Yellow"  
}

def newDeck():
  cards = []

  #0 represents a sorry card
  for x in range(4):
    cards.append(0)
  for x in range(5):
    cards.append(1)
  for x in range(2, 6):
    for y in range(4):
      cards.append(x)
  for x in range(7, 9):
    for y in range(4):
      cards.append(x)
  for x in range(10, 13):
    for y in range(4):
      cards.append(x)
  random.shuffle(cards)

  #test
  #cards[0] = 2
  #cards[1] = 4
  #cards[5] = 12
  #end test

  return cards

class Piece:
  #color depends on index: 0-red, 1-yellow, 2-blue, 3-green
  #posn: 0-14 (starting at 0 at the spot before start)
  #colorSide: 0-3 (color), 4 (safe zone)
  def __init__(self, posn, colorSide):
    self.posn = posn
    self.colorSide = colorSide

class Game:
  #colorPieces: list of 4 lists of pieces outside start and home each representing their own color
  #startHomeData: array of startHomeData (0-7) - redStart, yellowStart, blueStart, greenStart, redHome, yellowHome, blueHome, greenHome
  #turn: 0-red, 1-yellow, 2-blue, 3-green
  #deck: array of ints representing cards
  def __init__(self):

    pieces = [[],[],[],[]]
    SHData = [4, 4, 4, 4, 0, 0, 0, 0]
    firstTurn = random.randint(0, 3)

    self.colorPieces = pieces
    self.startHomeData = SHData
    self.turn = firstTurn
    self.deck = newDeck()


  def pickupCard(self):
    if (len(self.deck) == 0):
      self.deck = newDeck()
    return self.deck.pop(0)
    

  #returns list of ints representing choices
  def getChoices(self, card):
    choices = []
    if (self.startHomeData[self.turn] > 0 and card == 0):
      numOtherOnBoard = 0
      for x in range(4):
        if (x != self.turn):
          lop = self.colorPieces[x]
          for y in range(len(lop)):
            if lop[y].posn < 15:
              numOtherOnBoard += 1
      for x in range(numOtherOnBoard):
        choices.append(x)
    else:
      if (card < 3 and self.startHomeData[self.turn] > 0):
        choices.append(-1)
      startHomeLength = self.startHomeData[self.turn] + self.startHomeData[self.turn + 4]
      if(startHomeLength < 4):
        for x in range(4 - startHomeLength):
          choices.append(x)
    return choices


  def pushbackStart(self, color):
    p = Piece(1, color)
    self.colorPieces[color].append(p)


  def movePiece(self, color, move, index):
    possibleHit = True
    if (index == -1):
      self.startHomeData[color] -= 1
      self.pushbackStart(self.turn)
      index = len(self.colorPieces[color]) - 1
    else:
      p = self.colorPieces[color][index]
      if move == 4:
        newPosn = p.posn - move
      else:
        newPosn = p.posn + move
      if (newPosn < 15 and newPosn >= 0):
        self.colorPieces[color][index].posn = newPosn
      elif (newPosn < 0):
        self.colorPieces[color][index].posn = newPosn + 15
        self.colorPieces[color][index].colorSide = (self.colorPieces[color][index].colorSide + 3) % 4
      elif (p.colorSide == (color + 3) % 4):
        possibleHit = False
        movesToSafe = self.colorPieces[color][index].posn + move
        if (movesToSafe >= 20):
          self.colorPieces[color].pop(index)
          self.startHomeData[color + 4] += 1
        elif (movesToSafe < 20):
          self.colorPieces[color][index].posn = movesToSafe
      else:
        self.colorPieces[color][index].posn = newPosn - 15
        self.colorPieces[color][index].colorSide = (self.colorPieces[color][index].colorSide + 1) % 4
    if (possibleHit):
      self.removeOnHit(index, self.colorPieces[color][index].posn, self.colorPieces[color][index].colorSide)


  def removeOnHit(self, thisIdx, psn, side):
    for x in range(4):
      for y in range(len(self.colorPieces[x])):
        if(x == self.turn and y == thisIdx):
          continue  
        pc = self.colorPieces[x][y]
        if (pc.posn == psn and pc.colorSide == side):
          self.startHomeData[x] += 1
          self.colorPieces[x].pop(y)
          return


  def pushbackSorry(self, color, index):
    if (self.startHomeData[color] > 0):
      i = -1
      for x in range(4):
        if (x == color):
          continue
        lop = self.colorPieces[x]
        for y in range(len(lop)):
          if lop[y].posn < 15:
            i += 1
          if (index == i):
            popped = self.colorPieces[x].pop(y)
            self.startHomeData[x] += 1
            break
      self.startHomeData[color] -= 1

      piece = Piece(popped.posn, popped.colorSide)
      self.colorPieces[color].append(piece)

  def changeTurn(self):
    self.turn = (self.turn + 1) % 4

  #returns boolean
  def isGameOver(self):
    for x in range(4):
      if (self.startHomeData[x + 4] == 4):
        return True
    return False

  def textPrint(self):
    for x in range(8):
      c = colorsDict[x % 4]
      print(c, end =" "),
      if (x > 3):
        print("Home:", end =" "),
      else:
        print("Start:", end =" "),
      print(self.startHomeData[x])

    board = [[0 for x in range(15)] for y in range(4)]

    homes = [[0 for x in range(5)] for y in range(4)]

    for x in range(4):
      for y in range(len(self.colorPieces[x])):
        psn = self.colorPieces[x][y].posn
        if (psn > 14):
          homes[(x + 3) % 4][psn - 15] = x + 1
        else:
          board[self.colorPieces[x][y].colorSide][psn] = x + 1

    for x in range(4):
      print(board[x])
    print("\n")

    for x in range(4):
      print(homes[x])



def playTextGame():
  g1 = Game()
  g1.textPrint()

  while(1):
    print(colorsDict[g1.turn] + " Turn!")
    input('Press enter to pick up a card')
    card = g1.pickupCard()
    print(card)
    print("Options: ")
    choices = g1.getChoices(card)

    if (choices):
      ch = int(input(choices))
      while ch not in choices:
        print("Bad Input")
        ch = int(input(choices))
      if (card == 0):
        g1.pushbackSorry(g1.turn, ch)
      else:
        g1.movePiece(g1.turn, card, ch)

      if(g1.isGameOver()):
        print(colorsDict(g1.turn) + "Wins!")
        break
      g1.textPrint()
    else:
      print("Unable to move")
      print("\n")
    
    if (card != 2):
      g1.changeTurn()

#playTextGame()
