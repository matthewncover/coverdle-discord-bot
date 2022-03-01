import pandas as pd, numpy as np, datetime as dt

from dateutil.relativedelta import relativedelta

import warnings
warnings.simplefilter('ignore')

class Reporting:

    def __init__(self, cmd_args:list):

        try:
            self.df0 = pd.read_csv("./coverdle_data.csv")
            self.df0.day = pd.to_datetime(self.df0.day, format='%Y%m%d')
            self.df = self.df0.copy()

            self.report_msg = ''

            self.game_filter = cmd_args[0]
            self.stats_filter = cmd_args[1]
            if cmd_args[2] != 'all_time':
                self.date_filter = dt.datetime.strptime(cmd_args[2], "%b%y")
            else:
                self.date_filter = cmd_args[2]
            
            self.define_fn_dicts()

            self.compile_report()
        except:

            self.report_msg = """\n
            Something has gone wrong. One of us done goofed.\n
            Type "$420 help" for a list of commands.
            """
        
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


    def user_performance(self):

        self.df_pass = self.df[self.df.score != 'X']
        self.df_pass.score = self.df_pass.score.astype(np.float16)

        def typical(x):

            return x.value_counts().index[0]

        self.user_performance_stats = (
            self.df_pass
            .groupby(['name', 'game'])
            .agg({
                'score': ['mean', 'min', typical, 'size']
                })
                .rename(columns = {
                    'mean': 'avg.',
                    'min': 'best',
                    'size': 'count'
                    })
        ).round(2).to_string()

        self.report_msg += f"""\n
        ===User Performance===\n
        {self.user_performance_stats}
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
        ).to_string()

        self.report_msg += f"""===Stoke Meter===\n
        {self.stoke_meter_stats}
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
                .to_string(index=True)
            )

        self.report_msg += f"""\n
        ===Game Popularity===\n
        Number of games played (% of total)\n
        {self.game_popularity_stats}
        """

    def team_performance(self):

        self.df_pass = self.df[self.df.score != 'X']
        self.df_pass.score = self.df_pass.score.astype(np.float16)

        self.team_performance_stats = (
            self.df_pass
            .score
            .describe()
            .round(3)
            .loc[
                ["count", "mean", "std",
                 "25%", "50%", "75%"]
            ]
        ).to_string()

        self.team_accuracy = f"""
        {round(
            self.df_pass.shape[0] / self.df.shape[0] * 100, 2
        )} %
        """
        self.report_msg += f"""\n
        ===Team Performance===\n
        Num games, average score, score standard deviation, quartiles\n
        {self.team_performance_stats}\n
        Team win rate: {self.team_accuracy}
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

        self.report_msg += f"""\n
        {str.capitalize(self.game_filter)}: {self.stats_filter.replace('_', ' ')} ({date_filter_string})
        """

        self.specified_game()
        
        if self.date_filter != 'all_time':
            self.df = self.specified_month(self.df)

        self.stats_fns[self.stats_filter]()

        if self.date_filter == 'all_time':
            self.report_msg += '\nStoke meter stats not available for all time.'

        pass

    
if __name__ == '__main__':

    msg = '$420 help'

    cmd_args = msg.split(' ')[1:]
    rep = Reporting(cmd_args)

    print(rep.report_msg)