import time
import re

def onGameStartSetup():
    if not table.isTwoSided():
        notifyAll(errorColor, "Table not set to be 2-sided; please quit the game and ensure that 2-sided option in the lobby is enabled.")
        return
    setGlobalVariable('playingCard_player', 'None')
    setGlobalVariable('playingCard_card', 'None')
    setGlobalVariable('playingCard_cost', 'None')
    setGlobalVariable('firstPlayer', 'None')
    setGlobalVariable('isSetup', 'False')
    me.setGlobalVariable('deckLoaded', 'False')
    
def onDeckLoadSetup(player, groups):
    mute()
    update()
    cardList = []
    if not table.isTwoSided():
        notifyAll(errorColor, "Table not set to be 2-sided; please quit the game and ensure that 2-sided option in the lobby is enabled.")
        for card in cardList:
            card.delete()
        return
    for group in groups:
        for card in group:
            if card.owner == me: cardList.append(card)
    if not devMode:
        #Verify that the deck loaded is a valid deck
        if not verifyDeck(cardList): return
        #Ensure that there is another player present
        while len(players) <= 1:
            time.sleep(0.5)
            whisper("waiting for another player to join.")
    initializeCardDefaults(cardList) #Read and parse each card's data
    me.counters['Points'].value = 0
    if devMode: me.counters['AT'].value = 30
    else: me.counters['AT'].value = 0
    setupDeck(cardList)
    
    me.setGlobalVariable('deckLoaded', 'True')
    if eval(getGlobalVariable('isSetup')) == False:
        setGlobalVariable('isSetup', 'True')
        if not devMode:
            whisperBar(infoColor, "Waiting for opponent to load their deck.")
            return
    setGlobalVariable('isSetup', 'False')
    for p in players:
        remoteCall(p, 'revealStartingProblem', [])
    if not devMode:
        notifyAll(infoColor, "Both decks loaded, randomly determining starting player.")
        time.sleep(0.2)
        rolls=[rnd(1,6),rnd(1,6)]
        while rolls[0] == rolls[1]:
            notifyAll(queryColor, "Both players rolled a {}. Rolling again")
            time.sleep(0.2)
            rolls=[rnd(1,6),rnd(1,6)]
        p1 = rolls.index(max(rolls[0], roll[1]))
        p2 = rolls.index(min(rolls[0], roll[1]))
        notifyAll(infoColor, "{} rolled a {}, {} rolled a {}. {} gets the choice.".format(players[p1], rolls[p1], players[p2], rolls[p2], players[p1]))
        remoteCall(players[p1], 'chooseFirstPlayer', [])
    else: chooseFirstPlayer()
    
    
def verifyDeck(cardList):
    mute()
    noOfCards = 0
    noOfProblems = 0
    noOfStartProblems = 0
    noOfManes = 0
    cardNameListDeck = []
    cardNameListProblem = []
    peekList = []
    for card in cardList:
        if not card.isFaceUp:
            card.isFaceUp = True
            peekList.append(card)
    for card in cardList:
        cn = card.name
        if card.subtitle != '': cn += ', '+card.subtitle
        if card.type == 'Problem':
            noOfProblems += 1
            if re.search(r'Starting Problem', card.Keywords): noOfStartProblems += 1
            cardNameListProblem.append(cn)
        elif card.type == 'Mane Character': noOfManes += 1
        #TODO: check Quests and Strifes
        else:
            noOfCards += 1
            cardNameListDeck.append(cn)
            
    if eval(me.getGlobalVariable('deckLoaded')): whisperBar(errorColor, "You already have a deck loaded. Please restart the game before loading another deck.")
    elif noOfCards < 45: whisperBar(errorColor, "Only {} cards found in your deck, you need at least 45. Please load a valid deck".format(noOfCards))
    elif noOfProblems != 10: whisperBar(errorColor, "{} cards found in your problem deck, you need exactly 10. Please load a valid deck".format(noOfProblems))
    elif noOfStartProblems < 1: whisperBar(errorColor, "No starting problems found in your problem deck, you need at least 1. Please load a valid deck".format(noOfProblems))
    elif noOfManes != 1: whisperBar(errorColor, "{} Manes found, you need exactly 1. Please load a valid deck".format(noOfCards))
    else:
        errorFound = False
        for cardName in cardNameListDeck:
            if cardNameListDeck.count(cardName) > 3:
                whisperBar(errorColor, "Too many of {} found. Please load a valid deck".format(cardName))
                errorFound = True
                break
        for cardName in cardNameList:
            if cardNameList.count(cardName) > 2:
                whisperBar(errorColor, "Too many of {} found. Please load a valid deck".format(cardName))
                errorFound = True
                break
        if not errorFound:
            for c in peekList: c.isFaceUp = False
            return True
    
    for card in cardList:
        card.delete()
    return False
    
def setupDeck(cardList):
    for card in cardList:
        if Type(card) == cardType.maneCharacter: moveToLocation(card, location.home, trigger=False, sync=False)
        elif Type(card) == cardType.problem: moveToLocation(card, location.problemDeck, trigger=False, sync=False)
        else: moveToLocation(card, location.deck, trigger=False, sync=False)
            
    startingProblemList = []
    for card in me.piles['Problem Deck']:
        if keyword.startingProblem in Keywords(card):
            foundDuplicate = False
            for sp in startingProblemList:
                if Name(sp) == Name(card): foundDuplicate = True
            if not foundDuplicate: startingProblemList.append(card)
    if len(startingProblemList) == 1:
        sellectedStartingProblem = startingProblemList[0]
    else:
        buttonList = []
        for card in startingProblemList:
            buttonText = Name(card)+':\nYour Req:'
            yourReq = YourRequirements(card)
            oppReq = OpponentsRequirements(card)
            for prop in iter(yourReq):
                buttonText += ' ' + prop.name + ' ' + str(yourReq[prop])
            buttonText += '\nOpposing Req:'
            for prop in iter(oppReq):
                buttonText += ' ' + prop.name + ' ' + str(oppReq[prop])
            buttonList.append(buttonText)
                
        num = askChoice("Choose your Starting Problem:", buttonList)
        sellectedStartingProblem = startingProblemList[num - 1]
    
    if me.hasInvertedTable():
        sellectedStartingProblem.moveToTable(-246,-59, True)
    else:                
        sellectedStartingProblem.moveToTable(246,-58, True)
    setLocation(sellectedStartingProblem, location.myProblem, sync=False)
    
    shuffle(me.piles['Problem Deck'])
    shuffle()
    me.setGlobalVariable('deckLoaded', 'True')
    update()
    
def revealStartingProblem():
    mute()
    for card in table:
        if Type(card) == cardType.problem and card.owner == me: card.isFaceUp = True
    update()
    
def chooseFirstPlayer():
    if len(players) < 2 and devMode: setGlobalVariable('firstPlayer', str(me._id)); continueSetup(); return
    choice = not confirm("Would you like to go first?")
    setGlobalVariable('firstPlayer', str(players[int(choice)]._id))
    for p in players:
        remoteCall(p, 'continueSetup', [])
        
def continueSetup():
    mute()
    if devMode:
        if len(me.Deck) < 6:
            drawAmount = len(me.Deck)
        else: drawAmount = 6
    else: drawAmount = 6
    
    for card in me.Deck.top(drawAmount):
        moveToLocation(card, location.hand, trigger=False, sync=False)
    notifyAll(infoColor, "{} draws their opening hand.".format(me))
    update()
    if confirm("Do you wish to mulligan?"):
        for card in me.hand:
            moveToLocation(card, location.deck, trigger=False, sync=False)
        shuffle()
        update()
        for card in me.Deck.top(drawAmount):
            moveToLocation(card, location.hand, trigger=False, sync=False)
        update()
        notifyAll(infoColor, "{} mulligans their hand.".format(me))
    
    syncLoactions()
    if eval(getGlobalVariable('isSetup')) == False:
        setGlobalVariable('isSetup', 'True')
        if not devMode:
            whisperBar(infoColor, "Waiting for opponent to choose if they want to mulligan.")
            return
        
    firstPlayer = Player(eval(getGlobalVariable('firstPlayer')))
    setGlobalVariable('turnPlayer', str(firstPlayer._id))
    remoteCall(firstPlayer, 'startGame', [])
    
def startGame():
    _startTurn()