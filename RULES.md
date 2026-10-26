# Simplified Splendor rules

This document defines the intended first playable version: one human against
one computer opponent.

## Setup

- The human plays first. Players alternate turns.
- Each player starts with no gems, no cards, and zero points.
- The bank starts with four gems of each color: Diamond, Sapphire, Emerald,
  Ruby, and Onyx. It also holds five Gold tokens. Gold can be selected, but
  gold alone cannot be taken. Select a market card and then gold to reserve it.
- Shuffle each of the three development decks separately and reveal four
  cards per level. Remaining cards stay face down.
- Shuffle the ten nobles and reveal three, displayed left of the supply.

## Taking a turn

Choose one action:

1. **Take gems:** take one, two, or three different colors from the bank,
   one gem per color. Each selected color must be available. Taking fewer
   than three is allowed even when more colors are available. You cannot
   take gems that would bring your inventory above 10. You cannot return
   or exchange gems to make room; gems leave your inventory only when spent
   on a card.
2. **Buy a card:** purchase one face-up market card you can afford.
3. **Reserve a card:** select a face-up market card, then gold, and confirm
   Reserve. Move the card to your reserved cards and take one gold from the
   bank. You may hold at most three reserved cards, and taking the gold must
   not exceed the 10-token inventory limit. Refill the market slot from its
   deck if possible. Reserved cards grant no points or discounts.
4. **Pass:** take no action and give the turn to the opponent.

A player cannot take gems and buy a card on the same turn.

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
deck leaves fewer cards available.

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

The computer follows the same rules, with no extra resources or access to
hidden deck order. Greedy AI is the default: it buys the highest-point
affordable card, otherwise collects gems toward visible cards, and passes
when no purchase or useful collection is possible. Manual control and
Pass-only AI are also available. See [README.md](README.md) for exact
strategy priorities and control options.

## Rules omitted or changed from full Splendor

- **Nobles:** when several qualify, the first in displayed order is awarded
  automatically rather than letting the player choose.
- **Reservations and gold:** reservations require taking one available gold
  without exceeding the token limit. Blind reservations and purchasing reserved
  cards are not implemented yet.
- **Two matching gems:** omitted for now; the full game permits this only
  when at least four gems of that color are available before taking them.
- **Player count:** only two players; no three- or four-player setup.
- **Gem collection:** this version freely permits taking fewer than three
  different colors; the referenced full rules require three when available.
- **Gem limit and returns:** the full game allows taking gems above the
  10-gem limit during a turn, then returning gems of your choice until you
  hold 10. This can change the mix of gems you hold. Here, taking gems must
  never exceed 10, and returning or exchanging gems is not allowed. At 10
  gems, you must buy a card or pass.
- **Passing:** voluntary passes and the two-pass ending are house rules.
- **First player:** the human always starts instead of choosing by age.

The comparison is with base Splendor, not Splendor Duel or expansions.
Reference: [publisher rulebook](https://cdn.svc.asmodee.net/production-asmodeeca/uploads/2022/01/SCSPL01EN_SPLENDOR_RULES_LIGHT.pdf).
