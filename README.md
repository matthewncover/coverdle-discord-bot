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
`$420 all_games game_popularity (all time)`
```
        All games: game popularity (all time)
        
        ===Game Popularity===
        Number of games played (% of total)
        
┌─────────┬────────────────────────┐
│ Game    │ Num Games (% of Total) │
├─────────┼────────────────────────┤
│ Wordle  │ 84 (33 %)              │
│ Worldle │ 75 (29 %)              │
│ Quordle │ 60 (23 %)              │
│ Nerdle  │ 33 (13 %)              │
└─────────┴────────────────────────┘
        
```
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
`$420 nerdle user_performance all_time`
```
        Nerdle: user performance (all time)
        
        ===User Performance===
        
                num games  avg. typical % struggled
name    game                                       
Ash     Nerdle          8  3.50       5         0 %
Delli   Nerdle         11  3.36       3         0 %
Matthew Nerdle          8  3.00       3         0 %
Miranda Nerdle          6  3.67       4         0 %
        
```