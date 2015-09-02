

import time
import re
import math

#-----------------------------------------------------------------------
# Globals
#-----------------------------------------------------------------------

devMode = eval(getGlobalVariable('devMode'))

#setup 256 white space characters for usage with notifyBar
longSpace="                                                                "
longSpace=longSpace+longSpace+longSpace+longSpace

#Setup useful colors
highlight = {'faceoff':'#00C000', 'faceoffIgnored':'#006000', 'selection':'#C000FF'}
infoColor = '#000000'       #Used to inform of an action taken
errorColor = '#7F0000'      #Used for errors, player trying to do something illegal, etc.
warnColor = '#7F7F00'       #Used for warnings, unable to take an action, etc.
queryColor = '#00007F'      #Used to indicate action needs to be taken, select a card, etc.

#-----------------------------------------------------------------------
# Custom Exceptions
#-----------------------------------------------------------------------
class StaticAttributeError(TypeError):
	def __init__(self, *args):
		TypeError.__init__(self, *args)
        
class IncorrectCommandType(TypeError):
    def __init__(self, *args):
        TypeError.__init__(self, *args)
        
class ResponseTimeout(Exception):
    def __init__(self, *args):
        Exception.__init__(self, *args)
        
class NoEffectDeffined(NotImplementedError):
    def __init__(self, *args):
        NotImplementedError.__init__(self, *args)

#-----------------------------------------------------------------------
# Enumeration class
# Licensed under the GNU LGPL V3. See for more info:
# https://github.com/torrentails/Python-2.x-Enumeration-Class
#-----------------------------------------------------------------------
#Define the enum item class
class Enum_Item(object):
    _name = ''
    _type = ''
    _initiated = False
    def __init__(self, name, type):
        self._name = name
        self._type = type
        self._initiated = True
    def __getattr__(self, name):
        if name == 'name':
            return self._name
        if name == 'type':
            return self._type
        else: raise AttributeError("No such attribute on 'Enum_Item' object.", name)
    def __setattr__(self, name, value):
        if self._initiated:
            raise TypeError("'Enum_Item' object does not support attribute assignment", name, value)
        else: super(Enum_Item, self).__setattr__(name, value)

#Define the enum class
class Enum(object):
    _d = {}
    _name = ''
    _initiated = False
    def __init__(self, name, enums):
        if type(name) != str: raise ValueError("Invalid name for object 'Enum'", name)
        for i in enums:
            if type(i) != str: raise TypeError("Enum values must be a string.", i)
            if enums.count(i) > 1: raise ValueError("Duplicate values not allowed.", i)
            self._d[i.upper().replace(' ','')] = Enum_Item(i, name)
        self._name = name
        self._initiated = True
    def __getattr__(self, a):
        try:
            return self._d[a.upper()]
        except KeyError:
            raise AttributeError("No enum value defined.", a)
        else:
            raise
    def __setattr__(self, a, v):
        if self._initiated:
            raise TypeError("'Enum' object does not support attribute assignment")
        else: super(Enum, self).__setattr__(a, v)
    def __getitem__(self, k):
        return self._d[k.upper().replace(' ','')]
    def __name__(self):
        return self._name
    def __iter__(self):
        i = 0 
        l = self._d.values()
        while i < len(l):
            yield l[i]
            i+=1

#-----------------------------------------------------------------------
# Script loading and dispatcher functions
#-----------------------------------------------------------------------
    
def excecute(card, effectType, a={}, retVal=True):
    if   effectType == dispatch.onGameLoad:    e,p = OnGameLoad(card),True
    elif effectType == dispatch.activatedList: e,p = ActivatedList(card),True
    elif effectType == dispatch.activated:     e,p = Activated(card),False
    elif effectType == dispatch.checkPlay:     e,p = CheckPlay(card),True
    #TODO: PrePlayCard may be unnecessary; re-examine this when the core is more fleshed out.
    elif effectType == dispatch.prePlayCard:   e,p = PrePlayCard(card),True
    elif effectType == dispatch.entersPlay:    e,p = EntersPlay(card),False
    #TODO: Should we remove LeavesPlay as it can be set via events through EntersPlay?
    elif effectType == dispatch.leavesPlay:    e,p = LeavesPlay(card),False
    elif effectType == dispatch.flipped:       e,p = Flipped(card),False
    #TODO: Should we remove Moved as it can be set via events through EntersPlay?
    elif effectType == dispatch.moved:         e,p = Moved(card),False
    elif effectType == dispatch.uncovered:     e,p = Uncovered(card),False
    elif effectType == dispatch.confronted:    e,p = Confronted(card),False
    elif effectType == dispatch.replaced:      e,p = Replaced(card),False
    
    if e == "": return retVal
    if p or isPPPEnabled():
        whiteSpace = -1
        while e[0] == ' ':
            whiteSpace += 1
            e = e[1:]
        e = parseString(e, whiteSpace)
        a['card'] = card
        exec(e)
    else: addPPP(excecute, card, effectType, a, retVal)
    return retVal
    
def parseString(str, ws):
    if ws == -1: ws = 0
    l = re.split("(/;|/`|;;|`|;,|;\.|; )",str)
    for i in range(len(l)):
        if l[i] == r'/;':    l[i] = ';'
        elif l[i] == r'/`':  l[i] = '`'
        elif l[i] == r';;':  l[i] = '"'
        elif l[i] == r'`':   l[i] = "'"
        elif l[i] == r';,':  l[i] = '<'
        elif l[i] == r';.':  l[i] = '>'
        elif l[i] == r'; ':
            l[i] = "\n"
            try:
                l[i+1] = l[i+1][ws:]
            except: pass
    return "".join(l)

#-----------------------------------------------------------------------
# Arbitrary data system
#-----------------------------------------------------------------------

dataDict = {}

def readData(name, default=None):
    if name not in dataDict: return default
    return dataDict[name]

def popData(name, default=None):
    if name not in dataDict: return default
    return dataDict.pop(name)
    
def writeData(name, data):
    dataDict[name] = data
    
def reason(msg):
    writeData('reason', msg)

#-----------------------------------------------------------------------
# Context manager
#-----------------------------------------------------------------------

context = {}

def setContext(**kargs):
    global context
    context = kargs
    # remoteCall(players[1], setContext, [**kargs])
    
def clearContext():
    global context
    context = {}
    remoteCall(players[1], flushContext, [])

#-----------------------------------------------------------------------
# Internal helper functions
#-----------------------------------------------------------------------
        
def countTotalPower(player, col = "all", loc = table):
    power = 0
    if cards == table: getCardsInPlay(player)
    else: cards = getCardsAtLocation(loc, player)
    invert = False
    if col != 'all' and col.name[:3] == 'Non':
        col = color[col.name[:4]]
        invert = True
    for c in cards:
        if isCharacter(c):
            if col == 'all':
                power += max(Power(c)['power'], 0)
            else:
                colors = Colors(c)
                if invert:
                    if col not in colors:
                        power += max(Power(c)['power'], 0)
                elif col in colors:
                    power += max(Power(c)['power'], 0)
    return power
    
def giveControl(lst):
    lst[0].setController(lst[1])
    
def canChallenge(card, charactersInvolved=[], player=me):
    dict = {'card':card, 'player':player, 'canChallenge':False, 'charactersInvolved':charactersInvolved}
    if charactersInvolved == []:
        for c in getCardsAtLocation(loc, player):
            if isCharacter(c):
                dict['canChallenge'] = True
                dict['charactersInvolved'].append(c)
    else: dict['canChallenge'] = True
    applyModifiers(modifier.canChallenge, dict)
    return dict['canChallenge'], dict['charactersInvolved']
    
def canConfront(card, player=me):
    loc = getLocation(card)
    if card.controller == player: colorReqs = YourRequirements(card, {'player':player})
    else: colorReqs = OpponentsRequirements(card, {'player':player})
    for c in colorReqs.iterkeys():
        if c == color.wild: wildReq = [c, colorReqs[c]]
        elif countTotalPower(player, c, loc) < colorReqs[c]: return False
        
def canConfrontWithCards(card, cardList, player=me):
    #Setup the function locals we'll need
    cards = []
    loc = card.location
    if card.controller == player: colorReqs = YourRequirements(card, {'player':player})
    else: colorReqs = OpponentsRequirements(card, {'player':player})
    allGroupsSatisfied = True
    hasWildRequirement = False
    excessPower = 0

    #Build the list of card's we'll need, in the format we need
    for card in cardList:
        cards.append([card, Power(card), Colors(card), False])
        #The final value in the list is set to True if the card has multiple colors
        if cards[len(cards)][2] > 1: cards[len(cards)][3] = True

    for col in colorReqs.keys():
        #Pass if the color is wild, it'll be checked later
        if col == color.wild:
            hasWildRequirement = True
            continue
        #Setup the for-loop locals we'll need
        groupSatisfied = False
        group = []
        reqCol = colorReqs[col]
        indicesToRemove = []
        #Add cards that match the color requirement
        for i in range(len(cards)):
            if colorMatch(col, cards[i][2]):
                group.append(cards[i])
                indicesToRemove.append(i)
        #Remove matches so that they don't match twice
        for i in indicesToRemove.reverse():
            del cards[i]
        #Sort the matches so that those with fewer colors and lower power are checked first.
        group.sort(None, lambda x: len(x[2])*10+x[1])
        #Count card's power totals, and return the excess to the pool.
        indicesToRemove = []
        for card in group:
            if reqCol <= 0:
                cards.append(card)
                continue
            reqCol -= card[1]
            if reqCol <= 0: groupSatisfied = True
        #Check if the confront requirement has enough power
        if not groupSatisfied:
            allGroupsSatisfied = False
            break
        else: excessPower += math.fabs(reqCol)

    #Check any wild requirements
    if hasWildRequirement:
        groupSatisfied = False
        col = color.wild
        reqCol = colorReqs[col]
        #Count card's power totals.
        for card in cards:
            reqCol -= card[1]
            if reqCol <= 0:
                groupSatisfied = True
                break
        #Check if the confront requirement has enough power
        if not groupSatisfied: allGroupsSatisfied = False

    return allGroupsSatisfied

#Checks if a match occurs given a list of colors and a color to match to.
def colorMatch(colorToMatch, colorList, matchWild = False):
    if colorToMatch == color.wild:
        if matchWild == True or (len(colorList) == 1 and color.colorless in colorList): return True
    if colorToMatch.name[:3] == 'Non': return color[colorToMatch.name[:4]] not in colorList
    return colorToMatch in colorList
    
def getHomeLimit(player=me):
    manes = [c for c in getCardsInPlay(player) if cardType.maneCharacter in TypeList(c)]
    homeLimit = 0
    for card in manes:
        kw = Keywords(card)
        if keyword.homeLimit in kw:
            homeLimit += kw[keyword.homeLimit]
    dict = {'player':player, 'homeLimit':homeLimit}
    applyModifiers(modifier.homeLimit, dict)
    return dict['homeLimit']

#-----------------------------------------------------------------------
# Misc Helper functions
#-----------------------------------------------------------------------

def notifyAll(message, col=infoColor, alsoLog=True):
    mute()
    if alsoLog: notify(message)
    for p in players:
        remoteCall(p, 'notifyBar', [col,message+longSpace])
        
def whisperBar(message, col=infoColor):
    mute()
    notifyBar(col, message+longSpace)
    whisper(message)
    
# def isBoosted(card):
    # return card.alternate == "Mane Character Boosted"

def shuffle(group=None):
    if group: group.shuffle()
    else: me.deck.shuffle()

def isPhase(p):
    return phase[getGlobalVariable("Phase")] == p

def isMyPhase(p):
    return isPhase(p) and me.isActivePlayer()
    
# def isExhausted(card, truefalse):
    # typList = TypeList(card)
    # if cardType.resource in typList or cardType.troublemaker in typList or isCharacter(card):
        # if isInPlay(card):
            # return card.orientation & Rot90 == Rot90
    # if truefalse: return False
    # return None
    
# def isReady(card, truefalse=False):
    # ex = isExhausted(card, truefalse)
    # if ex == None:
        # if trueFalse: return False
        # else: return ex
    # return not ex
    
# def canExhaust(card):
    # if isReady(card, True) == True:
        # return applyModifiers(modifier.canExhaust, {'card':card, 'isReady':True})['isReady']
    # return False
    
# def canReady(card):
    # if isExhausted(card, True) == True:
        # return applyModifiers(modifier.canReady, {'card':card, 'isExhausted':True})['isExhausted']
    # return False
    
def exhaust(card):
    mute()
    if card.controller != me:
        remoteCall(card.controller, 'exhaust', [card])
        return
    if canExhaust(card):
        if not fireEvent(preEvent.exhaust, card=card):
            card.orientation = Rot90
            fireEvent(event.exhaust, card=card)
    
def ready(card):
    mute()
    if card.controller != me:
        remoteCall(card.controller, 'ready', [card])
        return
    if canReady(card):
        if not fireEvent(preEvent.ready, card=card):
            card.orientation = Rot0
            fireEvent(event.ready, card=card)

# def dismiss(cardList):
    # pass
    
# def isCharacter(card):
    # if cardType.friend in TypeList(card) or cardType.maneCharacter in TypeList(card):
        # return cardType.character
    # else: return False
    
def getTurnPlayer():
    return Player(eval(setGlobalVariable('turnPlayer')))
    
def draw(amount=1, player=me, note=True):
    mute()
    if player != me:
        remoteCall(player, 'draw', [amount, player, note])
        return
    deck = me.deck
    if len(deck) == 0:
        whisperBar("You don't have any cards in your {} to draw.".format(deck.name), warnColor)
        return
    dict={'amount':amount}
    applyModifiers(modifier.drawCard, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.draw, **dict):
            if len(deck) < dict['amount']:
                whisperBar("Ran out of cards in your {} to draw.".format(deck.name), errorColor)
                dict['amount'] = len(deck)
            disablePPP()
            for card in deck.top(dict['amount']):
                moveToLocation(card, location.hand)
                update()
                fireEvent(event.draw, **dict)
            enablePPP()
            if note:
                if dict['amount'] == 1: notifyAll("{} draws a card.".format(me))
                else: notifyAll("{} draws {} cards.".format(me,dict['amount']))
    
def discard(cardList):
    if type(cardList) != list: cardList = [cardList]
    for card in cardList:
        if not fireEvent(preEvent.discard, card=card):
            moveToLocation(card, location.discardPile)
            fireEvent(event.discard, card=card)

def gainAT(amount):
    dict = {'amount':amount}
    applyModifiers(modifier.gainAT, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.gainAT, **dict):
            me.counters['AT'].value += dict['amount']
            if dict['amount'] == 1: notifyAll("{} gains an Actions Token.".format(me))
            else: notifyAll("{} gains {} Actions Tokens.".format(me, dict['amount']))
            fireEvent(event.gainAT, **dict)
            
def loseAT(amount, spent=False):
    dict = {'amount':amount, 'spent':spent}
    applyModifiers(modifier.loseAT, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.loseAT, **dict):
            me.counters['AT'].value -= dict['amount']
            fireEvent(event.loseAT, **dict)

def spendAT(amount):
    loseAT(amount, True)

def gainPoints(amount):
    dict = {'amount':amount}
    applyModifiers(modifier.gainPoints, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.gainPoints, **dict):
            me.counters['Points'].value += dict['amount']
            if dict['amount'] == 1: notifyAll("{} gains a Point.".format(me))
            else: notifyAll("{} gains {} Points.".format(me, dict['amount']))
            fireEvent(event.gainPoints, **dict)

def losePoints(amount):
    dict = {'amount':amount}
    applyModifiers(modifier.losePoints, dict)
    if dict['amount'] > 0:
        if not fireEvent(preEvent.losePoints, **dict):
            me.counters['Points'].value += dict['amount']
            if dict['amount'] == 1: notifyAll("{} loses a Point.".format(me))
            else: notifyAll("{} loses {} Points.".format(me, dict['amount']))
            fireEvent(event.losePoints, **dict)

def uncover(card):
    if card.isFaceUp: return
    dict = {'card':card}
    applyModifiers(modifier.uncover, dict)
    if not fireEvent(preEvent.uncover, **dict):
        card.isFaceUp = True
        fireEvent(event.uncover, **dict)

def beginFaceoff(faceoffType, cardList):
    #TODO: Write faceoff code
    pass

def challangeTM(card, charactersInvolved=[]):
    can, lst = canChallange(card, charactersInvolved)
    if card not in lst: lst.append(card)
    if can: beginFaceoff(faceoff.troublemaker, lst)
    
def confront(card):
    #TODO: Write confront code
    pass
    
def replaceProblem(card, solved=True):
    #TODO: Write replacement code
    pass

