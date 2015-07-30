CardBase = Card

def Card(id):
    try:
        return gs.card_dict[id]
    except KeyError:
        return _Card(id)

class _Card(object):
    def __init__(self, id):
        self._id = id
        self._side = [{},{}]
        c = CardBase(id)
        # Front Side
        self._side[0]['_name'] = list(c.Name)
        self._side[0]['_title'] = list(c.Title)
        self._side[0]['_subtitle'] = list(c.Subtitle)
        self._side[0]['_traits'] = parseTraits(c.Traits)
        self._side[0]['_colors'] = parseColors(c.Colors)
        self._side[0]['_power'] = intOrNone(c.Power)
        self._side[0]['_keywords'] = parseKeywords(c.Keywords)
        self._side[0]['_text'] = c.Text
        # Back Side
        if self.Type == "Mane Character":
            alt = "Mane Character Boosted"
            self._side[1]['_name'] = list(c.alternateProperty(alt,'Name'))
            self._side[1]['_title'] = list(c.alternateProperty(alt,'Title'))
            self._side[1]['_subtitle'] = list(c.alternateProperty(alt,'Subtitle'))
            self._side[1]['_traits'] = parseTraits(c.alternateProperty(alt,'Traits'))
            self._side[1]['_colors'] = parseColors(c.alternateProperty(alt,'Colors'))
            self._side[1]['_power'] = intOrNone(c.alternateProperty(alt,'Power'))
            self._side[1]['_keywords'] = parseKeywords(c.alternateProperty(alt,'Keywords'))
            self._side[1]['_text'] = c.alternateProperty(alt,'Text')
        # Common info
        self._type = list(c.Type.replace(' ',''))
        self._cost = intOrNone(c.Cost)
        self._play_requirements = parseRequirements(c.PlayRequirements)
        self._bonus_points = intOrNone(c.BonusPoints)
        self.your_requirements = parseRequirements(c.YourRequirements)
        self.opponents_requirements = parseRequirements(c.OpponentsRequirements)
        self._number = c.Number.replace(' ','')
        self._rarity = c.Rarity.replace(' ','')
        self._effect_class = load_effect_class(c.EffectClass)
        
        # Setup a few other things
        self._location = location.deck
        self._applied_modifiers = []
        self._created_modifiers = []
        
        # Load the instance into the gamestate manager for later use
        gs.card_dict[id] = self
        
    # Will attempt to call the associated function then check the effect class, and finally check the base card class.
    def __getattr__(self, a):
        try:
            return getattr(self, '_'+a.lower)()
        except AttributeError:
            try:
                return getattr(self._effect_class, a)
            except AttributeError:
                return getattr(CardBase(self._id), a)

class Effect_Base(object):
    def activated_list(self): return []
    def activate(self, index = 1): return ''
    def can_play(self): return True
    def enters_play(self): pass
    def leaves_play(self): pass
    def moved(self): pass
    def uncovered(self): pass
    def confronted(self): pass
    def replaced(self): pass
    
def intOrNone(n):
    try: return int(n)
    except: return None
    
def parseTraits(string):
    l = parseList(string)
    for i in range(len(l)):
        l[i] = trait[l[i]]
    return l
        
def parseColors(string):
    l = parseList(string)
    for i in range(len(l)):
        l[i] = color[l[i]]
    return l

def parseRequirements(string):
    l = parseDict(string)
    d = {}
    for i in l:
        d[color[i[0]]] = int(i[1])
    return d
        
def parseKeywords(string):
    d = {}
    if string == '': return d
    s = []
    l = re.split("(,|, )",string)
    for i in range(len(l)):
        if l[i] != r', ' and l[i] != r',': s.append(l[i])
    
    for v in s:
        n = ''
        if v.endswith(('0','1','2','3','4','5','6','7','8','9')):
            n = int(v[-1])
            v = v[:-2]
        d[keyword[v.replace(' ','')]] = n
    return d
            
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
        
def load_effect_class(class_text):
    whiteSpace = -1
    cls = Effect_Base
    try:
        while class_text[0] == ' ':
            whiteSpace += 1
            class_text = csl[1:]
        class_text = parse_string(class_text)
        exec(class_text)
    except IndexError:
        pass
    return cls()
    
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
            except: pass
    return "".join(l)