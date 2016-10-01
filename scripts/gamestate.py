class Gamestate(object):
    def __init__(self):
        self.__syncOn = True
        self.__pending_data = []
        self.__player_data = {Player(me._id):set()}
        self.card_dict = {}
        self.pending_response = {}
        
    def __setattr__(self, a, v):
        # Stuff
        try:
            super(Gamestate, self).__setattr__(a, v)
        except:
            self.__pending_data.append([a, v])
            getattr(self, '_'+a)(v)
            self.sync()
        
    def __sync_clients(self, force = False):
        if self.__syncOn or force:
            if len(getPlayers()) > 1:
                whisper('Synchronising clients')
            else:
                whisper('No additional players detected')
        # else:
            # whisper('Delaying sync')
            
    def __sync_change(self, value):
        self.__syncOn = value
        if value:
            self.__sync_clients()
    def __get_sync_func(self):
        return self.__sync_clients
    sync = property(__get_sync_func, __sync_change)
        
    def get_response(self, id, timeout = 100)
        timeout_count = 0
        while(g.pending_response.has_key(id)):
            sleep(0.1)
            timeout_count += 1
            if timeout_count >= timeout:
                del g.pending_response[id]
                raise ResponseTimeout("{} took too long to respond.".format(player))
        return self.__response[id]
    def set_reponse(self, id, value):
        self.__response[id] = value

g = Gamestate()
Gamestate = None

def rcall(func, *args, **kwargs):
    try: func = func.__name__ except: pass
    player = kwargs.get('player', players[1])
    callback = kwargs.get('callback', None)
    id = uuid4()
    g.pending_response[id] = callback
    rcall_send_message(player, func, message.INITIAL, id, *args)
    return(id)
        
def rcall_recieve_message(func, typ, id *args):
    if typ == message.RESPONSE:
        g.set_reponse(id, args)
        callback = g.pending_response.pop(id)
        if callback:
        	callback(*args)
    elif typ == message.INITIAL:
        globals()[func](args)
        
def rcall_send_message(player, *args, **kwargs):
    remoteCall(player, 'rcall_recieve_message', args)
    
