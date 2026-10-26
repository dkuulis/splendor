import unittest

from game.constants import SAPPHIRE, RUBY, ONYX, GOLD
from game import Card, State
from game.selection import Selection


class SelectionTests(unittest.TestCase):
    def setUp(self):
        self.state = State()
        self.selection = Selection()
        self.card = Card('selected', 1, RUBY, 1, {})
        self.state.market[1] = [self.card]

    def test_selection_is_pending_and_mutually_exclusive(self):
        state = self.state
        selection = self.selection
        supply = dict(state.supply)
        selection.select_token(RUBY, state)
        selection.select_card(self.card, state)
        self.assertEqual(selection.tokens, {})
        self.assertIs(selection.card, self.card)
        self.assertEqual(state.market[1], [self.card])
        for cards in state.players[0].cards.values():
            self.assertEqual(cards, [])
        self.assertEqual(state.turn.active_player, 0)
        selection.select_token(SAPPHIRE, state)
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {SAPPHIRE: 1})
        self.assertEqual(state.supply, supply)
        selection.deselect_token(SAPPHIRE, state)
        self.assertEqual(selection.tokens, {})

    def test_repeated_gem_clicks_select_available_supply_and_remove_one_at_a_time(self):
        state = self.state
        selection = self.selection
        supply = dict(state.supply)
        for count in range(1, 5):
            selection.select_token(RUBY, state)
            self.assertEqual(selection.tokens, {RUBY: count})
            self.assertEqual(selection.can_take_tokens(state), count == 2)
        self.assertFalse(selection.can_select_token(RUBY, state))
        selection.select_token(RUBY, state)
        self.assertEqual(selection.tokens, {RUBY: 4})
        selection.select_token(SAPPHIRE, state)
        for count in range(3, -1, -1):
            selection.deselect_token(RUBY, state)
            expected = {SAPPHIRE: 1}
            if count:
                expected[RUBY] = count
            self.assertEqual(selection.tokens, expected)
        self.assertEqual(state.supply, supply)
        self.assertEqual(state.current_player.tokens, {})

    def test_card_toggle_and_replacement(self):
        other = Card('other', 1, ONYX, 0, {})
        self.state.market[1].append(other)
        self.selection.select_card(self.card, self.state)
        self.selection.select_card(other, self.state)
        self.assertIs(self.selection.card, other)
        self.selection.select_card(other, self.state)
        self.assertIsNone(self.selection.card)

    def test_invalid_selection_preserves_pending_action(self):
        self.selection.select_card(self.card, self.state)
        self.selection.select_token('unknown', self.state)
        self.state.supply[RUBY] = 0
        self.selection.select_token(RUBY, self.state)
        self.selection.select_card(Card('missing', 1, RUBY, 0, {}), self.state)
        self.assertIs(self.selection.card, self.card)

    def test_non_gold_selection_clears_card_and_gold_but_keeps_other_gems(self):
        state = self.state
        selection = self.selection
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        selection.select_token(RUBY, state)
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {RUBY: 1})
        selection.select_token(SAPPHIRE, state)
        self.assertEqual(selection.tokens, {RUBY: 1, SAPPHIRE: 1})
        self.assertFalse(selection.can_perform_action(state))

    def test_finished_game_cannot_select(self):
        self.state.turn.finished = True
        self.selection.select_card(self.card, self.state)
        self.selection.select_token(RUBY, self.state)
        self.assertIsNone(self.selection.card)
        self.assertEqual(self.selection.tokens, {})

    def test_clear_resets_pending_action_even_after_game_ends(self):
        state = self.state
        selection = self.selection
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        state.turn.finished = True
        selection.clear()
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})
        self.assertEqual(selection.action_kind, 'pass')
        self.assertEqual(state.market[1], [self.card])
        self.assertEqual(state.current_player.tokens, {})

    def test_finished_game_preserves_pending_selection_on_deselect(self):
        state = self.state
        selection = self.selection
        selection.select_token(RUBY, state)
        state.turn.finished = True
        selection.deselect_token(RUBY, state)
        self.assertEqual(selection.tokens, {RUBY: 1})

    def test_independent_selection_uses_supplied_state_without_changing_it(self):
        state = self.state
        selection = Selection()
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'reserve')
        self.assertIsNone(self.selection.card)
        self.assertEqual(self.selection.tokens, {})
        self.assertEqual(state.current_player.tokens, {})
        self.assertEqual(state.market[1], [self.card])

    def test_reservation_replaces_and_toggles_cards(self):
        state = self.state
        selection = self.selection
        other = Card('other', 1, ONYX, 0, {})
        state.market[1].append(other)
        selection.reserve_card(self.card, state)
        selection.reserve_card(other, state)
        self.assertIs(selection.card, other)
        self.assertEqual(selection.action_kind, 'reserve')
        self.assertEqual(selection.tokens, {GOLD: 1})
        selection.reserve_card(other, state)
        self.assertEqual(selection.action_kind, 'pass')
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})

    def test_token_transitions_follow_selection(self):
        state = self.state
        selection = self.selection
        selection.select_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'pass')
        selection.select_card(self.card, state)
        selection.select_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'reserve')
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'buy')
        self.assertIs(selection.card, self.card)
        selection.select_token(RUBY, state)
        selection.select_token(SAPPHIRE, state)
        selection.select_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'take')
        self.assertEqual(selection.tokens, {RUBY: 1, SAPPHIRE: 1})
        self.assertIsNone(selection.card)
        selection.deselect_token(RUBY, state)
        self.assertEqual(selection.action_kind, 'take')
        selection.deselect_token(SAPPHIRE, state)
        self.assertEqual(selection.action_kind, 'pass')
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.action_kind, 'pass')

    def test_invalid_reservation_preserves_pending_buy(self):
        state = self.state
        selection = self.selection
        selection.select_card(self.card, state)
        reserved = Card('reserved', 1, RUBY, 0, {})
        state.current_player.reserved_cards.append(reserved)
        for card in (reserved, Card('missing', 1, RUBY, 0, {})):
            selection.reserve_card(card, state)
            self.assertEqual(selection.action_kind, 'buy')
            self.assertIs(selection.card, self.card)
            self.assertEqual(selection.tokens, {})
        state.turn.finished = True
        selection.reserve_card(self.card, state)
        self.assertEqual(selection.action_kind, 'buy')

    def test_transition_matrix(self):
        # Each destination includes the exact card and tokens, not just intent.
        expected = {
            'gem': ['gems', 'gems', 'gems', 'two_gems', 'gems'],
            'gold': ['empty', 'reserve_initial', 'reserved_initial', 'gems', 'two_gold_initial'],
            'affordable': ['buy', 'buy', 'buy', 'buy', 'buy'],
            'unaffordable': ['reserve', 'reserve', 'reserve', 'reserve', 'reserve'],
            'reserved': ['reserved', 'reserved', 'reserved', 'reserved', 'reserved'],
            'unaffordable_reserved': ['empty', 'buy_initial', 'reserved_initial', 'gems', 'reserve_initial'],
            'remove_gem': ['empty', 'buy_initial', 'reserved_initial', 'empty', 'reserve_initial'],
            'remove_gold': ['empty', 'buy_initial', 'reserved_initial', 'gems', 'buy_initial'],
            'remove_card': ['empty', 'empty', 'reserved_initial', 'gems', 'empty'],
            'remove_reserved': ['empty', 'buy_initial', 'empty', 'gems', 'reserve_initial'],
        }
        for event, destinations in expected.items():
            for index, destination in enumerate(destinations):
                with self.subTest(event=event, initial=index):
                    state = State()
                    selection = Selection()
                    initial_card = Card('initial', 1, RUBY, 0, {})
                    market = Card('affordable', 1, RUBY, 0, {})
                    costly = Card('costly', 1, RUBY, 0, {RUBY: 2})
                    initial_reserved = Card('initial_reserved', 1, RUBY, 0, {})
                    reserved = Card('reserved', 1, RUBY, 0, {})
                    costly_reserved = Card('costly_reserved', 1, RUBY, 0, {RUBY: 2})
                    state.market[1] = [initial_card, market, costly]
                    state.current_player.reserved_cards = [initial_reserved, reserved, costly_reserved]
                    if index in (1, 4):
                        selection.select_card(initial_card, state)
                    elif index == 2:
                        selection.select_card(initial_reserved, state)
                    elif index == 3:
                        selection.select_token(SAPPHIRE, state)
                    if index == 4:
                        selection.select_token(GOLD, state)
                    supply = dict(state.supply)
                    if event == 'gem':
                        selection.select_token(RUBY, state)
                    elif event == 'gold':
                        selection.select_token(GOLD, state)
                    elif event in ('affordable', 'unaffordable', 'reserved', 'unaffordable_reserved'):
                        selection.select_card({
                            'affordable': market, 'unaffordable': costly,
                            'reserved': reserved, 'unaffordable_reserved': costly_reserved,
                        }[event], state)
                    elif event == 'remove_gem':
                        selection.deselect_token(SAPPHIRE, state)
                    elif event == 'remove_gold':
                        selection.deselect_token(GOLD, state)
                    elif event == 'remove_card' and index in (1, 4):
                        selection.select_card(initial_card, state)
                    elif event == 'remove_reserved' and index == 2:
                        selection.select_card(initial_reserved, state)
                    outcomes = {
                        'empty': ('pass', None, {}),
                        'gems': ('take', None, {RUBY: 1} if event == 'gem' else {SAPPHIRE: 1}),
                        'two_gems': ('take', None, {RUBY: 1, SAPPHIRE: 1}),
                        'buy': ('buy', market, {}),
                        'buy_initial': ('buy', initial_card, {}),
                        'reserved': ('buy', reserved, {}),
                        'reserved_initial': ('buy', initial_reserved, {}),
                        'reserve': ('reserve', costly, {GOLD: 1}),
                        'reserve_initial': ('reserve', initial_card, {GOLD: 1}),
                        'two_gold_initial': ('reserve', initial_card, {GOLD: 2}),
                    }
                    self.assertEqual((selection.action_kind, selection.card, selection.tokens),
                                     outcomes[destination])
                    self.assertEqual(state.supply, supply)
                    self.assertEqual(state.current_player.tokens, {})
                    self.assertEqual(state.turn.active_player, 0)

    def test_unaffordable_reservation_keeps_gold_until_card_is_deselected(self):
        state = self.state
        selection = self.selection
        self.card.cost = {RUBY: 2}
        selection.select_card(self.card, state)
        selection.deselect_token(GOLD, state)
        self.assertEqual(selection.tokens, {GOLD: 1})
        self.assertEqual(selection.action_kind, 'reserve')
        selection.select_card(self.card, state)
        self.assertIsNone(selection.card)
        self.assertEqual(selection.tokens, {})
        self.assertEqual(selection.action_kind, 'pass')

    def test_removing_one_of_multiple_gems_keeps_take(self):
        selection = self.selection
        selection.select_token(RUBY, self.state)
        selection.select_token(SAPPHIRE, self.state)
        selection.deselect_token(RUBY, self.state)
        self.assertEqual(selection.tokens, {SAPPHIRE: 1})
        self.assertEqual(selection.action_kind, 'take')
