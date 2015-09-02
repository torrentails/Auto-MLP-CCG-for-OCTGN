#-----------------------------------------------------------------------
# Premiere keywords
#-----------------------------------------------------------------------
class KW_Caretaker(Keyword_Base):
    def new_instance(self, card)
        # Create a new power modifier
        mod = card.new_modifier(self, modifier.power)
        self.modifier.add(mod)
        # Apply it only under the right conditions
        def condition(self, card):
            found_critter = False
            if card.is_at_problem:
                for c in cards_at_location(card.location, me)
                    if cardType.friend in c.type and trait.critter in c.traits:
                        found_critter = True
                        break
            return found_critter
        mod.condition = condition
        # Increase its power by one
        def action(self, card, power): return power + 1
        mod.action = action

class KW_Inspired(Keyword_Base):
    def new_instance(self, card):
        # Increment inspired effects value
        gs.write('inspired_effects', gs.read('inspired_effects', 0, me)+1, me)
        # If the only inspired effect, create a new start of phase event
        if gs.read('inspired_effects', 0, me) == 1:
            evt = new_event(event.startOfPhase)
            # set up the conditions
            def condition(self): return gs.is_phase(phase.main, me)
            evt.condition = condition
            # set up the actions
            def action(self):
                mute()
                deck = players[1].Deck
                inspired_num = gs.read('inspired_effects', 0, me)
                card_list = deck.top(inspired_num)
                if card_list == None: return
                elif inspired_num == 1:
                    if confirm("Do you want to put {} back on top of {}'s deck?".format(card_list, players[1])):
                        notifyAll("{} used Inspired to put one card on the top of {}'s deck.".format(me, players[1]))
                    else:
                        card_list.moveToBottom(deck)
                        notifyAll("{} used Inspired to put one card on the bottom of {}'s deck.".format(me, players[1]))
                    update()
                else:
                    cards_top = selectCard(card_list, min = 0, max = inspired_num, title = "Choose cards to put on top", question = "Select, in any order, the cards to put on the top of {}'s deck.".format(players[1]))
                    for c in cards_top:
                        card_list.remove(c)
                    if len(card_list) <= 1:
                        cards_bottom = card_list
                    else:
                        cards_bottom = selectCard(card_list, min = 0, max = len(card_list), title = "Choose cards to put on bottom", question = "Select, in any order, the cards to put on the bottom of {}'s deck.".format(players[1]))
                    
                    # TODO: Might need to take control of cards to move them.
                    cards_top.reverse()
                    for c in cards_top:
                        c.moveTo(deck,0)
                    for c in cards_bottom:
                        c.moveToBottom(deck)
                    update()
                        
                    if len(cards_top) > 0 and len(cards_bottom) == 0:
                        notifyAll("{} used Inspired to put {} cards on the top of {}'s deck.".format(me, len(cards_top), players[1]))
                    elif len(cards_top) == 0 and len(cards_bottom) > 0:
                        notifyAll("{} used Inspired to put {} cards on the bottom of {}'s deck.".format(me, len(cards_bottom), players[1]))
                    elif len(cards_top) == 1 and len(cards_bottom) == 1:
                        notifyAll("{} used Inspired to put a card on the top and a card on the bottom of {}'s deck.".format(me, players[1]))
                    elif len(cards_top) > 1 and len(cards_bottom) == 1:
                        notifyAll("{} used Inspired to put {} cards on the top and a card on the bottom of {}'s deck.".format(me, len(cards_top), players[1]))
                    elif len(cards_top) == 1 and len(cards_bottom) > 1:
                        notifyAll("{} used Inspired to put a card on the top and {} cards on the bottom of {}'s deck.".format(me, len(cards_bottom), players[1]))
                    else:
                        notifyAll("{} used Inspired to put {} cards on the top and {} cards on the bottom of {}'s deck.".format(me, len(card_top), len(cards_bottom), players[1]))
            evt.action = action
            # store the event for later use
            gs.write('inspired_event', evt, me)
    def leaves_play(self, card):
        # Read the amount of inspired effects minus 1
        inspired_num = gs.read('inspired_effects', 0, me)-1
        # Write that number back into inspired effects
        gs.write('inspired_effects', max(inspired_num, 0), me)
        # If there are no inspired effects left, remove the inspired event
        if inspired_num <= 0:
            evt = gs.read('inspired_event', None, me)
            try: evt.remove()
            except AttributeError: return
            else: gs.clearData('inspired_event', me)
    def face_down(self, card): self.leaves_play(card)

class KW_Random(Keyword_Base):
    def faceoff(self, card):
        # Crate a new event to before each card is flipped
        preevt = card.new_event(preEvent.flipCard)
        # Make sure the car being flipped is ours
        preevt.condition = lambda self, card: card.controller == me
        # Reset if random has been used in a previous flip
        def action(self, card): gs.write('random_used', False, me)
        preevt.action = action
        # Remove this event at the end of the faceoff
        preevt.remove_on_event = event.faceoffCleanup
        
        # Create another event to fire after a card is flipped
        evt = card.new_event(event.flipCard)
        # Check that the card is ours, has 1 power and that we haven't used random for this card yet
        def condition(self, card): return card.controller == me and card.power == 1 and not gs.read('random_used', False, me) and self.card.involved_in_faceoff()
        evt.condition = condition
        def action(self, card):
            # let the game know that random has triggered for this card
            gs.write('random_used', True, me)
            # Ask if the player would like to re-flip
            if confirm("Would you like to activate Random to ignore the power of {} and flip a new card?".format(card)):
                # Ignore the flipped card's power
                card.ignoreFlippedPower()
                # Flip a new card
                flipFaceoffCard(me)
        evt.action = action
        # Ensure the trigger only happens once for each Random effect
        evt.trigger_once = True
        # Remove this event at the end of the faceoff
        evt.remove_on_event = event.faceoffCleanup

class KW_Stubborn(Keyword_Base):
    def new_instance(self, card):
        # TODO: Write once we figure out how exhaustion code affects the card
        pass

class KW_Studious(Keyword_Base):
    def faceoff(self, card):
        # Create a new resolve faceoff event
        evt = card.new_event(event.resolveFaceoff)
        # Check that the player is the winner of the faceoff
        def condition(self):
            return gs.faceoff_winner == me and not gs.read('studious_used', False, me) and self.card.involved_in_faceoff()
        evt.condition = condition
        # Give the player an action token
        def action(self):
            gs.write('studious_used', True, me)
            gainAT(me)
        evt.action = action
        # Remove the event and reset studious at the end of the faceoff
        def cleanup_action(self):
            try: evt.remove()
            except: pass
            gs.write('studious_used', False, me)
        new_event(event.faceoffCleanup).action = cleanup_action

class KW_Swift(Keyword_Base):
    def new_instance(self, card):
        # Create a new movement modifier
        mod = card.new_modifier(self, modifier.movement)
        self.modifier.add(mod)
        # Check that it was a standard, main phase move
        def condition(self, card): return cm.is_main_pahse_move
        mod.condition = condition
        # Reduce its main phase movement by one
        def action(self, card, cost): return max(cost-1, 0)
        mod.action = action

class KW_Villain(Keyword_Base):
    def face_up(self, card):
        # When turned face up, frighten each friend at it's problem
        for c in card.location:
            if cardType.friend in c.type:
                c.frighten()

#-----------------------------------------------------------------------
# Canterlot Nights keywords
#-----------------------------------------------------------------------
class KW_Pumped(Keyword_Base):
    def faceoff(self, card):
        # Create a new event to trigger at the end of the faceoff
        evt = card.new_event(event.endFaceoff)
        def condition(self):
            # Get a list of flipped cards we control
            lst = [c for c in cm.flippedCards if c.controller == me]
            # Check that we did actually flip cards and that the Pumped card was actually involved in the faceoff
            return len(lst) >= 1 and self.card.involved_in_faceoff() and confirm("Would you like to banish a card beneath {} for Pumped?".format(self.card))
        evt.condition = condition
        def action(self):
            # We need to build the list again
            lst = [c for c in cm.flippedCards if c.controller == me]
            # If there was more than one card flipped during the faceoff, we need to ask which one the player wants to banish
            if len(lst) > 1:
                dlg = askDlg(lst)
                dlg.title="Chose a card for pumped."
                dlg.text="Choose a card to banish beneath {}".format(self.card))
                lst = dlg.show()
            # Banish the chosen card beneath the Pumped card
            self.card.banish_cards_beneath(lst)
        evt.action = action
        # Remove the event during the faceoffs clean up
        evt.remove_on_event(event.faceoffCleanup)
        
class KW_Supportive(Keyword_Base):
    def new_instance(self, card):
        # Create a new modifier for power
        mod = card.new_modifier(self, modifier.power)
        self.modifier.add(mod)
        # We need to store the creating effect so that we car retrieve the Supportive value
        # mod.effect = self
        def condition(self, card):
            # Check that the card is at a problem
            if card.is_at_problem:
                # For each card at this location, check if it is ours and that it's a Mane Character
                for c in [c for c in cards_at_location(card.location) if c.controller == me and cardType.maneCharacter in c.type]:
                    # if c.controller == me and cardType.maneCharacter in c.type:
                    for col in card.colors:
                        # Cross reference the colors of the two cards and return True if there is a match
                        if col in c.colors:
                            return True
            # Otherwise, no match is found, so we return False
            return False
        mod.condition = condition
        # Add power equal to the Supportive value
        def action(self, card, power): return power + self.value
        mod.action = action

#-----------------------------------------------------------------------
# Crystal Games keywords
#-----------------------------------------------------------------------
class KW_Prismatic(Keyword_Base):
    def new_instance(self, card):
        # Create a new color modifier
        mod = card.new_modifier(self, modifier.color)
        self.modifier.add(mod)
        def action(self, card, colorList):
            # Get a list of our cards in play that also have the crystal trait
            lst = [c for c in gs.cards_in_play(me) if trait.crystal in c.traits]
            for c in lst:
                for col in c.colors:
                    # If the card doesn't have the color, add it to the list
                    if col not in colorList: colorList.append(col)
            return colorList
        mod.action = action

class KW_Teamwork(Keyword_Base):
    def new_instance(self, card):
        # Created two new modifiers, one for the keywords and one for the effects
        mod_effect = card.new_modifier(self, modifier.effect)
        mod_kword = card.new_modifier(self, modifier.keyword)
        self.modifier.add(mod_effect)
        self.modifier.add(mod_kword)
        # Store the printed effects set for use later
        mod_effect.lst = card.get_effects(printed=True)
        # Likewise for the keywords, excluding the Teamwork keyword
        mod_kword.lst = [kw for kw in card.get_keywords(printed=True).items() if kw[0] != keyword.teamwork]
        # Check that the card is a friend and shares a trait with the Teamwork card
        def condition(self, card):
            if card.controller == me and cardType.friend in card.type:
                for t in self.card.traits:
                    if t in card.traits: return True
            return False
        mod_effect.condition = condition
        mod_kword.condition = condition
        # Add the effect to the set
        def effect_action(self, card, effect_set):
            for effect in self.lst:
                effect_set.add(effect.__class__(card))
            return effect_set
        mod_effect.action = effect_action
        # Add the keywords to the dict
        def kword_action(self, card, kw_dict):
            for kw in [kw for kw in self.lst if kw not in kw_dict]:
                if kw[0] not in kw_dict: kw_dict[kw[0]]=kw[1].__class__(card, kw[1].value))
            return kw_dict
        mod_kword.action = kword_action
        # Apply only to cards at it's location
        mod_effect.applies_to = [card.get_location]
        mod_kword.applies_to = [card.get_location]

#-----------------------------------------------------------------------
# Absolute Discord keywords
#-----------------------------------------------------------------------
# class Chaos(Keyword_Base):

#-----------------------------------------------------------------------
# Equestrian Odysseys keywords
#-----------------------------------------------------------------------
class KW_Calming(Keyword_Base):
    def new_instance(self, card):
        mod = card.new_modifier(self, modifier.power)
        mod.condition = lambda self, card: card.entered_play_this_turn()
        mod.action = lambda self, card, power: power - self.value
        mod.applies_to = [card.get_location]

class KW_Competitive(Keyword_Base):
    def new_instance(self, card):
        mod = card.new_modifier(self, modifier.power)
        mod.condition = lambda self, card: card.involved_in_faceoff()
        mod.action = lambda self, card, power: power + self.value

class KW_Diligent(Keyword_Base):
    def faceoff(self, card):
        evt = card.new_event(event.resolveFaceoff)
        evt.value = self.value
        def condition(self):
            return gs.faceoff_winner == me and self.card.involved_in_faceoff()
        evt.condition = condition
        def action(self):
            self.card.add_counter(plus_1_power, self.value)
        evt.action = action
        # Remove the event at the end of the faceoff
        evt.remove_on_event(event.faceoffCleanup)

class KW_Eccentric(Keyword_Base):
    def new_instance(self, card):
        mod = card.new_modifier(self, modifier.opposingConfrontRequirements)
        mod.condition = lambda self, card: cardType.problem in card.type
        def action(self, card, reqs):
            try: reqs[color.wild] += self.value
            except KeyError: reqs[color.wild] = self.value
            return reqs
        mod.action = action
        mod.applies_to = [card.get_location]

class KW_Meticulous(Keyword_Base):
    def new_instance(self, card):
        evt = card.new_event(event.startOfTurn)
        evt.value = self.value
        def condition(self):
            if gs.turn_player = me:
                if self.value == 1:
                    return confirm("Would you like to use Meticulous to look at the top card of your deck?")
                elif self.value > 1:
                    return confirm("Would you like to use Meticulous to look at the top {} cards of your deck?".format(self.value))
            return False
        evt.condition = condition
        def action(self):
            if self.value == 0: return
            elif self.value == 1:
                card = me.Deck.top()
                if confirm("Would you like to put {} on the top of your deck?".format(card)):
                    notifyAll("{} used Meticulous to put a card on the top of their deck.".format(me))
                    card.move_to(me.Deck)
                else:
                    notifyAll("{} used Meticulous to put a card on the bottom of their deck.".format(me))
                    card.move_to_bottom(me.Deck)
            else:
                card_list = me.Deck.top(self.value)
                dlg = askDlg(card_list)
                dlg.title = "Choose cards to put on top."
                dlg.text = "Choose, in order, the cards you want to put on top of your deck."
                dlg.min = 0
                dlg.max = self.value
                cards_top = dlg.show()
                
                for c in cards_top:
                    card_list.remove(c)
                if len(card_list) <= 1:
                    cards_bottom = card_list
                else:
                    dlg = askDlg(card_list)
                    dlg.title = "Choose cards to put on bottom."
                    dlg.text = "Choose, in order, the cards to put on the bottom of your deck."
                    dlg.min = len(card_list)
                    dlg.max = len(card_list)
                    cards_bottom = dlg.show()
                
                cards_top.reverse()
                for c in cards_top:
                    c.move_to(me.Deck)
                for c in cards_bottom:
                    c.move_to_bottom(me.Deck)
                update()
                    
                if len(cards_top) > 0 and len(cards_bottom) == 0:
                    notifyAll("{} used Meticulous to put {} cards on the top of their deck.".format(me, len(cards_top)))
                elif len(cards_top) == 0 and len(cards_bottom) > 0:
                    notifyAll("{} used Meticulous to put {} cards on the bottom of their deck.".format(me, len(cards_bottom)))
                elif len(cards_top) == 1 and len(cards_bottom) == 1:
                    notifyAll("{} used Meticulous to put a card on the top and a card on the bottom of their deck.".format(me))
                elif len(cards_top) > 1 and len(cards_bottom) == 1:
                    notifyAll("{} used Meticulous to put {} cards on the top and a card on the bottom of their deck.".format(me, len(cards_top)))
                elif len(cards_top) == 1 and len(cards_bottom) > 1:
                    notifyAll("{} used Meticulous to put a card on the top and {} cards on the bottom of their deck.".format(me, len(cards_bottom)))
                else:
                    notifyAll("{} used Meticulous to put {} cards on the top and {} cards on the bottom of their deck.".format(me, len(card_top), len(cards_bottom)))
        evt.action = action
    
        ## TODO: Can use this code for a better Inspired but too lazy to move it right now.
        # gs.write('meticulous_value', gs.read('meticulous_value', 0, me)+self.value, me)
        # evt = card.new_event(event.startOfTurn)
        # evt.value = self.value
        # def condition(self):
            # if gs.turn_player = me and not gs.read('meticulous_used', False, me):
                # val = gs.read('meticulous_value', 0, me)
                # if val == 1:
                    # return confirm("Would you like to activate Meticulous to look at the top card of your deck?")
                # elif val > 1:
                    # return confirm("Would you like to activate Meticulous to look at the top {} cards of your deck?".format(val))
            # return False
        # evt.condition = condition
        # def action(self):
            # val = gs.read('meticulous_value', 0, me)
            # if val == 0: return
            # elif val == 1:
                # card = me.Deck.top()
                # if confirm("Would you like to put {} on the top of your deck?".format(card)):
                    # notifyAll("{} used Meticulous to put a card on the top of their deck.".format(me))
                # else:
                    # card.moveToBottom(me.Deck)
                    # notifyAll("{} used Meticulous to put a card on the bottom of their deck.".format(me))
            # else:
                # card_list = me.Deck.top(val)
                # dlg = askDlg(card_list)
                # dlg.title = "Choose cards to put on top."
                # dlg.text = "Choose, in order, the cards you want to put on top of your deck."
                # dlg.min = 0
                # dlg.max = val
                # cards_top = dlg.show()
                
                # for c in cards_top:
                    # card_list.remove(c)
                # if len(card_list) <= 1:
                    # cards_bottom = card_list
                # else:
                    # dlg = askDlg(card_list)
                    # dlg.title = "Choose cards to put on bottom."
                    # dlg.text = "Choose, in order, the cards to put on the bottom of your deck."
                    # dlg.min = len(card_list)
                    # dlg.max = len(card_list)
                    # cards_bottom = dlg.show()
                
                # cards_top.reverse()
                # for c in cards_top:
                    # c.moveTo(deck,0)
                # for c in cards_bottom:
                    # c.moveToBottom(deck)
                # update()
                    
                # if len(cards_top) > 0 and len(cards_bottom) == 0:
                    # notifyAll("{} used Meticulous to put {} cards on the top of their deck.".format(me, len(cards_top)))
                # elif len(cards_top) == 0 and len(cards_bottom) > 0:
                    # notifyAll("{} used Meticulous to put {} cards on the bottom of their deck.".format(me, len(cards_bottom)))
                # elif len(cards_top) == 1 and len(cards_bottom) == 1:
                    # notifyAll("{} used Meticulous to put a card on the top and a card on the bottom of their deck.".format(me))
                # elif len(cards_top) > 1 and len(cards_bottom) == 1:
                    # notifyAll("{} used Meticulous to put {} cards on the top and a card on the bottom of their deck.".format(me, len(cards_top)))
                # elif len(cards_top) == 1 and len(cards_bottom) > 1:
                    # notifyAll("{} used Meticulous to put a card on the top and {} cards on the bottom of their deck.".format(me, len(cards_bottom)))
                # else:
                    # notifyAll("{} used Meticulous to put {} cards on the top and {} cards on the bottom of their deck.".format(me, len(card_top), len(cards_bottom)))
        # evt.action = action
        # def cleanup(self):
            # gs.write('meticulous_value', max(gs.read('meticulous_value', 0, me)-self.value, 0), me)
        # evt.cleanup = cleanup

class KW_Showy(Keyword_Base):
    def new_instance(self, card):
        mod = card.new_modifier(modifier.movementCost, self)
        mod.condition = lambda self, card, cost: card.controller != me
        mod.action = lambda self, card, cost: cost + self.value
        mod.applies_to = [card.get_location]

class KW_Vexing(Keyword_Base):
    def new_instance(self, card):
        evt = card.new_event(preEvent.confront)
        def condition(self):
            problem = cm.problem_confonted
            return cm.confronting_player != me and problem == self.card.at_problem() and confirm("{} is about to confront {}. Would you like to activate Vexing on {}?".format(players[1], problem, self.card))
        evt.condition = condition
        def action(self):
            self.card.retire()
            return False
        evt.action = action