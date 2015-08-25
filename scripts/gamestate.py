class Gamestate(object):
    def __init__(self):
        self._syncOn = True
        self._pending_data = []
        self[me._id
        self.card_dict = {}
        
    def __setattr__(self, a, v):
        # Stuff
        try:
            super(Gamestate, self).__setattr__(a, v)
        except:
            self._pending_data.append([a, v])
            getattr(self, '_'+a)(v)
            self.sync()
        
    def sync(self, force = False):
        if self._syncOn or force:
            if len(getPlayers()) > 1:
                whisper('Synchronising clients')
            else:
                whisper('No additional players detected')
        else:
            whisper('Delaying sync')
            
    def disableSync(self):
        self._syncOn = false
        
    def enableSync(self):
        self._syncOn = true
        
    def flush(self):
        pass # TODO: add sync code here

gs = Gamestate()
        
def respond(*args):
    gs.response = args
    gs.response_recieved = True

def wait_response(player = players[1], command = None, args_list = [], timeout = 100):
    if type(command) != string: raise IncorrectCommandType(str(command))
    gs.response_recieved = False
    timeout_count = 0
    remoteCall(player, command, args_list)
    while(not gs.response_recieved):
        sleep(0.1)
        timeout_count += 1
        if timeout_count >= timeout: raise ResponseTimeout("{} took too long to respond.".format(player))
    # if len(gs.response) == 1: return gs.response[0]
    return gs.response