class Gamestate(object):
    def __init__(self):
        self._syncOn = True
        self._pending = []
        
        self.card_dict = {}
        
    def sync(force = True):
        if self._syncOn or force:
            whisper('Synchronising clients')
            
    def disableSync():
        self._syncOn = false
        
    def enableSync():
        self._syncOn = true
        
    def flush():
        pass # TODO: add sync code here

gs = Gamestate()