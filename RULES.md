# Simplified Splendor rules

This document defines the intended first playable version: one human against
one computer opponent.

## Setup

- The human plays first. Players alternate turns.
- Each player starts with no gems, no cards, and zero points.
- The bank starts with four gems of each color: Diamond, Sapphire, Emerald,
  Ruby, and Onyx. It also holds five Gold tokens. Gold can be selected, but
  gold alone cannot be taken. Select a market card and gold, in either order,
  to reserve it.
- Shuffle each of the three development decks separately and reveal four
  cards per level. Remaining cards stay face down.
- Shuffle the ten nobles and reveal three, displayed left of the supply.

## Taking a turn

Choose one action:

1. **Take gems:** take exactly three different colors from the bank,
   one gem per color, or take exactly two gems of one color if at least four
   of that color are available before taking them. Each selected color must
   be available. Human players cannot take one gem or two different colors,
   even when fewer colors are available. The AI may take one or two different
   colors; both players in manual mode follow human rules. You may temporarily exceed 10 tokens; return the exact
   excess before ending your turn, as described below.
2. **Buy a card:** purchase one face-up market card or one of your reserved
   cards you can afford. Reserved cards cannot be reserved again.
3. **Reserve a card:** select a face-up market card and gold, and confirm
   Reserve. Move the card to your reserved cards and take one gold from the
   bank. You may hold at most three reserved cards. If taking gold brings
   your holdings above 10, return the excess before ending your turn. Refill
   the market slot from its deck if possible. Reserved cards grant no points or discounts.
4. **Pass:** click Pass with nothing selected to give the turn to
   the opponent without collecting anything. This counts toward the
   two-consecutive-pass ending described below.

A player cannot take gems and buy a card on the same turn.

After Take or Reserve, if you hold more than 10 tokens, the action button
changes to **Return**. The original action has already transferred the gems
or reserved the card, but the same player stays active. Click tokens in that
player’s panel to select returns, including any owned gold or newly collected
gems. Selected tokens appear as color piles; click a selected pile to remove
one pending return. Confirm Return only when the selected total equals the
excess, leaving exactly 10. Other actions are unavailable until Return finishes.
Only then are nobles awarded and game completion checked, before advancing
the turn. Restart remains available.

## Cards and payment

Each card has a color, a points value, and a cost by gem color. Every owned
card reduces future costs of its color by one. Discounts stack and are never
spent. For each color, pay `max(0, cost - owned cards of that color)`.

For example, a card costing three Ruby and two Sapphire costs one Ruby and
two Sapphire if you already own two Ruby cards.

Gold is a wildcard: after discounts, spend matching colored gems first, then
one gold for each missing gem of any color. Gold must cover the combined
shortfall across all colors. Return the actual colored gems and gold paid to
the bank.

Return payment to the bank and add the card to your inventory. Its points
count immediately; its discount applies to later purchases. A free card
still uses your turn. Refill the market from the matching deck; an exhausted
deck leaves fewer cards available. Buying a reserved card removes it from your
reserved list without changing the market or decks.

## Nobles

At the end of each turn, compare the active player's permanent card bonuses
with each available noble's requirements. Tokens do not count and nothing
is spent. Award the first qualifying noble in the displayed order, at most
one per turn, and remove it from the available nobles without replacement.
Owned nobles grant points but no gem discounts.

## Ending the game

Reaching at least 15 points triggers the final round. Finish that round so
both players have taken equal turns: if the human triggers it, the computer
still takes its turn; if the computer triggers it, the game ends immediately.

Highest score wins. If tied, the player with fewer purchased cards wins.
If still tied, the game is a draw.

As a simplified stalemate rule, two consecutive passes end the game using
the same scoring and tie-break rules, even below 15 points. Any purchase or
gem-taking or reservation action resets the consecutive-pass count.

## Computer opponent

The computer follows the same rules except that it may take one or two
different gem colors. It has no extra resources or access to hidden deck order. Greedy AI is the default: it buys the highest-point
affordable card, otherwise collects gems toward visible cards, and passes
when no purchase or useful collection is possible. Manual control and
Pass-only AI are also available. See [README.md](README.md) for exact
strategy priorities and control options.

## Rules omitted or changed from full Splendor

- **Nobles:** when several qualify, the first in displayed order is awarded
  automatically rather than letting the player choose.
- **Reservations and gold:** reservations require taking one available gold. Blind reservations are not implemented.
- **Player count:** only two players; no three- or four-player setup.
- **Gem collection:** human players must take exactly three different colors
  or two matching gems, even when fewer colors are available. Only the AI
  may take one or two different colors.
- **Passing:** voluntary passes and the two-pass ending are house rules.
- **First player:** the human always starts instead of choosing by age.

The comparison is with base Splendor, not Splendor Duel or expansions.
Reference: [publisher rulebook](https://cdn.svc.asmodee.net/production-asmodeeca/uploads/2022/01/SCSPL01EN_SPLENDOR_RULES_LIGHT.pdf).
