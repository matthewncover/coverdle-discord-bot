import pandas as pd, numpy as np, datetime as dt, math
from table2ascii import Alignment, table2ascii as t2a, PresetStyle

from dateutil.relativedelta import relativedelta

import warnings
warnings.simplefilter('ignore')

class Reporting:

    def __init__(self, cmd_args:list, df0:pd.DataFrame):

        # try:
            # self.df0 = pd.read_csv("./coverdle_data.csv")
            self.df0 = df0
            self.df0.day = pd.to_datetime(self.df0.day, format='%Y%m%d')
            self.df = self.df0.copy()

            self.report_msg = '```\n'

            self.game_filter = cmd_args[0]
            self.stats_filter = cmd_args[1]

            if cmd_args[2] != 'all_time':
                self.date_filter = dt.datetime.strptime(cmd_args[2], "%b%y")
            else:
                self.date_filter = cmd_args[2]
            
            self.define_fn_dicts()

            self.compile_report()
        # except:

        #     self.report_msg = """\n
        #     Something has gone wrong. One of us done goofed.
        #     Type "$420 help" for a list of commands.
        #     """
        
    def define_fn_dicts(self):

        # self.game_filter_fn_dict = {
        #     "all_games": 
        # }

        self.stats_fns = {
            "all_stats": self.all_stats,
            "user_performance": self.user_performance,
            "game_popularity": self.game_popularity,
            "team_performance": self.team_performance,
            "stoke_meter": self.stoke_meter
        }


    def specified_game(self):

        self.games = (
            self.df.game.unique().tolist()
            if self.game_filter == 'all_games'
            else [str.capitalize(self.game_filter)]
        )

        self.df = (
            self.df[
                self.df.game.isin(self.games)
            ]
    )

    def specified_month(self, df):

        # another input: table that results from filtering/melting/whatever based on secondary arg

        # self.report_msg += f'{monthyear}\n--------\n'

        one_month_ahead = self.date_filter + relativedelta(months=1)

        return (
            df[
                (df.day >= self.date_filter) &
                (df.day < one_month_ahead)
            ]
            )


    def no_data(self, df):

        if df.shape[0] == 0:
            self.report_msg += """
            Sheeeit. No data.
            """
            return True
        else:
            return False

    def stats_t2a(self, df, colnames):

        df = df.reset_index()
        df.columns = colnames

        return t2a(
            header = df.columns.tolist(),
            body = df.values.tolist(),
            style = PresetStyle.thin_compact,
            alignments = [Alignment.LEFT]*len(df.columns),
            first_col_heading = True
        )

    def stats_t2a_tp(self, df, colnames):

        df = df.reset_index()
        df.columns = colnames

        return t2a(
            header = df.colnames.tolist(),
            body = df.values.tolist(),
            style = PresetStyle.thin_compact,
            alignments = [Alignment.RIGHT, Alignment.LEFT, Alignment.RIGHT]
        )

    def user_performance(self):

        self.df_pass = self.df[self.df.score != 'X']
        self.df_pass.score = self.df_pass.score.astype(np.float16)

        def pass_mean(x):

            return round(x[ x!= "X"].astype(float).mean(), 2)
        
        def typical(x):

            typ = x.value_counts().index[0]
            if type(typ) != str:
                typ = round(typ, 2)
            
            return typ

        def bed_shatting(x):

            return x[x == "X"].shape[0]

        self.user_performance_stats = (
            self.df
            .groupby(['name', 'game'])
            .agg({
                'score': [pass_mean, typical, 'size', bed_shatting]
            })
            .assign(
                percent_struggled = lambda x: (x[("score", "bed_shatting")] / x[("score", "size")])*100
            )
            .rename(columns = {
                'pass_mean': 'avg.',
                'size': 'num games',
                'bed_shatting': '% struggled'
            })
        )

        self.user_performance_stats[("score", "% struggled")] = self.user_performance_stats.percent_struggled.astype(int).astype(str) + " %"

        # self.user_performance_stats.drop(["percent_struggled"], axis=1, inplace=True)
        
        self.user_performance_stats = self.user_performance_stats[[("score", "num games"), ("score", "avg."), ("score", "typical"), ("score", "% struggled")]]
        self.user_performance_stats.columns = ["num games", "avg.", "typical", "% struggled"]

        if self.no_data(self.user_performance_stats):
            return

        self.report_msg += f"""
        ===User Performance===
        \n{self.user_performance_stats.to_string()}
        """

    def stoke_meter(self):
        # (num games done) / (X days of that month)
        # possible to have 400% stoke level

        if self.date_filter == 'all_time':
            return

        self.stoke_meter_stats = (
            (
                self.df.name.value_counts() / (
                    self.date_filter + relativedelta(months=1) - relativedelta(days=1)
                ).day * 100 * (4 / len(self.games))
                )
                .astype(int)
                .astype(str)
                + ' %'
        )
        
        if self.no_data(self.stoke_meter_stats):
            return

        self.report_msg += f"""
        ===Stoke Meter===
        \n{self.stats_t2a(self.stoke_meter_stats, colnames=['Name', 'Stoke Level'])}
        """


    def game_popularity(self):

        if self.date_filter == 'all_time':
            df_all_games = self.df0.copy()
        else:
            one_month_ahead = self.date_filter + relativedelta(months=1)

            df_all_games = (
                self.df0[
                    (self.df0.day >= self.date_filter) &
                    (self.df0.day < one_month_ahead)
                ]
            )

        self.game_popularity_stats = (
            (
                self.df.game
                .value_counts().astype(str) 
                + ' (' + (
                    df_all_games.game.value_counts() / df_all_games.shape[0] * 100
                    )
                    .astype(int)
                    .astype(str)
                    + ' %)'
                    )
                .dropna()
            )

        if self.no_data(self.game_popularity_stats):
            return

        self.report_msg += f"""
        ===Game Popularity===
        Number of games played (% of total)
        \n{self.stats_t2a(self.game_popularity_stats, colnames=['Game', 'Num Games (% of Total)'])}
        """

    def team_performance(self):

        self.df_pass = self.df[self.df.score != 'X']
        self.df_pass.score = self.df_pass.score.astype(np.float16)

        # self.team_performance_stats = (
        #     self.df_pass
        #     .score
        #     .describe()
        #     .round(3)
        #     .loc[
        #         ["count", "mean", "std",
        #          "min", "25%", "50%", "75%"]
        #     ]
        # )

        if self.game_filter == "quordle":

            score_array = pd.Series(
                self.df
                [[x for x in self.df.columns if x.startswith("quordle_")]]
                .values.ravel()
                ).dropna()
        else:
            score_array = self.df.score

        self.team_performance_stats = (
            pd.Series(
                ["X" if x == "X" else str(int(float(x))) for x in score_array]
            )
            .value_counts()
            .reset_index()
            .rename(columns={
                'index': "score",
                0: "count"
            })
            .sort_values(by="score")
            # .assign(
            #     frequency=lambda x: (x['count']/score_array.shape[0])*100,
            #     )
            .reset_index(drop=True)
        )

        self.team_performance_stats = self.team_performance_stats.append(
            pd.DataFrame(
                [[str(x), 0] for x in np.arange(1,7)
                 if str(x) not in score_array.unique().tolist()],
                 columns = self.team_performance_stats.columns)
        ).reset_index(drop=True)

        self.team_performance_stats["frequency"] = pd.Series([
            f"{int(x/score_array.shape[0]*100)} %" for x in self.team_performance_stats["count"]
        ])

        self.team_performance_stats['bar'] = pd.Series([
            "="*int(x/score_array.shape[0]*100) for x in self.team_performance_stats["count"]
        ])

        self.team_performance_stats = (
            self.team_performance_stats
            .sort_values(by="score")
            .set_index("score")
            [["bar","frequency"]]

        )
        
        if self.no_data(self.team_performance_stats):
            return

        self.team_accuracy = f"""{round(
            self.df_pass.shape[0] / self.df.shape[0] * 100, 2
            )} %
        """

        self.report_msg += f"""
        ===Team Performance===
        \n{self.stats_t2a(
            self.team_performance_stats, colnames = ['score', 'frequency', ' ']
        )}
        \nTeam win rate: {self.team_accuracy}
        """

    def all_stats(self):

        self.game_popularity()
        self.stoke_meter()
        self.team_performance()
        self.user_performance()

    def compile_report(self):

        date_filter_string = (
            'all time' if self.date_filter == 'all_time'
            else self.date_filter.strftime("%B %Y")
        )

        self.report_msg += f"""
        {str.capitalize(self.game_filter).replace('_', ' ')}: {self.stats_filter.replace('_', ' ')} ({date_filter_string})
        """

        self.specified_game()
        
        if self.date_filter != 'all_time':
            self.df = self.specified_month(self.df)

        self.stats_fns[self.stats_filter]()

        if (self.date_filter == 'all_time') & (self.stats_filter in ['all_stats', 'stoke_meter']):
            self.report_msg += '\nStoke meter stats not available for all time.'

        self.report_msg += "```"

        pass

    
if __name__ == '__main__':

    msg = '$420 all_games game_popularity all_time'

    cmd_args = msg.split(' ')[1:]
    rep = Reporting(cmd_args)

    print(rep.report_msg)