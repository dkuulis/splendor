import ast
import copy
import random
import unittest
from itertools import combinations, combinations_with_replacement
from pathlib import Path

from game.card import Card
from game.constants import DIAMOND, EMERALD, GOLD, ONYX, RUBY, SAPPHIRE, TOKENS
from game.initialize import create_initial_state
from game.noble import Noble
from game.selection import Selection
from game.state import State
from simulation import Card as SimulationCard, Noble as SimulationNoble, State as SimulationState
from simulation import generate_moves


def game_card_value(card):
    return card.tier - 1, TOKENS.index(card.token), card.points, tuple(card.cost.get(token, 0) for token in TOKENS)


def card_value(card):
    return card.tier, card.token, card.points, card.cost


def game_noble_value(noble):
    return noble.points, tuple(noble.requirements.get(token, 0) for token in TOKENS)


def noble_value(noble):
    return noble.points, noble.requirements


def game_snapshot(state):
    return {
        "supply": list(state.supply.get(token, 0) for token in TOKENS),
        "market": [sorted(game_card_value(card) for card in state.market[tier]) for tier in (1, 2, 3)],
        "decks": [[game_card_value(card) for card in state.decks[tier]] for tier in (1, 2, 3)],
        "nobles": [game_noble_value(noble) for noble in state.nobles],
        "tokens": [[player.tokens.get(token, 0) for token in TOKENS] for player in state.players],
        "discounts": [[player.discounts.get(token, 0) for token in TOKENS] for player in state.players],
        "token_count": [player.token_count for player in state.players],
        "card_count": [player.card_count for player in state.players],
        "points": [player.points for player in state.players],
        "reserved": [sorted(game_card_value(card) for card in player.reserved_cards) for player in state.players],
        "purchased": [sorted(game_card_value(card) for cards in player.cards.values() for card in cards)
                      for player in state.players],
        "owned_nobles": [sorted(game_noble_value(noble) for noble in player.nobles)
                         for player in state.players],
    }


def reserved_indices(state, player_index):
    return [index for index, card in enumerate(state.cards)
            if card.owner == player_index and not card.purchased]


def snapshot(state):
    return {
        "supply": state.supply[:],
        "market": [sorted(card_value(state.cards[index]) for index in row) for row in state.market_indices],
        "decks": [[card_value(card) for card in state.cards[start:end]]
                  for start, end in zip(state.deck_starts, state.deck_ends)],
        "nobles": [noble_value(noble) for noble in state.nobles if noble.owner is None],
        "tokens": [player.tokens[:] for player in state.players],
        "discounts": [player.discounts[:] for player in state.players],
        "token_count": [player.token_count for player in state.players],
        "card_count": [player.card_count for player in state.players],
        "points": [player.points for player in state.players],
        "reserved": [sorted(card_value(state.cards[index]) for index in reserved_indices(state, player_index))
                     for player_index in range(2)],
        "purchased": [sorted(card_value(card) for card in state.cards
                             if card.owner == player_index and card.purchased)
                      for player_index in range(2)],
        "owned_nobles": [sorted(noble_value(noble) for noble in state.nobles if noble.owner == player)
                         for player in range(2)],
    }


def take_witness(move, state):
    # Find an independently validated UI take whose required returns produce
    # the simulation's net vector. The simulator need not store this witness.
    for size in range(1, 4):
        for tokens in combinations_with_replacement(TOKENS[1:], size):
            selection = Selection()
            selection.tokens = {token: tokens.count(token) for token in tokens}
            if not selection.can_take_tokens(state):
                continue
            returned = [selection.tokens.get(token, 0) - delta
                        for token, delta in zip(TOKENS, move.tokens)]
            excess = max(0, state.current_player.token_count + size - 10)
            if (sum(returned) == excess and all(amount >= 0 for amount in returned)
                    and all(amount <= state.current_player.tokens.get(token, 0)
                            + selection.tokens.get(token, 0)
                            for token, amount in zip(TOKENS, returned))):
                return selection.tokens
    raise AssertionError("No legal take/return sequence for " + str(move.tokens))


def selection_for(move, state, position):
    selection = Selection()
    selection.returning = state.return_required
    if move.card_index is not None:
        card = position.cards[move.card_index]
        if card.owner is not None:
            selection.card = next(candidate for candidate in state.current_player.reserved_cards
                                  if game_card_value(candidate) == card_value(card))
        else:
            selection.card = next(candidate for candidate in state.market[card.tier + 1]
                                  if game_card_value(candidate) == card_value(card))
    if move.kind == "take":
        selection.tokens = take_witness(move, state)
    elif move.kind == "reserve":
        selection.tokens = {GOLD: 1}
    else:
        selection.tokens = {}
    return selection


def perform_game_move(move, source, position):
    # Use the desktop's strict collection rules for either simulated player.
    source.current_player.is_ai = False
    selection = selection_for(move, source, position)
    if move.kind == "reserve" and source.supply.get(GOLD, 0) == 0:
        # Simulation permits a goldless reservation; the desktop UI currently
        # requires gold. Reuse its market/turn rules with no token transfer.
        assert len(source.current_player.reserved_cards) < 3
        assert selection.card in source.market[selection.card.tier]
        assert not any(move.tokens)
        source.current_player.reserved_cards.append(selection.card)
        source.remove_market_card(selection.card)
        source.finish_turn(passed=False)
        return
    assert selection.can_perform_action(source)
    collected = dict(selection.tokens)
    selection.perform_action(source)
    if move.kind in ("take", "reserve") and source.return_required:
        selection.tokens = {token: collected.get(token, 0) - amount
                            for token, amount in zip(TOKENS, move.tokens)
                            if collected.get(token, 0) != amount}
        assert selection.can_perform_action(source)
        selection.perform_action(source)


def move_key(kind, location, tokens):
    return kind, location, tuple(tokens)


class SimulationTests(unittest.TestCase):
    def check_moves(self, source):
        state = SimulationState.from_game(source)
        player = source.turn.active_player
        before = snapshot(state)
        self.assertEqual(before, game_snapshot(source))
        cursors = state.deck_starts[:]
        cards = state.cards[:]
        market = [row[:] for row in state.market_indices]
        card_status = [(card.owner, card.purchased) for card in state.cards]
        nobles = state.nobles[:]
        owners = [noble.owner for noble in nobles]
        moves = generate_moves(state, player)
        self.assertEqual(snapshot(state), before)
        for move in moves:
            with self.subTest(kind=move.kind, card_index=move.card_index, tokens=move.tokens):
                effect = vars(move).copy()
                expected = copy.deepcopy(source)
                perform_game_move(move, expected, state)
                move.make(state, player)
                self.assertEqual(vars(move), effect)
                self.assertEqual(snapshot(state), game_snapshot(expected))
                move.unmake(state, player)
                self.assertEqual(vars(move), effect)
                self.assertEqual(snapshot(state), before)
                self.assertEqual(state.deck_starts, cursors)
                self.assertEqual(state.cards, cards)
                for row, previous_row in zip(state.market_indices, market):
                    self.assertCountEqual(row, previous_row)
                self.assertEqual([(card.owner, card.purchased) for card in state.cards], card_status)
                self.assertEqual(state.nobles, nobles)
                self.assertEqual([noble.owner for noble in state.nobles], owners)
        self.assertEqual(game_snapshot(source), before)
        return state, moves

    def test_initial_moves_match_game_and_restore_state(self):
        for is_ai in (False, True):
            source = create_initial_state(7)
            source.current_player.is_ai = is_ai
            _, moves = self.check_moves(source)
            self.assertEqual(sum(move.kind == "take" for move in moves), 15)
            self.assertEqual(sum(move.kind == "reserve" for move in moves), 12)

    def test_generation_is_complete_against_selection_permissions(self):
        for active in (0, 1):
            for held in (0, 8, 9, 10):
                source = create_initial_state(3)
                source.turn.active_player = active
                player = source.current_player
                player.is_ai = False
                player.tokens = {GOLD: 3, RUBY: 4, DIAMOND: held - 7} if held >= 8 else {}
                source.supply[SAPPHIRE] = 0
                source.supply[EMERALD] = 3
                player.reserved_cards = [Card("reserved", 1, ONYX, 1, {RUBY: 3})]
                expected = set()
                cards = [card for row in source.market.values() for card in row] + player.reserved_cards
                candidates = []
                for card in cards:
                    candidates.extend((("buy", card, {}), ("reserve", card, {GOLD: 1})))
                for size in range(1, 4):
                    for tokens in combinations_with_replacement(TOKENS, size):
                        counts = {token: tokens.count(token) for token in tokens}
                        candidates.append(("take", None, counts))
                for kind, card, tokens in candidates:
                    selection = Selection()
                    selection.returning = source.return_required
                    selection.card = card
                    selection.tokens = tokens
                    if selection.action_kind == kind and selection.can_perform_action(source):
                        if kind == "buy" and card in player.reserved_cards:
                            kind = "buy_reserved"
                        counts = [tokens.get(token, 0) for token in TOKENS]
                        if card is None:
                            location = None
                        elif card in player.reserved_cards:
                            location = ("reserved", player.reserved_cards.index(card))
                        else:
                            location = (card.tier - 1, source.market[card.tier].index(card))
                        if kind in ("take", "reserve"):
                            excess = max(0, player.token_count + sum(counts) - 10)
                            for returned_tokens in combinations_with_replacement(TOKENS, excess):
                                returned = [returned_tokens.count(token) for token in TOKENS]
                                if all(back <= player.tokens.get(token, 0) + taken
                                       for token, back, taken in zip(TOKENS, returned, counts)):
                                    net = [taken - back for taken, back in zip(counts, returned)]
                                    expected.add(move_key(kind, location, net))
                        else:
                            payment = player.card_payment(card)
                            expected.add(move_key(kind, location,
                                                  [-payment.get(token, 0) for token in TOKENS]))
                state = SimulationState.from_game(source)
                actual = []
                for move in generate_moves(state, active):
                    if move.card_index is None:
                        location = None
                    elif state.cards[move.card_index].owner is not None:
                        location = ("reserved", reserved_indices(state, active).index(move.card_index))
                    else:
                        tier = state.cards[move.card_index].tier
                        location = (tier, state.market_indices[tier].index(move.card_index))
                    actual.append(move_key(move.kind, location, move.tokens))
                self.assertEqual(set(actual), expected)
                self.assertEqual(len(actual), len(set(actual)))
                self.check_moves(source)

    def test_payment_reserved_order_and_exhausted_market(self):
        source = State()
        player = source.current_player
        player.tokens = {RUBY: 1, GOLD: 2, DIAMOND: 0}
        player.add_card(Card("discount", 1, RUBY, 0, {}))
        reserved = Card("reserved", 2, EMERALD, 2, {RUBY: 3})
        player.reserved_cards = [Card("first", 1, RUBY, 0, {}), reserved,
                                 Card("last", 1, RUBY, 0, {})]
        source.market[1] = [Card("left", 1, DIAMOND, 0, {}),
                            Card("middle", 1, SAPPHIRE, 0, {RUBY: 2}),
                            Card("right", 1, ONYX, 0, {})]
        state, moves = self.check_moves(source)
        move = next(move for move in moves if move.kind == "buy_reserved" and move.card_index == reserved_indices(state, 0)[1])
        expected_payment = tuple(-player.card_payment(reserved).get(token, 0) for token in TOKENS)
        self.assertEqual(move.tokens, expected_payment)
        move.make(state, 0)
        self.assertEqual(state.players[0].tokens, [1, 0, 0, 0, 0, 0])
        self.assertEqual(state.players[0].token_count, 1)
        move.unmake(state, 0)
        self.assertEqual(move.tokens, expected_payment)

    def test_reservations_require_spare_slot_but_not_gold(self):
        for gold, reserved_count in ((0, 0), (0, 2), (0, 3), (1, 3), (1, 2)):
            source = create_initial_state(2)
            source.supply[GOLD] = gold
            source.current_player.reserved_cards = [Card(str(index), 1, RUBY, 0, {})
                                                    for index in range(reserved_count)]
            _, moves = self.check_moves(source)
            self.assertEqual(any(move.kind == "reserve" for move in moves),
                             reserved_count < 3)

    def test_goldless_reservation_at_token_limit_transfers_no_tokens(self):
        source = create_initial_state(2)
        source.supply[GOLD] = 0
        source.current_player.tokens = {GOLD: 2, DIAMOND: 4, RUBY: 4}
        state, moves = self.check_moves(source)
        reservations = [move for move in moves if move.kind == "reserve"]
        self.assertEqual(len(reservations), 12)
        before = snapshot(state)
        move = reservations[0]
        self.assertFalse(any(move.tokens))
        tier_index = state.cards[move.card_index].tier
        replacement_index = state.deck_starts[tier_index]
        move.make(state, 0)
        self.assertEqual(state.supply, before["supply"])
        self.assertEqual([player.tokens for player in state.players], before["tokens"])
        self.assertEqual(state.players[0].token_count, 10)
        self.assertEqual(reserved_indices(state, 0), [move.card_index])
        self.assertIn(replacement_index, state.market_indices[tier_index])
        move.unmake(state, 0)
        self.assertEqual(snapshot(state), before)

    def test_noble_order_final_round_and_finished_state(self):
        for active in (0, 1):
            source = State()
            source.turn.active_player = active
            source.current_player.add_card(Card("points", 1, DIAMOND, 12, {}))
            source.market[1] = [Card("winning", 1, RUBY, 0, {})]
            source.nobles = [Noble("unqualified", 3, {ONYX: 4}),
                             Noble("first", 3, {RUBY: 1}), Noble("second", 3, {RUBY: 1})]
            state, moves = self.check_moves(source)
            before = snapshot(state)
            move = next(move for move in moves if move.kind == "buy")
            self.assertEqual(move.noble_index, 1)
            move.make(state, active)
            self.assertEqual(state.nobles[move.noble_index].owner, active)
            self.assertEqual(move.noble_index, 1)
            self.assertTrue(state.final_round)
            self.assertEqual(state.finished(1 - active), active == 1)
            if state.finished(1 - active):
                self.assertEqual(generate_moves(state, 1 - active), [])
            move.unmake(state, active)
            self.assertEqual(snapshot(state), before)

    def test_take_and_reserve_complete_overflow_in_one_move(self):
        for kind in ("take", "reserve"):
            source = create_initial_state(5)
            source.current_player.tokens = {GOLD: 2, DIAMOND: 4, RUBY: 4}
            source.current_player.add_card(Card("points", 1, RUBY, 12, {}))
            source.nobles = [Noble("qualified", 3, {RUBY: 1})]
            state, moves = self.check_moves(source)
            before = snapshot(state)
            self.assertFalse(any(move.kind == "return" for move in moves))
            move = next(move for move in moves
                        if move.kind == kind and any(amount < 0 for amount in move.tokens))
            self.assertEqual(move.noble_index, 0)
            perform_game_move(move, source, state)
            move.make(state, 0)
            self.assertEqual(snapshot(state), game_snapshot(source))
            self.assertEqual(state.players[0].token_count, 10)
            self.assertTrue(state.final_round)
            self.assertEqual(state.nobles[move.noble_index].owner, 0)
            move.unmake(state, 0)
            self.assertEqual(snapshot(state), before)

    def test_buy_moves_record_nobles_for_market_and_reserved_bonuses(self):
        source = State()
        for index in range(2):
            source.current_player.add_card(Card(str(index), 1, RUBY, 0, {}))
        source.market[1] = [Card("ruby", 1, RUBY, 0, {}),
                            Card("emerald", 1, EMERALD, 0, {}),
                            Card("onyx", 1, ONYX, 0, {})]
        source.current_player.reserved_cards = [Card("reserved", 2, RUBY, 0, {})]
        source.nobles = [Noble("first_ruby", 3, {RUBY: 3}),
                         Noble("second_ruby", 3, {RUBY: 3}),
                         Noble("emerald", 3, {EMERALD: 1})]
        state, moves = self.check_moves(source)
        for move in moves:
            if move.kind not in ("buy", "buy_reserved"):
                self.assertIsNone(move.noble_index)
            elif state.cards[move.card_index].token == TOKENS.index(RUBY):
                self.assertEqual(move.noble_index, 0)
            elif state.cards[move.card_index].token == TOKENS.index(EMERALD):
                self.assertEqual(move.noble_index, 2)
            else:
                self.assertIsNone(move.noble_index)

    def test_noble_indices_stay_stable_and_owned_nobles_are_skipped(self):
        state = SimulationState()
        ruby = TOKENS.index(RUBY)
        requirements = [0] * len(TOKENS)
        requirements[ruby] = 1
        state.nobles = [SimulationNoble(3, requirements, owner=0),
                        SimulationNoble(3, requirements, owner=1),
                        SimulationNoble(3, requirements)]
        state.cards = [SimulationCard(0, ruby, 0, [0] * len(TOKENS))]
        state.market_indices[0] = [0]
        for player in state.players:
            player.points = 3
        state.players[0].discounts[ruby] = state.players[1].discounts[ruby] = 1
        for player in state.players:
            player.card_count = 1
        nobles = state.nobles[:]
        before = snapshot(state)
        for player in (0, 1):
            move = next(move for move in generate_moves(state, player) if move.kind == "buy")
            self.assertEqual(move.noble_index, 2)
            move.make(state, player)
            self.assertEqual(state.nobles, nobles)
            self.assertEqual([noble.owner for noble in state.nobles], [0, 1, player])
            self.assertEqual(state.players[player].points, 6)
            self.assertTrue(all(move.noble_index is None for move in generate_moves(state, 1 - player)))
            move.unmake(state, player)
            self.assertEqual(state.nobles, nobles)
            self.assertEqual([noble.owner for noble in state.nobles], [0, 1, None])
            self.assertEqual(snapshot(state), before)

    def test_zero_net_take_completes_turn(self):
        source = create_initial_state(3)
        source.current_player.tokens = {GOLD: 2, DIAMOND: 4, RUBY: 4}
        state, moves = self.check_moves(source)
        zeros = [move for move in moves if move.kind == "take" and not any(move.tokens)]
        self.assertEqual(len(zeros), 1)
        before = snapshot(state)
        zeros[0].make(state, 0)
        self.assertEqual([player.tokens for player in state.players], before["tokens"])
        self.assertEqual(state.supply, before["supply"])
        zeros[0].unmake(state, 0)
        self.assertEqual(snapshot(state), before)

    def test_returning_reservation_gold_can_leave_zero_net_transfer(self):
        source = create_initial_state(3)
        source.current_player.tokens = {GOLD: 2, DIAMOND: 4, RUBY: 4}
        state, moves = self.check_moves(source)
        move = next(move for move in moves if move.kind == "reserve" and not any(move.tokens))
        before = snapshot(state)
        move.make(state, 0)
        self.assertEqual([player.tokens for player in state.players], before["tokens"])
        self.assertEqual(state.supply, before["supply"])
        self.assertEqual(len(reserved_indices(state, 0)), 1)
        move.unmake(state, 0)
        self.assertEqual(snapshot(state), before)

    def test_pairs_require_four_before_collection_even_with_returns(self):
        source = State()
        source.current_player.tokens = {DIAMOND: 4, RUBY: 4, GOLD: 2}
        source.supply = {token: 3 if token == RUBY else 0 for token in TOKENS}
        state, moves = self.check_moves(source)
        self.assertFalse(any(move.kind == "take" and move.tokens[TOKENS.index(RUBY)] == 2
                             for move in moves))
        source.supply[RUBY] = 4
        state, moves = self.check_moves(source)
        self.assertTrue(any(move.kind == "take" and move.tokens[TOKENS.index(RUBY)] == 2
                            for move in moves))

    def test_distinct_takes_match_available_supply_colors(self):
        gems = TOKENS[1:]
        for count in range(6):
            source = State()
            source.supply = {token: int(token in gems[:count]) for token in TOKENS}
            source.supply[GOLD] = 5
            _, moves = self.check_moves(source)
            takes = [move for move in moves if move.kind == "take"]
            expected = list(combinations(gems[:count], min(3, count))) if count else []
            self.assertEqual(len(takes), len(expected))
            self.assertTrue(all(sum(move.tokens) == min(3, count) for move in takes))

    def test_single_net_gem_can_result_from_triple_and_returns(self):
        source = State()
        source.current_player.tokens = {GOLD: 1, DIAMOND: 4, RUBY: 4}
        source.supply = {token: int(token in (SAPPHIRE, EMERALD, ONYX)) for token in TOKENS}
        state, moves = self.check_moves(source)
        sapphire = TOKENS.index(SAPPHIRE)
        move = next(move for move in moves if move.tokens[sapphire] == 1
                    and sum(abs(amount) for amount in move.tokens) == 1)
        before = snapshot(state)
        move.make(state, 0)
        self.assertEqual(state.players[0].token_count, 10)
        move.unmake(state, 0)
        self.assertEqual(snapshot(state), before)

    def test_scarce_collections_include_required_returns(self):
        for colors in ((SAPPHIRE,), (SAPPHIRE, EMERALD)):
            for held in (9, 10):
                source = State()
                source.current_player.tokens = {GOLD: 5, DIAMOND: 4, RUBY: held - 9}
                source.supply = {token: int(token in colors) for token in TOKENS}
                state, moves = self.check_moves(source)
                self.assertTrue(moves)
                self.assertTrue(all(move.kind == "take" for move in moves))
                self.assertTrue(all(sum(move.tokens) == min(len(colors), 10 - held) for move in moves))
                for move in moves:
                    before = snapshot(state)
                    move.make(state, 0)
                    self.assertLessEqual(state.players[0].token_count, 10)
                    move.unmake(state, 0)
                    self.assertEqual(snapshot(state), before)

    def test_final_round_and_ties_restore_arrays(self):
        for points, counts, winner in (([15, 15], [2, 2], None),
                                        ([16, 15], [3, 1], 0),
                                        ([15, 15], [3, 2], 1)):
            state = SimulationState()
            for player, count in zip(state.players, counts):
                player.points = 14
                player.card_count = count
            state.cards = [SimulationCard(0, TOKENS.index(RUBY), points[0] - 14, [0] * len(TOKENS)),
                           SimulationCard(0, TOKENS.index(EMERALD), points[1] - 14, [0] * len(TOKENS))]
            state.market_indices[0] = [0, 1]
            before = snapshot(state)
            objects = (state.players, state.players[0].tokens, state.supply, state.market_indices[0], state.cards)
            first = next(move for move in generate_moves(state, 0) if move.kind == "buy")
            first.make(state, 0)
            self.assertTrue(state.final_round)
            self.assertFalse(state.finished(1))
            second = next(move for move in generate_moves(state, 1) if move.kind == "buy")
            second.make(state, 1)
            self.assertTrue(state.finished(0))
            self.assertEqual(state.winner(0), winner)
            self.assertEqual(generate_moves(state, 0), [])
            second.unmake(state, 1)
            first.unmake(state, 0)
            self.assertEqual(snapshot(state), before)
            for original, restored in zip(objects, (state.players, state.players[0].tokens, state.supply,
                                                    state.market_indices[0], state.cards)):
                self.assertIs(original, restored)

    def test_no_moves_does_not_end_game_or_generate_pass(self):
        source = State()
        source.turn.consecutive_passes = 1
        source.supply = {token: 0 for token in TOKENS}
        state = SimulationState.from_game(source)
        self.assertNotIn("consecutive_passes", vars(state))
        before = snapshot(state)
        self.assertEqual(generate_moves(state, 0), [])
        self.assertFalse(state.finished(0))
        self.assertEqual(snapshot(state), before)

    def test_random_paths_match_game_and_unwind_exactly(self):
        for seed in range(10):
            source = create_initial_state(seed)
            state = SimulationState.from_game(source)
            before = snapshot(state)
            player = source.turn.active_player
            rng = random.Random(seed)
            history = []
            for _ in range(120):
                moves = generate_moves(state, player)
                if not moves:
                    break
                move = rng.choice(moves)
                history.append((move, player, snapshot(state), state.deck_starts[:]))
                perform_game_move(move, source, state)
                move.make(state, player)
                player = 1 - player
                self.assertEqual(snapshot(state), game_snapshot(source))
                self.assertEqual(state.finished(player), source.turn.finished)
                self.assertEqual(state.winner(player), source.turn.winner)
            for move, player, previous, cursors in reversed(history):
                move.unmake(state, player)
                self.assertEqual(snapshot(state), previous)
                self.assertEqual(state.deck_starts, cursors)
            self.assertEqual(snapshot(state), before)

    def test_conversion_owns_arrays_and_definitions(self):
        source = create_initial_state(8)
        source.players[1].nobles = [Noble("owned", 3, {RUBY: 1})]
        state = SimulationState.from_game(source)
        before = snapshot(state)
        source.supply[GOLD] = 0
        source.players[0].tokens[RUBY] = 3
        source.market[1][0].cost[RUBY] = 99
        source.market[1].clear()
        source.players[1].nobles[0].points = 99
        self.assertEqual(snapshot(state), before)
        self.assertIsInstance(state.cards[0].cost, tuple)
        owned = [noble for noble in state.nobles if noble.owner == 1]
        self.assertEqual(len(owned), 1)
        self.assertEqual(owned[0].points, 3)

    def test_conversion_of_finished_game_derives_result(self):
        source = State()
        source.turn.active_player = 1
        source.current_player.add_card(Card("winning", 1, RUBY, 15, {}))
        source.finish_turn(passed=False)
        state = SimulationState.from_game(source)
        self.assertEqual(snapshot(state), game_snapshot(source))
        self.assertTrue(state.finished(0))
        self.assertEqual(state.winner(0), 1)
        self.assertEqual(generate_moves(state, 0), [])

    def test_native_state_and_definitions_need_no_game_objects(self):
        state = SimulationState()
        ruby = TOKENS.index(RUBY)
        emerald = TOKENS.index(EMERALD)
        state.players[0].tokens[ruby] = 1
        state.players[0].token_count = 1
        cost = [0] * len(TOKENS)
        cost[ruby] = 1
        card = SimulationCard(0, emerald, 2, cost)
        requirements = [0] * len(TOKENS)
        requirements[emerald] = 1
        state.nobles = [SimulationNoble(3, requirements)]
        state.cards = [card]
        state.market_indices[0] = [0]
        before = snapshot(state)
        move = next(move for move in generate_moves(state, 0) if move.kind == "buy")
        move.make(state, 0)
        self.assertEqual(state.players[0].points, 5)
        self.assertEqual(state.players[0].discounts[emerald], 1)
        self.assertEqual(state.players[0].card_count, 1)
        move.unmake(state, 0)
        self.assertEqual(snapshot(state), before)

    def test_explicit_player_controls_generation_and_execution(self):
        state = SimulationState()
        ruby = TOKENS.index(RUBY)
        emerald = TOKENS.index(EMERALD)
        state.players[1].tokens[ruby] = 1
        state.players[1].token_count = 1
        cost = [0] * len(TOKENS)
        cost[ruby] = 1
        state.cards = [SimulationCard(0, emerald, 2, cost)]
        state.market_indices[0] = [0]
        before = snapshot(state)
        self.assertFalse(any(move.kind == "buy" for move in generate_moves(state, 0)))
        move = next(move for move in generate_moves(state, 1) if move.kind == "buy")
        move.make(state, 1)
        self.assertEqual([player.points for player in state.players], [0, 2])
        self.assertEqual([player.token_count for player in state.players], [0, 0])
        self.assertEqual(state.players[1].discounts[emerald], 1)
        move.unmake(state, 1)
        self.assertEqual(snapshot(state), before)
        self.assertNotIn("active_player", vars(state))

    def test_card_indices_survive_reservation_purchase_and_deck_exhaustion(self):
        state = SimulationState()
        state.cards = [SimulationCard(0, TOKENS.index(token), 0, [0] * len(TOKENS))
                       for token in (RUBY, EMERALD, ONYX)]
        state.market_indices[0] = [0, 1]
        state.deck_starts[0] = 2
        state.deck_ends[0] = 3
        before = snapshot(state)
        cards = state.cards[:]
        reserve = next(move for move in generate_moves(state, 0)
                       if move.kind == "reserve" and move.card_index == 0)
        reserve.make(state, 0)
        self.assertCountEqual(state.market_indices[0], [2, 1])
        self.assertEqual(state.deck_starts[0], 3)
        self.assertEqual(state.cards[0].owner, 0)
        self.assertFalse(state.cards[0].purchased)
        buy_market = next(move for move in generate_moves(state, 1)
                          if move.kind == "buy" and move.card_index == 1)
        buy_market.make(state, 1)
        self.assertEqual(state.market_indices[0], [2])
        self.assertEqual(state.deck_starts[0], 4)
        buy_reserved = next(move for move in generate_moves(state, 0)
                            if move.kind == "buy_reserved" and move.card_index == 0)
        buy_reserved.make(state, 0)
        self.assertTrue(state.cards[0].purchased)
        self.assertEqual(state.cards[0].owner, 0)
        self.assertEqual(state.market_indices[0], [2])
        self.assertEqual(state.deck_starts[0], 4)
        self.assertFalse(any(move.card_index == 0 for move in generate_moves(state, 0)))
        buy_last = next(move for move in generate_moves(state, 1)
                        if move.kind == "buy" and move.card_index == 2)
        buy_last.make(state, 1)
        self.assertEqual(state.market_indices[0], [])
        self.assertEqual(state.deck_starts[0], 5)
        buy_last.unmake(state, 1)
        self.assertEqual(state.market_indices[0], [2])
        self.assertEqual(state.deck_starts[0], 4)
        buy_reserved.unmake(state, 0)
        self.assertFalse(state.cards[0].purchased)
        self.assertEqual(state.cards[0].owner, 0)
        buy_market.unmake(state, 1)
        self.assertCountEqual(state.market_indices[0], [2, 1])
        reserve.unmake(state, 0)
        self.assertCountEqual(state.market_indices[0], [0, 1])
        self.assertEqual(state.deck_starts[0], 2)
        self.assertEqual(state.cards, cards)
        self.assertTrue(all(card.owner is None and not card.purchased for card in state.cards))
        self.assertEqual(snapshot(state), before)

    def test_simulation_imports_game_only_through_constants(self):
        directory = Path(__file__).resolve().parents[1] / "simulation"
        for path in directory.glob("*.py"):
            for node in ast.walk(ast.parse(path.read_text())):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("game"):
                    self.assertEqual(node.module, "game.constants")
                    self.assertEqual(path.name, "constants.py")
                elif isinstance(node, ast.Import):
                    self.assertFalse(any(alias.name == "game" or alias.name.startswith("game.")
                                         for alias in node.names))
