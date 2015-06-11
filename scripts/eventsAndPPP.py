#-----------------------------------------------------------------------
# Event bus management
#-----------------------------------------------------------------------

#Event bus
eventBus = {}
delayedEvents = []
eventsToRemove = []
eventsToAdd = []
isIteratingEvents = 0

def registerEvent(evt, funcion, delayed=False, runOnce=False, ignorePPP=False id=None, **kwargs):
    if id == None: id = uuid4()
    if delayed: delayedEvents.append([evt, funcion, runOnce, ignorePPP, id, kwargs])
    else:
        global isIteratingEvents
        if isIteratingEvents > 0:
            eventsToAdd.append([evt, funcion, delayed, runOnce, ignorePPP, id, kwargs])
        if evt not in eventBus: eventBus[evt] = {}
        eventBus[evt][id] = [funcion, runOnce, kwargs, ignorePPP]
    return id
        
def enableDelayedEvents():
    global delayedEvents
    for e in delayedEvents:
        registerEvent(e[0], e[1], runOnce=e[2], ignorePPP=e[3], id=e[4], **e[5])
    delayedEvents = []

def removeEvent(id):
    eventsToRemove.append(id)
    cleanupEvents()
    
def cleanupEvents():
    global isIteratingEvents
    if isIteratingEvents > 0: return
    rmLst = []
    global eventsToRemove
    for e in eventBus.iterkeys():
        for id in eventsToRemove:
            if id in eventBus[e]:
                rmLst.append([e,eventsToRemove.pop(eventsToRemove.index(id))])
    for v in rmLst:
        del eventBus[v[0]][v[1]]
    eventsToRemove = []
    global eventsToAdd
    for e in eventsToAdd:
        registerEvent(e[0], e[1], e[2], e[3], e[4], e[5], **e[6])
    
def fireEvent(evt, ignorePPP=False, **args):
    if evt not in eventBus: return False
    if ignorePPP or isPPPEnabled():
        args['event'] = evt
        args['canceled'] = False
        global isIteratingEvents
        isIteratingEvents += 1
        for id in eventBus[evt].iterkeys():
            args.update(eventBus[evt][id][2])
            ret = eventBus[evt][id][0](args)
            if ret == None or ret == True:
                if eventBus[evt][id][1]: removeEvent(id)
        isIteratingEvents -= 1
        cleanupEvents()
    else:
        addPPP(fireEvent, **args)
        return False
    return args['canceled']
    
#-----------------------------------------------------------------------
# Pre-Priority Processing Queue
#-----------------------------------------------------------------------

PPPQ = []

def addPPP(func, *args, **kwargs):
    PPPQ.append([func, args, kwargs])
    if isPPPEnabled(): processQ()

def enablePPP():
    setGlobalVariable('PPP', 'True')
    processQ()
    
def disablePPP():
    setGlobalVariable('PPP', 'False')
    
def isPPPEnabled():
    return eval(getGlobalVariable('PPP')
    
def processQ():
    if isPPPEnabled():
        global PPPQ
        lst = PPPQ.copy()
        for e in lst:
            e[0](*e[1], **e[2])