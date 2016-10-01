def C(card=0,x=0,y=0):
    if type(card) == str:
        log("Creating test card with UUID {}".format(card))
        card = table.create(card, x, y)
    else:
        lst = ('f692c999-91d8-46c5-89d9-f8cf72d4b443', #Cloudchaser
            '57925aaa-fd6f-4fe6-abdb-8ab0f678c223', #Fluttershy, mane
            '817af21e-4bd7-4535-9640-8c1ee9e2e19a', #Special Delivery
            'a63ba886-ba91-4fcf-a67b-1e2b41511cf0', #Critter Cuisine
            '13af9a59-ed0c-43fa-a195-3d334bc9a592') #Yellow Parasprite
        log("Creating test card with UUID {}".format(lst[card]))
        card = table.create(lst[card], x, y)

    log("Created test card {}".format(card))
    return card

def test_cards():
    global c
    c = []
    for i in range(4):
        c.append(C(i))

def _print_pos(args):
    print args.card.c.position

def test_tween(card, tw=None, dtime=0.5):
    if tw is None:
        lst = (linear,easeInQuad,easeOutQuad,easeInOutQuad,easeInCubic,easeOutCubic,easeInOutCubic,easeInQuart,easeOutQuart,easeInOutQuart,easeInQuint,easeOutQuint,easeInOutQuint,easeInSine,easeOutSine,easeInOutSine,easeInExpo,easeOutExpo,easeInOutExpo,easeInCirc,easeOutCirc,easeInOutCirc,easeInElastic,easeOutElastic,easeInOutElastic,easeInBack,easeOutBack,easeInOutBack,easeInBounce,easeOutBounce,easeInOutBounce)
        for _tw in lst:
            alert("Next: {}".format(_tw.__name__))
            test_tween(card, _tw, dtime)
    else:
        for x in _tween(300, dtime=dtime, tween_func=tw):
            card._set_table_position(x)
            update()