#-----------------------------------------------------------------------
#   Auto MLP CCG - Zone Management Subsystem
#   Copyright (c) 2015 Nathan Sullivan (email: contact@torrentails.com)
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program. If not, see http://www.gnu.org/licenses/
#-----------------------------------------------------------------------

#Define the standard card width and height for convenience
cardWidth = 84
cardHeight = 117
cardSep = cardWidth+int(cardWidth/6)*0

#Set up the zone boundaries
zones = {location.home:      {'char':   [{'orient': 'centre', 'y':195, 'max':11, 'sep':cardSep},
                                         {'orient': 'centre', 'y':-315, 'max':11, 'sep':cardSep}],
                              'res':    [{'orient': 'right', 'x':600, 'y':195, 'max':11, 'sep':cardSep},
                                         {'orient': 'left', 'x':-600, 'y':-315, 'max':11, 'sep':cardSep}],
                              'FUTM':   [{'orient': 'left', 'x':-600, 'y':195, 'max':11, 'sep':cardSep},
                                         {'orient': 'right', 'x':600, 'y':-315, 'max':11, 'sep':cardSep}],
                              'bounds': [{'x1':-610, 'y':190, 'x2':610, 'y2':400},
                                         {'x1':-610, 'y':-200, 'x2':610, 'y2':-370}]},
         location.myProblem: {'char':   [{'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep},
                                         {'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep}],
                              'res':    [{'orient': 'left', 'x':246, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                         {'orient': 'right', 'x':246+cardWidth, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                              'FDTM':   [{'orient': 'right', 'x':246+cardWidth, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                         {'orient': 'left', 'x':246, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                              'FUTM':   [{'orient': 'centre', 'y':-29-cardHeight, 'max':2, 'sep':cardSep},
                                         {'orient': 'centre', 'y':-29, 'max':2, 'sep':cardSep}],
                              'prob':   [{'orient': 'centre', 'y':-58, 'max':1, 'sep':cardHeight},    #problem loc: x:246 y:-58
                                         {'orient': 'centre', 'y':-59, 'max':1, 'sep':cardHeight}],   #problem loc x:-246 y:-59,
                              'bounds': [{'x1':0, 'y1':-200, 'x2':610, 'y2':190},
                                         {'x1':0, 'y1':-200, 'x2':610, 'y2':190}]},
         location.oppProblem:{'char':   [{'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep},
                                         {'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep}],
                              'res':    [{'orient': 'left', 'x':-246, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                         {'orient': 'right', 'x':-246+cardWidth, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                              'FDTM':   [{'orient': 'right', 'x':-246+cardWidth, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                         {'orient': 'left', 'x':-246, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                              'FUTM':   [{'orient': 'centre', 'y':-29-cardHeight, 'max':2, 'sep':cardSep},
                                         {'orient': 'centre', 'y':-29, 'max':2, 'sep':cardSep}],
                              'prob':   [{'orient': 'centre', 'y':-58, 'max':1, 'sep':cardHeight},    #problem loc: x:246 y:-58
                                         {'orient': 'centre', 'y':-59, 'max':1, 'sep':cardHeight}],   #problem loc x:-246 y:-59,
                              'bounds': [{'x1':-610, 'y1':-200, 'x2':0, 'y2':190},
                                         {'x1':-610, 'y1':-200, 'x2':0, 'y2':190}]}}

locations = {location.home:[], location.myProblem:[], location.oppProblem:[], location.deck:[], location.problemDeck:[], location.hand:[], location.discardPile:[], location.banishedPile:[], location.queue:[]}

def isTable(loc):
    return loc == location.home or loc == location.myProblem or loc == location.oppProblem
    
def updateLocations(key, val):
    locations[location[key]]=val
    
def syncLoactions():
    for p in players:
        for k in iter(locations):
            remoteCall(p, 'updateLocations', [k.name, locations[k]])

def getLocation(card):
    if card.group != table: return location[card.group.name]
    for k in iter(locations):
        if card._id in locations[k]: return k
    raise Exception("Card not in a group or not properly assigned.", card)
    
def getCardsAtLocation(loc, player=None):
    if player: return [card for card in locations[loc] if card.controller == player]
    return locations[loc]
    
def getGroupFromLocation(p, loc):
    if isTable(loc): return table
    if loc == location.hand: return p.hand
    if loc == location.deck: return p.deck
    return p.piles[loc.name]
    
def setLocation(card, loc, organize=True, sync=True):
    for k in iter(locations):
        l = locations[k]
        if k == loc:
            if card._id not in l:
                foundCard = len(l)
                for id in l:
                    if Name(Card(id)) == Name(card):
                        foundCard = l.index(id)
                        break
                l.insert(foundCard, card._id)
        elif card._id in l:
            l.remove(card._id)
        if organize: organizeZone(k)
    if sync: syncLoactions()
    
def moveToLocation(card, loc, index=None, trigger=True, sync=True):
    #TODO: add events and modifiers relating to card movement
    oldLoc = getLocation(card)
    if type(loc) == int:
        index = loc
        loc = oldLoc
    if oldLoc == loc:
        if index:
            if inPlay(card): card.setIndex(index)
            else: card.moveTo(card.group, index)
        return
    g = getGroupFromLocation(card.controller, loc)
    if g == table:
        card.moveToTable(0, 0)
        if index: card.setIndex(index)
    else:
        card.moveTo(g)
    setLocation(card, loc, sync=sync, organize=isTable(loc))

def inPlay(card=None):
    if card == None:
        return locations[location.home]+locations[location.myProblem]+locations[location.oppProblem]
    return isTable(getLocation(card))
            
def getLocationFromCords(x, y=None):
    if y == None:
        x,y = x.position
    invert = int(me.hasInvertedTable())
    for zone in iter(zones):
        z = zones[zone][invert]
        if z['x1'] < x < z['x2'] and z['y1'] < y < z['x2']: return zone
    
def organizeZone(loc):
    if not isTable(loc): return
    l = locations[loc]
    characters = []
    resources = []
    facedownTroublemakers = []
    faceupTroublemakers = []
    problems = []
    for id in l:
        card = Card(id)
        if card.controller == me:
            if isCharacter(card): characters.append(card)
            elif Type(card) == cardType.resource: resources.appen(card)
            elif Type(card) == cardType.troublemaker:
                if card.isFaceUp: faceupTroublemakers.append(card)
                else: facedownTroublemakers.append(card)
            elif Type(card) == cardType.problem: problems.append(card)
    organizeCardsInZone(loc, 'char', characters)
    organizeCardsInZone(loc, 'res', resources)
    organizeCardsInZone(loc, 'FDTM', facedownTroublemakers)
    organizeCardsInZone(loc, 'FUTM', faceupTroublemakers)
    organizeCardsInZone(loc, 'prob', problems)
    
def generateZonedCardList(lst, zmax):
    cardList = []
    cli = 0
    i1 = 0
    while i1 < len(lst):
        cardList.append([])
        i2 = 0
        while i2 < zmax:
            try:
                cardList[cli].append(lst[i1])
                i2 += 1
                i1 += 1
            except: i2 = zmax
        cli += 1
    return cardList
    
def organizeCardsInZone(loc, typ, lst):
    if lst == []: return
    zone = zones[loc][typ][int(me.hasInvertedTable())]
    bounds = zones[loc]['bounds'][int(me.hasInvertedTable())]
    if bounds['x1'] > bounds['x2']: zoneWidth = bounds['x1']-bounds['x2']
    else: zoneWidth = bounds['x2']-bounds['x1']
    zmax = zone['max']
    sep = zone['sep']
    cardList = generateZonedCardList(lst, zone['max'])
    
    if min(len(lst),zmax)%2 == 0: xoffset = int(zoneWidth/2)+bounds['x1']
    else: xoffset = int(zoneWidth/2)+bounds['x1']-int(sep/2)
    yoffset = zone['y']
    defXoffset = xoffset-cardWidth*int(zmax/2)
    
    positions = []
    for cli in range(len(cardList)):
        for i in range(len(cardList[cli])):
            if cli == 0:
                if i%2 == 0: positions.append([xoffset+(sep*int(i/2)), yoffset])
                else: positions.append([xoffset-(sep*int((i/2)+1)), yoffset])
            else:
                positions.append([xoffset, yoffset])
                xoffset += sep
        xoffset = (defXoffset+(int(sep/2)*(cli+1)))
        if me.hasInvertedTable(): yoffset -= int(cardHeight/3)
        else: yoffset += int(cardHeight/3)
    positions.sort(None, lambda v: (v[0]*0.001)+v[1])
    for i in range(len(lst)):
        card = lst[i]
        card.moveToTable(positions[i][0],positions[i][1])
        
#What did I intend this to do again?
def getPositionalX(posList, cardList, zoneDict, startIndex):
    pass