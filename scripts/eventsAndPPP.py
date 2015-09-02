#-----------------------------------------------------------------------
# Event bus management
#-----------------------------------------------------------------------

# def remove_on_event(self, e):
    # evt = new_event(e)
    # evt.event = self
    # def action(self, *args): self.event.destroy()
    # evt.action = action
    # evt.fire_once = True

#Event bus
eventBus = {}
delayedEvents = []
eventsToRemove = []
eventsToAdd = []
isIteratingEvents = 0

def registerEvent(evt, funcion, delayed=False, runOnce=False, alwaysFire=False, id=None, **kwargs):
    if id == None: id = uuid4()
    if delayed: delayedEvents.append([evt, funcion, runOnce, alwaysFire, id, kwargs])
    else:
        global isIteratingEvents
        if isIteratingEvents > 0:
            eventsToAdd.append([evt, funcion, delayed, runOnce, alwaysFire, id, kwargs])
        if evt not in eventBus: eventBus[evt] = {}
        eventBus[evt][id] = [funcion, runOnce, kwargs, alwaysFire]
    return id
        
def enableDelayedEvents():
    global delayedEvents
    for e in delayedEvents:
        registerEvent(e[0], e[1], False, e[2], e[3], e[4], **e[5])
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

# TODO: Fix this for PPP
def fireEvent(evt, ignorePPP=False, **args):
    if evt not in eventBus: return False
    ignorePPP = ignorePPP or isPPPEnabled()
    args['event'] = evt
    args['canceled'] = False
    global isIteratingEvents
    isIteratingEvents += 1
    for id in eventBus[evt].iterkeys():
        if id not in eventsToRemove:
            if ignorePPP or eventBus[evt][id][3]:
                args.update(eventBus[evt][id][2])
                ret = eventBus[evt][id][0](args)
                if ret == None or ret == True:
                    if eventBus[evt][id][1]: removeEvent(id)
            else:
                addPPP(fireSpecificEvent, evt, id, **args)
        isIteratingEvents -= 1
        cleanupEvents()
    return args['canceled']
    
def fireSpecificEvent(evt, id, **args):
    if evt not in eventBus or id in eventsToRemove: return
    if id in eventBus[evt]:
        args.update(eventBus[evt][id][2])
        ret = eventBus[evt][id][0](args)
        if ret == None or ret == True:
            if eventBus[evt][id][1]: removeEvent(id)

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
    return eval(getGlobalVariable('PPP'))
    
def processQ():
    if isPPPEnabled():
        global PPPQ
        lst = list(PPPQ)
        for e in lst:
            e[0](*e[1], **e[2])