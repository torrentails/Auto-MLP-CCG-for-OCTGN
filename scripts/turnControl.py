#-----------------------------------------------------------------------
# Turn control
#-----------------------------------------------------------------------

def endPhase(group, x=0, y=0):
    curPhase = phase[getGlobalVariable("Phase", phase.ready.name)]
    if not fireEvent(event.endPhase, phase=curPhase):
        if curPhase == phase.ready: _troublemakerPhase()
        elif curPhase == phase.troublemaker: _mainPhase()
        elif curPhase == phase.main: _scorePhase()
        elif curPhase == phase.score: _endPhase()
        elif curPhase == phase.end: _passTurn()

def _startTurn():
    mute()
    enablePPP()
    fireEvent(event.startTurn)
    _readyPhase()

def _readyPhase():
    mute()
    setGlobalVariable("Phase", phase.ready.name)
    disablePPP()
    fireEvent(event.startOfPhase, phase=phase.ready)
    fireEvent(event.readyPhase)
    # Ready Step
    for card in getCardsInPlay(me): ready(card)
    # Action Step
    higestPoints = max(me.counters['Points'].value, players[1].counters['Points'].value)
    if highestPoints >= 11: AtToGain = 5
    elif highestPoints >= 6: AtToGain = 4
    elif highestPoints >= 3: AtToGain = 3
    else: AtToGain = 2
    gainAT(AtToGain)
    enablePPP()
    # Draw Step
    if not eval(getGlobalVariable('firstTurn')): draw()
    if not fireEvent(event.endPhase, phase=phase.ready):
        _troublemakerPhase()

def _troublemakerPhase():
    mute()
    setGlobalVariable("Phase", phase.troublemaker.name)
    fireEvent(event.startOfPhase, phase=phase.troublemaker)
    fireEvent(event.troublemakerPhase)
    # Uncover step
    for card in getCardsInPlay():
        if cardType.troublemaker in TypeList(card) and card.controler == me:
            uncover(card)
    # Challenge Step
    foundTMToChalange = False
    for card in getCardsInPlay():
        if cardType.troublemaker in TypeList(card):
            if canChallange(card): foundTMToChalange = True
    if not foundTMToChalange:
        _troublemakerPhaseEnd()
    
def _troublemakerPhaseEnd():
    if not fireEvent(event.endOfPhase, phase=phase.troublemaker):
        _mainPhase()

def _mainPhase():
    mute()
    setGlobalVariable("Phase", phase.main.name)
    firEvent(event.startOfPhase, phase=phase.main)
    fireEvent(event.mainPhase)
    # Main phase actions (in any order):
        # Play a card
        # Move a character
        # Draw a card for 1 AT
        # Rally a frightened friend
        # Activate an ability
        
def _mainPhaseEnd():
    if not firEvent(event.endOfPhase, phase=phase.main):
        _scorePhase()

def _scorePhase():
    mute()
    setGlobalVariable("Phase", phase.score.name)
    fireEvent(event.startOfPhase, phase=phase.score)
    fireEvent(event.scorePhase)
    # Confront step
    problemsConfronted = []
    for card in getCardsInPlay():
        if cardType.problem in TypeList(card):
            if canConfront(card):
                #TODO: Maybe ask which problem to confront first?
                if confront(card):
                    problemsConfronted.append(card)
    # Faceoff Step
    problemsToSolve = []
    if len(problemsConfronted) >= 2:
        lst = getCardsAtLocation(location.myProblem) + getCardsAtLocation(location.oppProblem)
        lst = [c for c in lst if isCharacter(c)]
        if beginFaceoff(faceoff.double, lst): problemsToSolve = problemsConfronted
    else:
        for card in problemsConfronted:
            if canConfront(card, players[1]):
                lst = [c for c in getCardsAtLocation(getLocation(card)) if isCharacter(c)]
                if beginFaceoff(faceoff.problem, lst):
                    problemsToSolve.append(card)
    # Solve Step
    for card in problemsToSolve:
        replaceProblem(card)
    if not fireEvent(event.endOfPhase, phase=phase.score):
        _endPhase()

def _endPhase():
    mute()
    setGlobalVariable("Phase", phase.end.name)
    fireEvent(event.startOfPhase, phase=phase.end)
    # End of Turn Step
    fireEvent(event.endPhase)
    disablePPP()
    # Wrap up Step
    # Apply hand limit
    cardsInHand = getCardsAtLocation(location.hand, me)
    dicardList = []
    handLimit = applyModifiers(modifier.handLimit, {'player':me, 'limit':8})['limit']
    if len(cardsInHand) > handLimit:
        boxTitle = "Too many cards in hand."
        while len(cardsInHand) > handLimit:
            if len(cardsInHand)-handLimit == 1: question = "Choose a card to discard."
            else: question = "Choose {} cards to discard.".format(len(cardsInHand)-handLimit)
            card = askCard(cardsInHand, boxTitle, question)
            dicardList.append(cardsInHand.pop(card))
        discard(dicardList)
    # Apply home limit
    cardsAtHome = [c for c in getCardsAtLocation(location.home, me) if cardType.friend in TypeList(c)]
    homeLimit = getHomeLimit()
    if len(cardsAtHome) > homeLimit:
        boxTitle = "Too many Friends at home."
        while len(cardsAtHome) > homeLimit:
            if len(cardsAtHome)-homeLimit == 1: question = "Choose a Friend to retire."
            else: question = "Choose {} Friends to retire.".format(len(cardsAtHome)-homeLimit)
            card = askCard(cardsAtHome, boxTitle, question)
            dicardList.append(cardsAtHome.pop(card))
        retire(dicardList, reason='homeLimit')
    if not fireEvent(event.endOfPhase, phase=phase.end):
        _passTurn()
    
def _passTurn():
    if not fireEvent(event.endTurn):
        setGlobalVariable('firstTurn', 'False')
        setGlobalVariable('turnPlayer', str(players[1]))
        remoteCall(players[1], '_startTurn', [])