"""Card and noble definitions."""

import random

from .constants import DIAMOND, SAPPHIRE, EMERALD, RUBY, ONYX
from .card import Card
from .noble import Noble
from .state import State


def create_initial_state(seed=None):
    """Shuffle and deal a new game; an optional seed makes the deal repeatable."""
    state = State()
    rng = random.Random(seed)
    for tier, deck in enumerate(create_decks(), 1):
        rng.shuffle(deck)
        state.market[tier] = deck[:4]
        state.decks[tier] = deck[4:]
    nobles = create_nobles()
    rng.shuffle(nobles)
    state.nobles = nobles[:len(state.players) + 1]
    state.log.append("New game. Decks shuffled and four cards dealt per level.")
    return state


def create_nobles():
    """Return fresh nobles."""
    return [
        Noble("noble_diamond_1", 3, {DIAMOND: 4, ONYX: 4}),
        Noble("noble_diamond_2", 3, {DIAMOND: 4, RUBY: 4}),
        Noble("noble_sapphire_3", 3, {DIAMOND: 4, SAPPHIRE: 4}),
        Noble("noble_sapphire_4", 3, {SAPPHIRE: 4, RUBY: 4}),
        Noble("noble_emerald_5", 3, {EMERALD: 4, RUBY: 4}),
        Noble("noble_emerald_6", 3, {SAPPHIRE: 3, EMERALD: 3, ONYX: 3}),
        Noble("noble_ruby_7", 3, {DIAMOND: 3, SAPPHIRE: 3, ONYX: 3}),
        Noble("noble_ruby_8", 3, {DIAMOND: 3, EMERALD: 3, RUBY: 3}),
        Noble("noble_onyx_9", 3, {EMERALD: 3, RUBY: 3, ONYX: 3}),
        Noble("noble_onyx_10", 3, {DIAMOND: 3, SAPPHIRE: 3, EMERALD: 3}),
    ]


def create_decks():
    """Return fresh level 1, 2, and 3 decks at indices 0, 1, and 2."""
    return [
        [  # Level 1
            Card("card_001_l1_onyx_d1s1e1r1", 1, ONYX, 0, {SAPPHIRE: 1, EMERALD: 1, RUBY: 1, DIAMOND: 1}),
            Card("card_002_l1_onyx_d1s2e1r1", 1, ONYX, 0, {SAPPHIRE: 2, EMERALD: 1, RUBY: 1, DIAMOND: 1}),
            Card("card_003_l1_onyx_d2s2r1", 1, ONYX, 0, {SAPPHIRE: 2, RUBY: 1, DIAMOND: 2}),
            Card("card_004_l1_onyx_e1r3o1", 1, ONYX, 0, {ONYX: 1, EMERALD: 1, RUBY: 3}),
            Card("card_005_l1_onyx_e2r1", 1, ONYX, 0, {EMERALD: 2, RUBY: 1}),
            Card("card_006_l1_onyx_d2e2", 1, ONYX, 0, {EMERALD: 2, DIAMOND: 2}),
            Card("card_007_l1_onyx_e3", 1, ONYX, 0, {EMERALD: 3}),
            Card("card_008_l1_onyx_s4", 1, ONYX, 1, {SAPPHIRE: 4}),
            Card("card_009_l1_sapphire_d1e1r1o1", 1, SAPPHIRE, 0, {ONYX: 1, EMERALD: 1, RUBY: 1, DIAMOND: 1}),
            Card("card_010_l1_sapphire_d1e1r2o1", 1, SAPPHIRE, 0, {ONYX: 1, EMERALD: 1, RUBY: 2, DIAMOND: 1}),
            Card("card_011_l1_sapphire_d1e2r2", 1, SAPPHIRE, 0, {EMERALD: 2, RUBY: 2, DIAMOND: 1}),
            Card("card_012_l1_sapphire_s1e3r1", 1, SAPPHIRE, 0, {SAPPHIRE: 1, EMERALD: 3, RUBY: 1}),
            Card("card_013_l1_sapphire_d1o2", 1, SAPPHIRE, 0, {ONYX: 2, DIAMOND: 1}),
            Card("card_014_l1_sapphire_e2o2", 1, SAPPHIRE, 0, {ONYX: 2, EMERALD: 2}),
            Card("card_015_l1_sapphire_o3", 1, SAPPHIRE, 0, {ONYX: 3}),
            Card("card_016_l1_sapphire_r4", 1, SAPPHIRE, 1, {RUBY: 4}),
            Card("card_017_l1_diamond_s1e1r1o1", 1, DIAMOND, 0, {ONYX: 1, SAPPHIRE: 1, EMERALD: 1, RUBY: 1}),
            Card("card_018_l1_diamond_s1e2r1o1", 1, DIAMOND, 0, {ONYX: 1, SAPPHIRE: 1, EMERALD: 2, RUBY: 1}),
            Card("card_019_l1_diamond_s2e2o1", 1, DIAMOND, 0, {ONYX: 1, SAPPHIRE: 2, EMERALD: 2}),
            Card("card_020_l1_diamond_d3s1o1", 1, DIAMOND, 0, {ONYX: 1, SAPPHIRE: 1, DIAMOND: 3}),
            Card("card_021_l1_diamond_r2o1", 1, DIAMOND, 0, {ONYX: 1, RUBY: 2}),
            Card("card_022_l1_diamond_s2o2", 1, DIAMOND, 0, {ONYX: 2, SAPPHIRE: 2}),
            Card("card_023_l1_diamond_s3", 1, DIAMOND, 0, {SAPPHIRE: 3}),
            Card("card_024_l1_diamond_e4", 1, DIAMOND, 1, {EMERALD: 4}),
            Card("card_025_l1_emerald_d1s1r1o1", 1, EMERALD, 0, {ONYX: 1, SAPPHIRE: 1, RUBY: 1, DIAMOND: 1}),
            Card("card_026_l1_emerald_d1s1r1o2", 1, EMERALD, 0, {ONYX: 2, SAPPHIRE: 1, RUBY: 1, DIAMOND: 1}),
            Card("card_027_l1_emerald_s1r2o2", 1, EMERALD, 0, {ONYX: 2, SAPPHIRE: 1, RUBY: 2}),
            Card("card_028_l1_emerald_d1s3e1", 1, EMERALD, 0, {SAPPHIRE: 3, EMERALD: 1, DIAMOND: 1}),
            Card("card_029_l1_emerald_d2s1", 1, EMERALD, 0, {SAPPHIRE: 1, DIAMOND: 2}),
            Card("card_030_l1_emerald_s2r2", 1, EMERALD, 0, {SAPPHIRE: 2, RUBY: 2}),
            Card("card_031_l1_emerald_r3", 1, EMERALD, 0, {RUBY: 3}),
            Card("card_032_l1_emerald_o4", 1, EMERALD, 1, {ONYX: 4}),
            Card("card_033_l1_ruby_d1s1e1o1", 1, RUBY, 0, {ONYX: 1, SAPPHIRE: 1, EMERALD: 1, DIAMOND: 1}),
            Card("card_034_l1_ruby_d2s1e1o1", 1, RUBY, 0, {ONYX: 1, SAPPHIRE: 1, EMERALD: 1, DIAMOND: 2}),
            Card("card_035_l1_ruby_d2e1o2", 1, RUBY, 0, {ONYX: 2, EMERALD: 1, DIAMOND: 2}),
            Card("card_036_l1_ruby_d1r1o3", 1, RUBY, 0, {ONYX: 3, RUBY: 1, DIAMOND: 1}),
            Card("card_037_l1_ruby_s2e1", 1, RUBY, 0, {SAPPHIRE: 2, EMERALD: 1}),
            Card("card_038_l1_ruby_d2r2", 1, RUBY, 0, {RUBY: 2, DIAMOND: 2}),
            Card("card_039_l1_ruby_d3", 1, RUBY, 0, {DIAMOND: 3}),
            Card("card_040_l1_ruby_d4", 1, RUBY, 1, {DIAMOND: 4}),
        ],
        [  # Level 2
            Card("card_041_l2_onyx_d3s2e2", 2, ONYX, 1, {SAPPHIRE: 2, EMERALD: 2, DIAMOND: 3}),
            Card("card_042_l2_onyx_d3e3o2", 2, ONYX, 1, {ONYX: 2, EMERALD: 3, DIAMOND: 3}),
            Card("card_043_l2_onyx_s1e4r2", 2, ONYX, 2, {SAPPHIRE: 1, EMERALD: 4, RUBY: 2}),
            Card("card_044_l2_onyx_e5r3", 2, ONYX, 2, {EMERALD: 5, RUBY: 3}),
            Card("card_045_l2_onyx_d5", 2, ONYX, 2, {DIAMOND: 5}),
            Card("card_046_l2_onyx_o6", 2, ONYX, 3, {ONYX: 6}),
            Card("card_047_l2_sapphire_s2e2r3", 2, SAPPHIRE, 1, {SAPPHIRE: 2, EMERALD: 2, RUBY: 3}),
            Card("card_048_l2_sapphire_s2e3o3", 2, SAPPHIRE, 1, {ONYX: 3, SAPPHIRE: 2, EMERALD: 3}),
            Card("card_049_l2_sapphire_d5s3", 2, SAPPHIRE, 2, {SAPPHIRE: 3, DIAMOND: 5}),
            Card("card_050_l2_sapphire_d2r1o4", 2, SAPPHIRE, 2, {ONYX: 4, RUBY: 1, DIAMOND: 2}),
            Card("card_051_l2_sapphire_s5", 2, SAPPHIRE, 2, {SAPPHIRE: 5}),
            Card("card_052_l2_sapphire_s6", 2, SAPPHIRE, 3, {SAPPHIRE: 6}),
            Card("card_053_l2_diamond_e3r2o2", 2, DIAMOND, 1, {ONYX: 2, EMERALD: 3, RUBY: 2}),
            Card("card_054_l2_diamond_d2s3r3", 2, DIAMOND, 1, {SAPPHIRE: 3, RUBY: 3, DIAMOND: 2}),
            Card("card_055_l2_diamond_e1r4o2", 2, DIAMOND, 2, {ONYX: 2, EMERALD: 1, RUBY: 4}),
            Card("card_056_l2_diamond_r5o3", 2, DIAMOND, 2, {ONYX: 3, RUBY: 5}),
            Card("card_057_l2_diamond_r5", 2, DIAMOND, 2, {RUBY: 5}),
            Card("card_058_l2_diamond_d6", 2, DIAMOND, 3, {DIAMOND: 6}),
            Card("card_059_l2_emerald_d3e2r3", 2, EMERALD, 1, {EMERALD: 2, RUBY: 3, DIAMOND: 3}),
            Card("card_060_l2_emerald_d2s3o2", 2, EMERALD, 1, {ONYX: 2, SAPPHIRE: 3, DIAMOND: 2}),
            Card("card_061_l2_emerald_d4s2o1", 2, EMERALD, 2, {ONYX: 1, SAPPHIRE: 2, DIAMOND: 4}),
            Card("card_062_l2_emerald_s5e3", 2, EMERALD, 2, {SAPPHIRE: 5, EMERALD: 3}),
            Card("card_063_l2_emerald_e5", 2, EMERALD, 2, {EMERALD: 5}),
            Card("card_064_l2_emerald_e6", 2, EMERALD, 3, {EMERALD: 6}),
            Card("card_065_l2_ruby_d2r2o3", 2, RUBY, 1, {ONYX: 3, RUBY: 2, DIAMOND: 2}),
            Card("card_066_l2_ruby_s3r2o3", 2, RUBY, 1, {ONYX: 3, SAPPHIRE: 3, RUBY: 2}),
            Card("card_067_l2_ruby_d1s4e2", 2, RUBY, 2, {SAPPHIRE: 4, EMERALD: 2, DIAMOND: 1}),
            Card("card_068_l2_ruby_d3o5", 2, RUBY, 2, {ONYX: 5, DIAMOND: 3}),
            Card("card_069_l2_ruby_o5", 2, RUBY, 2, {ONYX: 5}),
            Card("card_070_l2_ruby_r6", 2, RUBY, 3, {RUBY: 6}),
        ],
        [  # Level 3
            Card("card_071_l3_onyx_d3s3e5r3", 3, ONYX, 3, {SAPPHIRE: 3, EMERALD: 5, RUBY: 3, DIAMOND: 3}),
            Card("card_072_l3_onyx_r7", 3, ONYX, 4, {RUBY: 7}),
            Card("card_073_l3_onyx_e3r6o3", 3, ONYX, 4, {ONYX: 3, EMERALD: 3, RUBY: 6}),
            Card("card_074_l3_onyx_r7o3", 3, ONYX, 5, {ONYX: 3, RUBY: 7}),
            Card("card_075_l3_sapphire_d3e3r3o5", 3, SAPPHIRE, 3, {ONYX: 5, EMERALD: 3, RUBY: 3, DIAMOND: 3}),
            Card("card_076_l3_sapphire_d7", 3, SAPPHIRE, 4, {DIAMOND: 7}),
            Card("card_077_l3_sapphire_d6s3o3", 3, SAPPHIRE, 4, {ONYX: 3, SAPPHIRE: 3, DIAMOND: 6}),
            Card("card_078_l3_sapphire_d7s3", 3, SAPPHIRE, 5, {SAPPHIRE: 3, DIAMOND: 7}),
            Card("card_079_l3_diamond_s3e3r5o3", 3, DIAMOND, 3, {ONYX: 3, SAPPHIRE: 3, EMERALD: 3, RUBY: 5}),
            Card("card_080_l3_diamond_o7", 3, DIAMOND, 4, {ONYX: 7}),
            Card("card_081_l3_diamond_d3r3o6", 3, DIAMOND, 4, {ONYX: 6, RUBY: 3, DIAMOND: 3}),
            Card("card_082_l3_diamond_d3o7", 3, DIAMOND, 5, {ONYX: 7, DIAMOND: 3}),
            Card("card_083_l3_emerald_d5s3r3o3", 3, EMERALD, 3, {ONYX: 3, SAPPHIRE: 3, RUBY: 3, DIAMOND: 5}),
            Card("card_084_l3_emerald_s7", 3, EMERALD, 4, {SAPPHIRE: 7}),
            Card("card_085_l3_emerald_d3s6e3", 3, EMERALD, 4, {SAPPHIRE: 6, EMERALD: 3, DIAMOND: 3}),
            Card("card_086_l3_emerald_s7e3", 3, EMERALD, 5, {SAPPHIRE: 7, EMERALD: 3}),
            Card("card_087_l3_ruby_d3s5e3o3", 3, RUBY, 3, {ONYX: 3, SAPPHIRE: 5, EMERALD: 3, DIAMOND: 3}),
            Card("card_088_l3_ruby_e7", 3, RUBY, 4, {EMERALD: 7}),
            Card("card_089_l3_ruby_s3e6r3", 3, RUBY, 4, {SAPPHIRE: 3, EMERALD: 6, RUBY: 3}),
            Card("card_090_l3_ruby_e7r3", 3, RUBY, 5, {EMERALD: 7, RUBY: 3}),
        ],
    ]
