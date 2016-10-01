#-----------------------------------------------------------------------
# Settings
#-----------------------------------------------------------------------

# Temporary settings because of "Queue Empty" error
class setting:
    develop = False
    debug = False

class _Setting_Manager(object):
    def __init__(self):
        self.__develop = getSetting('developer_mode', False)
        self.__debug = getSetting('debug_mode', False)

    @property
    def develop(self):
        return self.__develop
    @develop.setter
    def develop(self, val):
        self.__develop = val

    @property
    def debug(self):
        return self.develop or self.__debug
    @debug.setter
    def debug(self, val):
        self.__debug = val
    