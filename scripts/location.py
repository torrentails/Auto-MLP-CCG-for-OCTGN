def _get_x_positions(length, offset=0, h_align='center'):
    last = None
    gap = 91

    for i in range(length+1):
        if i <= 2:
            last = 84*(i+1)+7*i
            
        else:
            gap = int(round(max(((last*1.0)/i)*(1-(i-4)/10.0),20)))
            if i == 3:
                gap = 84
            last = int(round(last+gap/2.0))
            
    if h_align == 'center':
        offset -= int(round(((length-1)*gap+84)/2.0))
    elif h_align == 'right':
        offset -= int(round((length-1)*gap+84))
    # elif h_align == 'left':
    #     offset += int(round((length-1)*gap+84))

    lst = []
    for i in range(length):
        lst.append(offset+gap*i)

    return lst

def _set_positions(lst, x_offset, y, h_align='center', reverse=False):
    x_positions = _get_x_positions(len(lst), x_offset, h_align)
    if reverse:
        x_positions.reverse()
        lst.reverse()
    for i in range(len(lst)):
        card = lst[i]
        facedown = card.facedown
        x = x_positions[i]
        card._set_table_position(x, y, facedown)
        card._base.sendToFront()

class _Location(object):
    def __init__(self, name, zone_type='Table', character_pos=None,
        resource_pos=None, faceup_TM_pos=None, facedown_TM_pos=None,
        problem_pos=None, event_pos=None):
        log("Initializing location LOCATION.{}".format(name),
            LOGLEVEL.VERBOSE)

        self.name = name
        self.id = uuid(hash(name))
        self.zone_type = zone_type
        self.card_list = []

        self.__positions = {}
        self.__positions['character'] = character_pos or (0, 0, 'center')
        self.__positions['resource'] = resource_pos or (0, 0, 'center')
        self.__positions['faceup_TM'] = faceup_TM_pos or (0, 0, 'center')
        self.__positions['facedown_TM'] = facedown_TM_pos or (0, 0, 'center')
        self.__positions['problem'] = problem_pos or (0, 0, 'center')
        self.__positions['event'] = event_pos or (0, 0, 'center')

    def __iter__(self):
        for card in self.card_list:
            yield card

    def __eq__(self, other):
        if other is self: return True
        if isinstance(other, self.__class__):
            return self.id == other.id
        return NotImplemented

    def __ne__(self, other):
        if other is self: return False
        if isinstance(other, self.__class__):
            return not self == other
        return NotImplemented

    def __hash__(self):
        return hash(self.id)

    def __str__(self):
        return "LOCATION.{}".format(self.name)

    def __repr__(self):
        return "LOCATION.{} ({})".format(self.name, self.id)

    def _set_offset(self, typ, x=None, y=None, h_align=None, organise=True):
        _x, _y, _h_align = self.__positions[typ]
        x = x or _x
        y = y or _y
        h_align = h_align or _h_align
        self.__positions[typ] = (x, y, h_align)
        if organise:
            self._organise()

    def _get_pos(self, typ):
        x, y, h_align = self.__positions[typ]
        if type(x) == _FuncionType:
            x = x(self)
        if type(y) == _FuncionType:
            y = y(self)
        if type(h_align) == _FuncionType:
            h_align = h_align(self)
        #TODO: fix y for two players
        return x, y, h_align

    def _remove_cards(self, card_list):
        if type(card_list) not in (tuple,list):
            card_list = (card_list,)

        for card in card_list:
            log("Removing {} from {}".format(card, self), LOGLEVEL.VERBOSE)
            try:
                self.card_list.remove(card)
            except ValueError:
                log("{} not found in {}".format(card, self), LOGLEVEL.WARN)
        self._organise()

    def _add_cards(self, card_list):
        if type(card_list) not in (tuple,list):
            card_list = (card_list,)

        for card in card_list:
            log("Adding {} to {}".format(card, self), LOGLEVEL.VERBOSE)
            if card in self.card_list:
                log("{} already in {}".format(card, self), LOGLEVEL.ERROR)
                return
            self.card_list.append(card)
        self._organise()

    def _get_sorted_lists(self):
        characters = []
        resources = []
        faceup_TMs = []
        facedown_TMs = []
        problems = []
        events = []

        for card in (c for c in self.card_list if c.controller == me):
            if card.is_character():
                characters.append(card)
            else:
                typ = card.type
                if CARDTYPE.PROBLEM in typ:
                    problems.append(card)
                elif CARDTYPE.TROUBLEMAKER in typ:
                    if card.is_faceup():
                        faceup_TMs.append(card)
                    else:
                        facedown_TMs.append(card)
                elif CARDTYPE.RESOURCE in typ:
                    attached = card.attached_to()
                    if attached:
                        if CARDTYPE.PROBLEM in attached.type:
                            resources.append(card)
                    else:
                        resources.append(card)
                else:
                    events.append(card)

        return characters, resources, faceup_TMs, facedown_TMs, problems, events

    def _organise(self):
        if self.zone_type != 'Table':
            log("Can not organise {}; not table".format(self), LOGLEVEL.VERBOSE)
            return

        log("Organising {}".format(self), LOGLEVEL.DEBUG)
        update()

        lists = self._get_sorted_lists()
        log("Sorting problems in {}".format(self), LOGLEVEL.VERBOSE)
        _set_positions(lists[4], *self._get_pos('problem'))
        log("Sorting facedown_TMs in {}".format(self), LOGLEVEL.VERBOSE)
        _set_positions(lists[3], *self._get_pos('facedown_TM'), reverse=True)
        log("Sorting faceup_TMs in {}".format(self), LOGLEVEL.VERBOSE)
        _set_positions(lists[2], *self._get_pos('faceup_TM'))
        log("Sorting resources in {}".format(self), LOGLEVEL.VERBOSE)
        _set_positions(lists[1], *self._get_pos('resource'))
        log("Sorting characters in {}".format(self), LOGLEVEL.VERBOSE)
        _set_positions(lists[0], *self._get_pos('character'), reverse=True)
        log("Sorting events in {}".format(self), LOGLEVEL.VERBOSE)
        _set_positions(lists[5], *self._get_pos('event'), reverse=True)

class _Location_Manager(object):
    def __init__(self):
        log("Initializing Location Manager", LOGLEVEL.DEBUG)
        self.__home = _Location('HOME', 'Table',
            (0, 195, 'center'), # Characters
            (-600, 195, 'left'), # resources
            (600, 195, 'right')) # faceup_TMs
        self.__myproblem = _Location('MYPROBLEM', 'Table',
            (321, 57, 'center'), # Characters
            (258, -14, 'right'), # resources
            (321, -94, 'center'), # faceup TMs # TODO: function for x location
            (385, -14, 'left'), # facedown TMs
            (305, -42, 'center')) # problems
        self.__oppproblem = _Location('OPPPROBLEM', 'Table',
            (-305, 50, 'center'), # Characters
            (-365, -39, 'right'), # resources
            (-305, -97, 'center'), # faceup TMs # TODO: function for x location
            (-245, -39, 'left'), # facedown TMs
            (-305, -41, 'center')) # problems
        self.__flipped = _Location('FLIPPED', 'Table',
            (0, 92, 'center')) # Characters
        self.__hand = _Location('HAND', 'Hand')
        self.__deck = _Location('DECK', 'Pile')
        self.__discard = _Location('DISCARD', 'Pile')
        self.__banished = _Location('BANISHED', 'Pile')
        self.__problemdeck = _Location('PROBLEMDECK', 'Pile')
        self.__other_locations = []

        def _func(self):
            all_list = [c for c in self.card_list if c.controller == me]
            return all_list, [], [], [], [], []
        self.__flipped._get_sorted_lists = _MethodType(_func, self.__flipped)

    @property
    def HOME(self):
        return self.__home
    @property
    def MYPROBLEM(self):
        return self.__myproblem
    @property
    def OPPPROBLEM(self):
        return self.__oppproblem
    @property
    def FLIPPED(self):
        return self.__flipped
    @property
    def DECK(self):
        return self.__deck
    @property
    def HAND(self):
        return self.__hand
    @property
    def DISCARD(self):
        return self.__discard
    @property
    def BANISHED(self):
        return self.__banished
    @property
    def PROBLEMDECK(self):
        return self.__problemdeck

    def __iter__(self):
        yield self.HOME
        yield self.MYPROBLEM
        yield self.OPPPROBLEM
        yield self.FLIPPED
        yield self.DECK
        yield self.HAND
        yield self.DISCARD
        yield self.BANISHED
        yield self.PROBLEMDECK
        for val in self.__other_locations:
            yield val

LOCATION = _Location_Manager()