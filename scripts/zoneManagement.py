#TODO: Clean this mess up
#TODO: Investigate occasional zone issues when playing friends.
#Define the standard card width and height for convenience
cardWidth = 84
cardHeight = 117
cardSep = cardWidth+int(cardWidth/6)*0

#Set up the zone boundaries
zones = {location.home:      {cardType.character:       [{'orient': 'centre', 'y':195, 'max':11, 'sep':cardSep},
                                                         {'orient': 'centre', 'y':-315, 'max':11, 'sep':cardSep}],
                              cardType.resource:        [{'orient': 'right', 'x':600, 'y':195, 'max':11, 'sep':cardSep},
                                                         {'orient': 'left', 'x':-600, 'y':-315, 'max':11, 'sep':cardSep}],
                              cardType.troublemaker:    [[{'orient': 'left', 'x':-600, 'y':195, 'max':11, 'sep':cardSep},
                                                          {'orient': 'right', 'x':600, 'y':-315, 'max':11, 'sep':cardSep}],
                                                         [{'orient': 'left', 'x':-600, 'y':195, 'max':11, 'sep':cardSep},
                                                          {'orient': 'right', 'x':600, 'y':-315, 'max':11, 'sep':cardSep}]],
                              'bounds': [{'x1':-610, 'y1':190, 'x2':610, 'y2':400},
                                         {'x1':-610, 'y1':-200, 'x2':610, 'y2':-370}]},
         location.myProblem: {cardType.character:       [{'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep},
                                                         {'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep}],
                              cardType.resource:        [{'orient': 'left', 'x':246, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                                         {'orient': 'right', 'x':246+cardWidth, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                              cardType.troublemaker:    [[{'orient': 'right', 'x':246+cardWidth, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                                          {'orient': 'left', 'x':246, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                                                         [{'orient': 'centre', 'y':-29-cardHeight, 'max':2, 'sep':cardSep},
                                                          {'orient': 'centre', 'y':-29, 'max':2, 'sep':cardSep}]],
                              cardType.problem:         [{'orient': 'centre', 'y':-58, 'max':1, 'sep':cardHeight},    #problem loc: x:246 y:-58
                                                         {'orient': 'centre', 'y':-59, 'max':1, 'sep':cardHeight}],   #problem loc x:-246 y:-59,
                              'bounds': [{'x1':0, 'y1':-200, 'x2':610, 'y2':190},
                                         {'x1':0, 'y1':-200, 'x2':610, 'y2':190}]},
         location.oppProblem:{cardType.character:       [{'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep},
                                                         {'orient': 'centre', 'y':30, 'max':5, 'sep':cardSep}],
                              cardType.resource:        [{'orient': 'left', 'x':-246, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                                         {'orient': 'right', 'x':-246+cardWidth, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                              cardType.troublemaker:    [[{'orient': 'right', 'x':-246+cardWidth, 'y':-29, 'max':4, 'sep':int(cardWidth/2)},
                                                          {'orient': 'left', 'x':-246, 'y':-29-cardHeight, 'max':4, 'sep':int(cardWidth/2)}],
                                                         [{'orient': 'centre', 'y':-29-cardHeight, 'max':2, 'sep':cardSep},
                                                          {'orient': 'centre', 'y':-29, 'max':2, 'sep':cardSep}]],
                              cardType.problem:         [{'orient': 'centre', 'y':-58, 'max':1, 'sep':cardHeight},    #problem loc: x:246 y:-58
                                                         {'orient': 'centre', 'y':-59, 'max':1, 'sep':cardHeight}],   #problem loc x:-246 y:-59,
                              'bounds': [{'x1':-610, 'y1':-200, 'x2':0, 'y2':190},
                                         {'x1':-610, 'y1':-200, 'x2':0, 'y2':190}]}}

locations = [{location.home:[], location.myProblem:[], location.oppProblem:[], location.deck:[], location.problemDeck:[], location.hand:[], location.discardPile:[], location.banishedPile:[], location.queue:[]},
{location.home:[], location.myProblem:[], location.oppProblem:[], location.deck:[], location.problemDeck:[], location.hand:[], location.discardPile:[], location.banishedPile:[], location.queue:[]},
{location.home:[], location.myProblem:[], location.oppProblem:[], location.deck:[], location.problemDeck:[], location.hand:[], location.discardPile:[], location.banishedPile:[], location.queue:[]}]

def isTable(loc):
    return loc == location.home or loc == location.myProblem or loc == location.oppProblem
    
def updateLocations(playerID, key, val):
    if playerID != me._id: locations[1][location[key]]=val
    for id in val:
        if id not in locations[2][location[key]]:
            locations[2][location[key]].append(id)
    
def syncLoactions():
    for p in players:
        for k in iter(locations[0]):
            remoteCall(p, 'updateLocations', [p._id, k.name, locations[0][k]])

def getLocation(card):
    if card.group != table: return location[card.group.name]
    for k in iter(locations[2]):
        if card._id in locations[2][k]: return k
    raise KeyError("Card not in a group or not properly assigned.", Name(card), card._id, card)
    
def getCardsAtLocation(loc, player=None):
    if player: return [card for card in locations[2][loc] if card.controller == player]
    return locations[2][loc]
    
def getCardsInPlay(player=None):
    lst = locations[2][location.home]+locations[2][location.myProblem]+locations[2][location.oppProblem]
    lst = [Card(c) for c in lst]
    if player: return [c for c in lst if c.controller == player]
    return lst

# def isInPlay(card=None):
    # return isTable(getLocation(card))
            
def getLocationFromCords(x, y=None):
    if y == None:
        x,y = x.position
    invert = int(me.hasInvertedTable())
    for zone in iter(zones):
        z = zones[zone]['bounds'][invert]
        if z['x1'] < x < z['x2'] and z['y1'] < y < z['y2']: return zone
    
def getGroupFromLocation(loc, player=me):
    if isTable(loc): return table
    if loc == location.hand: return player.hand
    if loc == location.deck: return player.deck
    return player.piles[loc.name]
    
def setLocation(card, loc, organize=True, sync=True):
    for k in iter(locations[0]):
        l = locations[0][k]
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
    for p in range(len(locations)):
        z = {}
        for l in locations[p]:
            z[l.name]=[]
            for c in locations[p][l]:
                z[l.name].append(Name(Card(c)))

def moveToLocation(card, loc, index=None, trigger=True, sync=True):
    #TODO: add events and modifiers relating to card movement
    oldLoc = getLocation(card)
    if type(loc) == int:
        index = loc
        loc = oldLoc
    if oldLoc == loc:
        if index:
            if isInPlay(card): card.setIndex(index)
            else: card.moveTo(card.group, index)
        return
    g = getGroupFromLocation(card.controller, loc)
    if g == table:
        card.moveToTable(0, 0)
        if index: card.setIndex(index)
    else:
        card.moveTo(g)
    setLocation(card, loc, sync=sync, organize=isTable(loc))
    
def organizeZone(loc):
    if not isTable(loc): return
    l = locations[0][loc]
    characters = []
    resources = []
    facedownTroublemakers = []
    faceupTroublemakers = []
    problems = []
    for id in l:
        card = Card(id)
        if card.controller == me:
            if isCharacter(card): characters.append(card)
            elif Type(card) == cardType.resource: resources.append(card)
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
    if typ == 'char': zone = zones[loc][cardType.character][int(me.hasInvertedTable())]
    elif typ == 'res': zone = zones[loc][cardType.resource][int(me.hasInvertedTable())]
    elif typ == 'FDTM': zone = zones[loc][cardType.troublemaker][0][int(me.hasInvertedTable())]
    elif typ == 'FUTM': zone = zones[loc][cardType.troublemaker][1][int(me.hasInvertedTable())]
    elif typ == 'prob': zone = zones[loc][cardType.problem][int(me.hasInvertedTable())]
    
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
        
def repositionCard(card, loc):
    typ = Type(card)
    invert = int(me.hasInvertedTable())
    if isCharacter(card): lim = zones[loc][cardType.character][invert]['max']
    elif typ == cardType.troublemaker: lim = zones[loc][typ][int(card.isFaceUp)][invert]['max']
    else: lim = zones[loc][cardType.resource][invert]['max']
    l = locations[0][loc]
    l.pop(l.index(card._id))
    index = -1
    x,y = card.position
    for i in range(len(l)):
        x1,y1 = Card(l[i]).position
        x2 = x1+cardWidth
        y2 = y1+cardHeight
        if x1 <= x < x2 and y1 <= y < y2: index = i+1
    if index == -1:
        for i in range(min(lim, len(l))):
            x1,y1 = Card(l[i]).position
            if x1 <= x < x2: index = i+1
    if index == -1:
        try:
            x1,y1 = Card(l[0]).position
            if x <= x1: index = 0
            else: index = len(l)
        except: index = 0
    l.insert(index, card._id)
    organizeZone(loc)