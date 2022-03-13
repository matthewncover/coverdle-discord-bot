# coverdle-discord-bot

Discord bot that captures scores from [Wordle](https://www.nytimes.com/games/wordle/index.html), [Worldle](https://worldle.teuteuf.fr/), [Nerdle](https://nerdlegame.com/), and [Quordle](https://www.quordle.com/#/) posts and presents statistics.
<br>

### Commands

Command format:<br>
        $420 (game option) (stat option) (date option)<br><br>
        game options:<br>
            all_games, wordle, worldle, nerdle, quordle<br><br>
        stat options:<br>
            all_stats, user_performance, game_popularity,<br>
            team_performance, stoke_meter<br><br>
        date options:<br>
            all_time, abbreviated month-year (ex. Feb22)<br>
### Examples

`$420 worldle stoke_meter Mar22`<br>
```
        Worldle: stoke meter (March 2022)
        
        ===Stoke Meter===
        
┌─────────┬─────────────┐
│  Name   │ Stoke Level │
├─────────┼─────────────┤
│ Matthew │    129 %    │
│  Chase  │    129 %    │
│   Ash   │    129 %    │
│ Miranda │    116 %    │
│  Delli  │    77 %     │
│  Nakul  │    51 %     │
│  Josh   │    25 %     │
└─────────┴─────────────┘
```

`$420 wordle team_performance all_time`<br>
```
        Wordle: team performance (all time)
        
        ===Team Performance===
        
┌───────┬──────────────────────────┐
│ score │ frequency                │
├───────┼──────────────────────────┤
│ 1     │                     0 %  │
│ 2     │ ==                  5 %  │
│ 3     │ ==============      29 % │
│ 4     │ =================   34 % │
│ 5     │ ========            17 % │
│ 6     │ ====                8 %  │
│ X     │ =                   3 %  │
└───────┴──────────────────────────┘
        
Team win rate: 96.43 %
        
```