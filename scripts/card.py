import re

Card_Base = Card

def Card(id):
    try:
        return gs.card_dict[id]
    except KeyError:
        return _Card(id)

class _Card(object):
    def __init__(self, id):
        self._id = id
        self._side_ = [{},{}]
        c = Card_Base(id)
        # Front Side
        self._side_[0]['_name_'] = [c.Name]
        self._side_[0]['_title_'] = [c.Title]
        self._side_[0]['_subtitle_'] = [c.Subtitle]
        self._side_[0]['_traits_'] = parseTraits(c.Traits)
        self._side_[0]['_colors_'] = parseColors(c.Colors)
        self._side_[0]['_power_'] = intOrNone(c.Power)
        self._side_[0]['_keywords_'] = parseKeywords(c, c.Keywords)
        self._side_[0]['_text_'] = c.Text
        # Back Side
        if c.Type == "Mane Character":
            altf = c.alternateProperty
            alt = "Mane Character Boosted"
            self._side_[1]['_name_'] = [altf(alt,'Name')]
            self._side_[1]['_title_'] = [altf(alt,'Title')]
            self._side_[1]['_subtitle_'] = [altf(alt,'Subtitle')]
            self._side_[1]['_traits_'] = parseTraits(altf(alt,'Traits'))
            self._side_[1]['_colors_'] = parseColors(altf(alt,'Colors'))
            self._side_[1]['_power_'] = intOrNone(altf(alt,'Power'))
            self._side_[1]['_keywords_'] = parseKeywords(c, altf(alt,'Keywords'))
            self._side_[1]['_text_'] = altf(alt,'Text')
        # Common info
        self._type_ = cardType[c.Type.replace(' ','')]
        self._cost_ = intOrNone(c.Cost)
        self._play_requirements_ = parseRequirements(c.PlayRequirements)
        self._bonus_points_ = intOrNone(c.BonusPoints)
        self._your_requirements_ = parseRequirements(c.YourRequirements)
        self._opponents_requirements_ = parseRequirements(c.OpponentsRequirements)
        self._number_ = c.Number.replace(' ','')
        self._rarity_ = rarity[c.Rarity.replace(' ','')]
        
        self._effect_ = load_effect_class(c.EffectClass)
        
        # Setup a few other things
        # self._applied_modifiers_ = []
        self._modifiers_ = []
        self._location_ = location.deck
        
        # Load the instance into the gamestate manager
        gs.new_card(self)
    
    # def __getattr__(self, a):
        # # Will attempt to call the associated function then check the effect class, and finally check the base card class.
        # try:
            # return getattr(self, '_'+a.lower)()
        # except AttributeError:
            # # try:
                # # return getattr(self._effect_class_, a)
            # # except AttributeError:
            # return getattr(Card_Base(self._id), a)
    
    # def __setattr__(self, a, v):
        # # if initialising, write the attribute, else check if it already exists and write it if so, if not, check for the underscore method and use that, finally just write the attribute as is
        # # if not self._initiated:
            # # super(_Card, self).__setattr__(a, v)
        # # else:
        # try:
            # getattr(self, a)
        # except AttributeError:
            # try:
                # getattr(self, '_'+a)(v)
            # except AttributeError:
                # # whisper("adding new attribute to {}".format(self._side_[0]['_name_'][0]))
                # super(_Card, self).__setattr__(a, v)
            # except TypeError:
                # raise StaticAttributeError("Can not change static attribute: {}".format(a))
        # else:
            # super(_Card, self).__setattr__(a, v)

    def get_location(self):
        return self._location_
    def set_location(self, loc, index=None, trigger=True):
        mute()
        oldLoc = self.location
        card = Card_Base(self._id)
        if type(loc) == int:
            index = loc
            loc = oldLoc
        if oldLoc == loc:
            if index:
                if self.inPlay: card.setIndex(index)
                else: card.moveTo(card.group, index)
            return
        g = getGroupFromLocation(loc)
        if g == table:
            card.moveToTable(0, 0)
            if index: card.setIndex(index)
        else:
            if index: card.moveTo(g, index)
            else: card.moveTo(g)
        self._location_ = loc
        gs.changeLoaction(self, loc)
    location = property(get_location, set_location)
        
    def get_boosted(self):
        Card_Base(self._id).alternate == 'Mane Character Boosted'
    def set_boosted(self, val, force=False, trigger=True):
        card = Card_Base(self._id)
        if val == True:
            card.alternate = 'Mane Character Boosted'
        elif val == False:
            card.alternate = ''
    boosted = property(get_boosted, set_boosted)

    def get_faceup(self):
        if cardType.maneCharacter in self.type: return True
        return Card_Base(self._id).isFaceUp
    def set_faceup(self, val, force=False, trigger=True):
        if cardType.maneCharacter in self.type:
            self.set_boosted(set, force, trigger)
        elif val == True:
            self.flipFaceup(force, trigger)
        elif val == False:
            self.flipFacedown(force, trigger)
    faceup = property(get_faceup, set_faceup)
    
    def get_exhausted(self):
        tpeList = self.type
        if cardType.resource in tpeList or cardType.troublemaker in typList or self.is_character():
            if self.is_in_play():
                return card.orientation & Rot90 == Rot90
        return False
    def set_exhausted(self, val, force=False, trigger=True):
        mute()
        if val == True:
            if (force and self.ready) or self.can_exhaust():
                canceled = False
                if trigger: canceled = fire_event(preEvent.exhaust, card=self):
                if force or not canceled:
                    Card_Base(self._id).orientation = Rot90
                    if trigger: fireEvent(event.exhaust, card=self)
        elif val == False:
            if (force and self.exhausted) or self.can_ready():
                canceled = False
                if trigger: canceled = fire_event(preEvent.ready, card=self):
                if force or not canceled:
                    Card_Base(self._id).orientation = Rot0
                    if trigger: fireEvent(event.ready)
    exhausted = property(get_exhausted, set_exhausted)
    exhaust = exhausted
    
    def get_ready(self):
        return not self.exhausted
    def set_ready(self, val, force=False, trigger=True):
        self.set_exhausted(not val, force, trigger)
    ready = property(get_ready, set_ready)
            
    def can_exhaust(self):
        return self._apply_modifiers(modifier.exhaust, self.ready)
            
    def can_ready(self):
        return self._apply_modifiers(modifier.ready, self.exhausted)
    
    # Property values of the card
    def get_name(self, printed=False):
        if printed: return self._side_[self.boosted]['_name_']
        return self._apply_modifiers(modifier.name, self._side_[self.boosted]['_name_'])
    name = property(get_name)
    def get_title(self, printed=False):
        if printed: return self._side_[self.boosted]['_title_']
        return self._apply_modifiers(modifier.title, self._side_[self.boosted]['_title_'])
    title = property(get_title)
    def get_subtitle(self, printed=False):
        if printed: return self._side_[self.boosted]['_subtitle_']
        return self._apply_modifiers(modifier.subtitle, self._side_[self.boosted]['_subtitle_'])
    subtitle = property(get_subtitle)
    def get_traits(self, printed=False):
        if printed: return self._side_[self.boosted]['_traits_']
        return self._apply_modifiers(modifier.traits, self._side_[self.boosted]['_traits_'])
    traits = property(get_traits)
    def get_colors(self, printed=False):
        if printed: return self._side_[self.boosted]['_colors_']
        return self._apply_modifiers(modifier.colors, self._side_[self.boosted]['_colors_'])
    colors = property(get_colors)
    def get_power(self, printed=False):
        if printed: return self._side_[self.boosted]['_name_']
        return self._apply_modifiers(modifier.power, self._side_[self.boosted]['_power_'])
    power = property(get_power)
    def get_keywords(self, printed=False):
        if printed: return self._side_[self.boosted]['_keywords_']
        return self._apply_modifiers(modifier.keywords, self._side_[self.boosted]['_keywords_'])
    keywords = property(get_keywords)
    def get_text(self, printed=False):
        if printed: return self._side_[self.boosted]['_text_']
        return self._apply_modifiers(modifier.text, self._side_[self.boosted]['_text_'])
    text = property(get_text)
    def get_type(self, printed=False):
        if printed: return self._type_
        return self._apply_modifiers(modifier.type, self._type_)
    type = property(get_type)
    def get_cost(self, printed=False):
        if printed: return self._cost_
        return self._apply_modifiers(modifier.cost, self._cost_)
    cost = property(get_cost)
    def get_play_requirements(self, printed=False):
        if printed: return self._play_requirements_
        return self._apply_modifiers(modifier.play_requirements, self._play_requirements_)
    play_requirements = property(get_play_requirements)
    def get_bonus_points(self, printed=False):
        if printed: return self._bonus_points_
        return self._apply_modifiers(modifier.bonus_points, self._bonus_points_)
    bonus_points = property(get_bonus_points)
    def get_your_requirements(self, printed=False):
        if printed: return self._your_requirements_
        return self._apply_modifiers(modifier.your_requirements, self._your_requirements_)
    your_requirements = property(get_your_requirements)
    def get_opponents_requirements(self, printed=False):
        if printed: return self._opponents_requirements_
        return self._apply_modifiers(modifier.opponents_requirements, self._opponents_requirements_)
    opponents_requirements = property(get_opponents_requirements)
    def get_number(self, printed=False):
        if printed: return self._number_
        return self._apply_modifiers(modifier.number, self._number_)
    number = property(get_number)
    def get_rarity(self, printed=False):
        if printed: return self._rarity_
        return self._apply_modifiers(modifier.rarity, self._rarity_)
    rarity = property(get_rarity)
    def get_effects(self, printed=False:
        if printed: return self._effect_
        return self._apply_modifiers(modifier.effect, self._effect_)
    effects = property(get_effects)
    
    # Effect functions of the card
    # TODO: match these up to their effect class counterparts
    def gameload(self):
        for obj in self._effect_class_:
            obj.gameload(self)
    def activate_list(self):
        lst = []
        for obj in self._effect_class_:
            item_list = obj.activate_list(self)
            if len(item) >= 1: lst.append(tupple([obj]+item_list))
        kw_dict = self.keywords
        for obj in kw_dict:
            item_list = kw_dict[obj].activate_list(self)
            if len(item) >= 1: lst.append(tupple([kw_dict[obj]]+item_list))
        return lst
    def activate(self, obj, index = 1):
        return obj.activate(self, index)
    def can_play(self):
        can = True
        for obj in self._effect_class_:
            can &= obj.can_play(self)
        kw_dict = self.keywords
        for obj in kw_dict:
            can &= kw_dict[obj].can_play(self)
        return can
    def enters_play(self):
        for obj in self._effect_class_:
            obj.enters_play(self)
    def leaves_play(self):
        for obj in self._effect_class_:
            obj.leaves_play(self)
    def moved(self):
        for obj in self._effect_class_:
            obj.moved(self)
    def face_up(self):
        for obj in self._effect_class_:
            obj.face_up(self)
    def face_down(self):
        for obj in self._effect_class_:
            obj.face_down(self)
    def confronted(self):
        for obj in self._effect_class_:
            obj.confronted(self)
    def solved(self):
        for obj in self._effect_class_:
            obj.solved(self)
    def replaced(self):
        for obj in self._effect_class_:
            obj.replaced(self)
            
    # Modifiers
    def new_modifier(self, modifier_type):
        mod = Modifier(self, modifier_type)
        self._modifiers_.append(mod)
        # self._applied_modifiers_.append(mod)
        return mod
        
    def _apply_modifiers(self, modifier_type, arg):
        return apply_modifiers(self, modifier_type, arg)
    
    # Directly accessible methods
    def is_character(self):
        type_set = self.type
        return cardType.friend in type_set or cardType.maneCharacter in type_set
    
    def is_in_play(self):
        loc = self.location
        return loc == location.home or loc == location.myProblem or loc == location.oppProblem
    
    # def ready(self, force=False, trigger=True):
        # mute()
        # if (force and self.exhausted) or self.canReady:
            # canceled = False
            # if trigger: canceled = fireEvent(preEvent.ready, card=self):
            # if force or not canceled:
                # Card_Base(self._id).orientation = Rot0
                # if trigger: fireEvent(event.ready, card=self)
    
    # def exhaust(self, force=False, trigger=True):
        # mute()
        # if (force and self.isReady) or self.canExhaust:
            # canceled = False
            # if trigger: canceled = fireEvent(preEvent.exhaust, card=self):
            # if force or not canceled:
                # Card_Base(self._id).orientation = Rot90
                # if trigger: fireEvent(event.exhaust, card=self)

class Effect_Base(object):
    def __init__(self, card):
        self._id = uuid4()
        self.printed = False
    def gameload(self, card): pass
    def activate_list(self, card): return []
    def activate(self, card, index = 1): return ''
    def can_play(self, card): return True
    def new_instance(self, card): pass
    def as_enters_play(self, card): pass
    def enters_play(self, card): pass
    def leaves_play(self, card): pass
    def moved(self, card): pass
    def face_up(self, card): pass
    def face_down(self, card): pass
    def faceoff(self, card): pass
    def flipped(self, card): pass
    def confronted(self, card): pass
    def solved(self, card): pass
    def replaced(self, card): pass
    def __eq__(self, other):
        if other is self: return True
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return NotImplemented
    def __ne__(self, other):
        if other is self: return False
        if isinstance(other, self.__class__):
            return not self == other
        return NotImplemented
    def __hash__(self): return hash(tuple(sorted(self.__dict__.items())))

def load_effect_class(class_text):
    whiteSpace = -1
    try:
        while class_text[0] == ' ':
            whiteSpace += 1
            class_text = class_text[1:]
        class_text = parse_string(class_text, whiteSpace)
        exec(class_text)
        return set((effect(),))
    except IndexError:
        return set()

def parse_string(str, ws):
    if ws == -1: ws = 0
    l = re.split("(/;|/`|;;|`|;,|;\.|; )",str)
    for i in range(len(l)):
        if l[i] == r'/;':    l[i] = ';'
        elif l[i] == r'/`':  l[i] = '`'
        elif l[i] == r';;':  l[i] = '"'
        elif l[i] == r'`':   l[i] = "'"
        elif l[i] == r';,':  l[i] = '<'
        elif l[i] == r';.':  l[i] = '>'
        elif l[i] == r'; ':
            l[i] = "\n"
            try:
                l[i+1] = l[i+1][ws:]
            except IndexError: pass
    return "".join(l)

def intOrNone(n, default=None):
    try: return int(n)
    except ValueError: return default
    
def parseTraits(string):
    l = parseList(string)
    for i in range(len(l)):
        l[i] = trait[l[i]]
    return set(l)
        
def parseColors(string):
    l = parseList(string)
    for i in range(len(l)):
        l[i] = color[l[i]]
    return set(l)

def parseRequirements(string):
    l = parseDict(string)
    d = {}
    for i in l:
        d[color[i[0]]] = int(i[1])
    return d
        
def parseKeywords(card, string):
    kw = {}
    if string == '': return kw
    s = []
    l = re.split("(,|, )",string)
    for i in range(len(l)):
        if l[i] != r', ' and l[i] != r',': s.append(l[i])
    class_text = None
    for v in s:
        n = ''
        while v.endswith(('0','1','2','3','4','5','6','7','8','9')):
            n = v[-1] + n
            v = v[:-1]
        if v.endswith((' ',)): v = v[:-1]
        obj = None
        val = intOrNone(n)
        try:
            if val == None: exec('obj = KW_'+v.replace(' ','_')+'()')
            else: exec('obj = KW_'+v.replace(' ','_')+'('+val+')')
        except NameError:
            if class_text == None:
                class_text = card.EffectClass
                whiteSpace = -1
                try:
                    while class_text[0] == ' ':
                        whiteSpace += 1
                        class_text = class_text[1:]
                    class_text = parse_string(class_text, whiteSpace)
                    exec(class_text)
                except IndexError:
                    raise NoEffectDeffined('Unable to load custom keyword effect: '+v)
            if val == None: exec('obj = KW_'+v.replace(' ','_')+'()')
            else: exec('obj = KW_'+v.replace(' ','_')+'('+val+')')
        kw[keyword[v.replace(' ','')]] = obj
    return kw
            
def parseList(string):
    lst = []
    if string == '': return lst
    l = re.split("(,|, )",string)
    for i in range(len(l)):
        if l[i] != r', ' and l[i] != r',': lst.append(l[i].replace(' ',''))
    return lst
    
def parseDict(string):
    lst = []
    if string == '': return lst
    s = []
    l = [x for x in re.split(",|, | ",string) if x != '']
    for i in range(len(l)):
        if i < len(l):
            if l[i] != r', ' and l[i] != r',' and l[i] != r' ': s.append(l[i])
    for n in range(len(l)):
        if n%2 != 0:
            lst.append([l[n].replace(' ',''),l[n-1]])
    return lst
