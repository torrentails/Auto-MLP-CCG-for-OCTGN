import re

_card_base = Card
_card_list = {}

CARDTYPE = _Enum('CARDTYPE', ('CHARACTER', 'MANECHARACTER', 'FRIEND', 'EVENT',
                              'RESOURCE', 'TROUBLEMAKER', 'PROBLEM'))

TRAIT = _Enum('TRAIT', ('EARTHPONY', 'UNICORN', 'PEGASUS', 'ALICORN', 'ALLY',
                        'BREEZIE', 'BUFFALO', 'CHANGELING', 'CRITTER',
                        'CRYSTAL', 'DONKEY', 'DRACONEQUUS', 'DRAGON', 'GRIFFON',
                        'ZEBRA', 'AHUIZOTL', 'COW', 'CHAOTIC', 'ELDER', 'FOAL',
                        'MINOTAUR', 'PERFORMER', 'ROCK', 'ROYALTY',
                        'SEASERPENT', 'TREE', 'ACCESSORY', 'ARMOR', 'ARTIFACT',
                        'ASSET', 'CONDITION', 'LOCATION', 'REPORT', 'MAILBOX',
                        'UNIQUE', 'GOTCHA', 'SHOWDOWN', 'EPIC'))

COLOR = _Enum('COLOR', ('BLUE', 'ORANGE', 'PINK', 'PURPLE', 'WHITE', 'YELLOW',
                        'COLORLESS', 'WILD', 'NONBLUE', 'NONORANGE', 'NONPINK',
                        'NONPURPLE', 'NONWHITE', 'NONYELLOW'))

#TODO write code to dynamically update keyword list
KEYWORD = _Enum('KEYWORD', ('HOMELIMIT', 'CARETAKER', 'INSPIRED', 'PRISMATIC',
                            'PUMPED', 'RANDOM', 'STARTINGPROBLEM', 'STUBBORN',
                            'STUDIOUS', 'SUPPORTIVE', 'SWIFT', 'TEAMWORK',
                            'VILLAIN'))

RARITY = _Enum('RARITY', ('COMMON', 'UNCOMMON', 'RARE', 'SUPERRARE',
                          'ULTRARARE', 'ROYALRARE', 'FIXED', 'PROMO'))

def parse_values(string, enum, as_dict=False):
    """ Accepts a string and parses through it to retrieve comma seperated
        enumeration values

        :param string:  String in the form of `value [num], value [num]...`
        :param enum:    Values will be extracted and mapped the supplied enum
        :param as_dict: If `True` the result will be a dictionary with the keys
        being the enum vlues and the values being associated numbers or `None`
        if not present, else the function will return a list of enum values

        :return list:   Will return either a list or a dict, depending on as_dict
    """
    if string == '':
        return {} if as_dict else []
    values = [val.strip() for val in string.split(',')]
    if as_dict:
        dct = {}
        for val in values:
            try:
                v = int(val[0])
                k = enum[val[2:].replace(' ', '').replace('-', '')]
                dct[k] = v
            except ValueError:
                try:
                    v = int(val[len(val)-1])
                    k = enum[val[:len(val)-2].replace(' ', '').replace('-', '')]
                    dct[k] = v
                except ValueError:
                    dct[enum[val]] = None
        return dct
    else:
        return [enum[val.replace(' ', '').replace('-', '')] for val in values]

class Card(object):
    def __new__(cls, id):
        try:
            return _card_list[id]
        except KeyError:
            return super(Card, cls).__new__(cls, id)

    def __init__(self, id):
        if id in _card_list:
            return

        c = _card_base(id)
        self._base = c
        # self.c is just temporary for testing; DO NOT USE IN CODE
        self.c = c
        self.__side = [{},{}]

        log("Creating card {}".format(self), LOGLEVEL.DEBUG)

        self.__side[0]['name'] = [c.Name]
        self.__side[0]['title'] = [c.Title]
        self.__side[0]['subtitle'] = [c.Subtitle]
        log("Parsing traits", LOGLEVEL.VERBOSE)
        self.__side[0]['traits'] = parse_values(c.Traits, TRAIT)
        log("Parsing colors", LOGLEVEL.VERBOSE)
        self.__side[0]['colors'] = parse_values(c.Colors, COLOR)
        log("Parsing power", LOGLEVEL.VERBOSE)
        try:
            self.__side[0]['power'] = int(c.Power)
        except ValueError:
            self.__side[0]['power'] = None # May need to be 0
        log("Parsing keywords", LOGLEVEL.VERBOSE)
        self.__side[0]['keywords'] = parse_values(c.Keywords, KEYWORD, as_dict=True)

        if c.Type == "Mane Character":
            log("Creating boosed side", LOGLEVEL.VERBOSE)
            altp = lambda val: c.alternateProperty(
                "Mane Character Boosted", val)
            self.__side[1]['name'] = [altp('Name')]
            self.__side[1]['title'] = [altp('Title')]
            self.__side[1]['subtitle'] = [altp('Subtitle')]
            log("Parsing boosted traits", LOGLEVEL.VERBOSE)
            self.__side[1]['traits'] = parse_values(altp('Traits'), TRAIT)
            log("Parsing boosted colors", LOGLEVEL.VERBOSE)
            self.__side[1]['colors'] = parse_values(altp('Colors'), COLOR)
            log("Parsing boosted power", LOGLEVEL.VERBOSE)
            try:
                self.__side[1]['power'] = int(altp('Power'))
            except ValueError:
                self.__side[1]['power'] = None # May need to be 0
            log("Parsing boosted keywords", LOGLEVEL.VERBOSE)
            self.__side[1]['keywords'] = parse_values(altp('Keywords'), KEYWORD,
                                             as_dict=True)

        log("Parsing cardtrype", LOGLEVEL.VERBOSE)
        self._base_type = [CARDTYPE[c.Type.replace(' ','')]]
        log("Parsing cost", LOGLEVEL.VERBOSE)
        try:
            self.__cost = int(c.Cost)
        except ValueError:
            self.__cost = None # May need to be 0
        log("Parsing play requirements", LOGLEVEL.VERBOSE)
        self.__play_requirements = parse_values(c.PlayRequirements, COLOR,
                                         as_dict=True)
        log("Parsing bonus points", LOGLEVEL.VERBOSE)
        try:
            self.__bonus_points = int(c.BonusPoints)
        except ValueError:
            self.__bonus_points = None
        log("Parsing your confront requirements", LOGLEVEL.VERBOSE)
        self.__your_requirements = parse_values(c.YourRequirements,
                                       COLOR, as_dict=True)
        log("Parsing opponents confront requirements", LOGLEVEL.VERBOSE)
        self.__opponents_requirements = parse_values(c.OpponentsRequirements,
                                            COLOR, as_dict=True)
        # self.__number = c.Number.replace(' ','')
        rarity_list = {'C':RARITY.COMMON,
            'U':RARITY.UNCOMMON,
            'R':RARITY.RARE,
            'SR':RARITY.SUPERRARE,
            'UR':RARITY.ULTRARARE,
            'RR':RARITY.ROYALRARE,
            'F':RARITY.FIXED,
            'P':RARITY.PROMO}
        log("Parsing raity", LOGLEVEL.VERBOSE)
        self.rarity = rarity_list[c.Rarity]
        
        self.__effects = []
        
        self.id = id
        self.uuid = c.model
        self.owner = me
        self.controller = me
        # TODO: This can be better
        # self.__location = LOCATION.DECK
        # LOCATION.DECK.card_list.append(self)
        self.set_location(LOCATION.MYPROBLEM)
        # self.in_play = False
        # self.turn_entered_location = g.turn_count
         
        _card_list[id] = self

    # def __getattr__(self, attr):
    #     log("Getting base card attribute of {}".format(self))
    #     return self._base.__getattr__(attr)

    # def __str__(self):
    #     return '{#' + str(self.id) + '}'

    def __str__(self):
        return "{}".format(self._base)

    def __apply_modifiers(self, key, modifier=None, value=None):
        log("Fetching modifiers for {} on {}".format(key, self), LOGLEVEL.DEBUG)
        if modifier is None:
            modifier = MODIFIER[key.replace('_', '').upper()]
        if value is None:
            value = self.__side[self.is_boosted()][key]
        val = _apply_modifiers(self, modifier, {key:value})
        return val[key]

    @property
    def name(self):
        return self.__apply_modifiers('name')

    @property
    def title(self):
        return self.__apply_modifiers('title')

    @property
    def subtitle(self):
        return self.__apply_modifiers('subtitle')

    @property
    def traits(self):
        return self.__apply_modifiers('traits', MODIFIER.TRAIT)

    @property
    def colors(self):
        return self.__apply_modifiers('colors', MODIFIER.COLOR)

    @property
    def power(self):
        return self.__apply_modifiers('power')

    # TODO: keywords

    @property
    def type(self):
        return self.__apply_modifiers('type', value=self._base_type)

    @property
    def cost(self):
        return self.__apply_modifiers('cost', value=self.__cost)

    @property
    def play_requirements(self):
        return self.__apply_modifiers('play_requirements',
            value=self.__play_requirements)

    @property
    def bonus_points(self):
        return self.__apply_modifiers('bonus_points',
            value=self.__bonus_points)

    @property
    def your_requirements(self):
        return self.__apply_modifiers('your_requirements',
            value=self.__your_requirements)

    @property
    def opponents_requirements(self):
        return self.__apply_modifiers('opponents_requirements',
            value=self.__opponents_requirements)

    # TODO: effects

    @property
    def _id(self):
        return self.id

    # @property
    # def controller(self):
    #     return self._base.controller
    # @controller.setter
    # def controller(self, player):
    #     self._base.controller = player
    
    # @property
    # def owner(self):
    #     return self._base.owner
    # @owner.setter
    # def owner(self, player):
    #     pass
    #     # self._base.owner = player

    @property
    def location(self):
        return self.__location

    @property
    def faceup(self):
        return self._base.isFaceUp

    @property
    def facedown(self):
        return not self.faceup

    def is_boosted(self):
        # TODO: Write this
        return False

    def is_character(self):
        _type = self.type
        return CARDTYPE.MANECHARACTER in _type or CARDTYPE.FRIEND in _type

    def attached_to(self):
        # TODO: Write this
        return None
    
    def set_location(self, location):
        try:
            old_loc = self.location
            log("Setting {} location: from {} to {}".format(self, old_loc,
                location), LOGLEVEL.DEBUG)
            old_loc._remove_cards(self)

        except AttributeError:
            log("Inititlizing {} loaction: {}".format(self, location),
                LOGLEVEL.DEBUG)

        self.__location = location
        location._add_cards(self)
    
    def _set_table_position(self, x=0, y=0, force_facedown=False):
        # TODO: Check that the card in on the table
        self._base.moveToTable(x, y, force_facedown)

    # _id     Returns the unique identity value of the card   
    # # alternate   The card's alternate form.  
    # # alternates  a LIST of all alternate forms of the card, identified by their 'type' string.   
    # _anchor  Anchors the card to the table, preventing players from manually moving it   
    # _controller  the player OBJECT of the card's current controller.     
    # filter  the current filter color as a string in #HEX color format.  
    # # group   Returns the group OBJECT that the card is currently located in.     
    # # index   the current index (z-value) of the card in the group it is in.  
    # # isFaceUp    Returns or Sets the card's visibility status.   
    # # height  Returns the card's height as defined by the game.   
    # highlight   the current highlight color as a string in #HEX color format.   
    # _markers     Returns a DICTIONARY of all markers which can be edited via python.     
    # # model   Returns the GUID of the card    
    # # name    Returns the chat-hoverable name of the card     
    # _orientation     Returns or Sets the current rotation of a card in 90 degree intervals.  
    # _owner   Returns the player OBJECT of the card's owner.  
    # _position    Returns the x,y coordinates of the card.    
    # # properties  Returns dictionary of all the card's custom properties and their values     
    # # set     The name of the expansion set that the card belongs to  
    # # setId   The GUID of the expansion set that the card belongs to  
    # # size    Returns the name of the card's current custom size  
    # _targetedBy  Returns the player OBJECT who is targeting the card.    
    # # width
    # # alternateProperty()     Returns a property value from an alternate form of the card.    
    # arrow()     Draws an arrow from the card to another card. active = False will remove the arrow.     
    # _delete()    Eliminates the card from the game.  
    # _isInverted()    Checks to see if the card would be inverted at the given y coordinate   
    # _moveTo()    Moves a card to a specified group. Top of piles if index = None.    
    # _moveToBottom()  Moves a card to the BOTTOM of a specified PILE.     
    # _moveToTable()   Moves a card to specified coordinates on the table.     
    # _offset()    a new coordinate tuple (x,y) slightly offset from the card's current position   
    # _peek()  Reveals the identity of the card to the local player while keeping it face-down.    
    # # resetProperties()   Clears all changes made to card properties, restoring their original values     
    # select()    Adds the card to the current selection.     
    # # sendToBack()    Sends the card behind all other cards on the TABLE ONLY     
    # # sendToFront()   Sends the card in front of all other cards on the TABLE ONLY    
    # target()    Targets the card, or removes target if active = False.