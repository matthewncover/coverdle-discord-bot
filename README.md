# coverdle-discord-bot

Discord bot that captures scores from [Wordle](https://www.nytimes.com/games/wordle/index.html), [Worldle](https://worldle.teuteuf.fr/), [Nerdle](https://nerdlegame.com/), and [Quordle](https://www.quordle.com/#/) posts and presents statistics.
<br>

#### Commands

Command format:<br>
        $420 (game option) (stat option) (date option)<br><br>
        game options:<br>
            all_games, wordle, worldle, nerdle, quordle<br><br>
        stat options:<br>
            all_stats, user_performance, game_popularity,<br>
            team_performance, stoke_meter<br><br>
        date options:<br>
            all_time, abbreviated month-year (ex. Feb22)<br>
#### Examples

`$420 worldle stoke_meter Mar22`<br>
        Worldle: stoke meter (March 2022)<br>
        ===Stoke Meter===<br>
┌─────────┬─────────────┐<br>
│  Name   │ Stoke Level │<br>
├─────────┼─────────────┤<br>
│ Matthew │    129 %    │<br>
│  Chase  │    129 %    │<br>
│   Ash   │    129 %    │<br>
│ Miranda │    116 %    │<br>
│  Delli  │    77 %     │<br>
│  Nakul  │    51 %     │<br>
│  Josh   │    25 %     │<br>
└─────────┴─────────────┘<br>