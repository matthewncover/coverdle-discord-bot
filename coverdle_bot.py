import discord
from discord.ext import commands

import pandas as pd, re, json, numpy as np

import datetime as dt
from dateutil.relativedelta import relativedelta

import warnings
warnings.simplefilter('ignore')

id_dict = json.load(open("ids.json"))

class CoverdleClient(discord.Client):

    def on_command(self, msg):

        self.cmd_args = msg.content.split(' ')[1:]
        self.cmd_arg_primary = self.cmd_args[0]

        self.report_obj = Reporting(self.cmd_args)
        self.report = self.report_obj.report_msg


    def on_wordle_entry(self, msg):

        self.author = f"{msg.author.name}#{msg.author.discriminator}"

        try:
            self.author_name = id_dict['author-ids'][self.author]
        except KeyError:
            self.author_name = "Who?"
        
        self.msg_day = msg.created_at.strftime("%Y%m%d")
        self.game = self.rdle_names[self.rdle_bools.index(True)]

        self.read_coverdle_data()
        self.find_score(msg)
        self.append_data()

    def read_coverdle_data(self):

        self.df = pd.read_csv("./coverdle_data.csv")

        # self.df.date = pd.to_datetime(self.df.date)
        # self.df.time = pd.to_datetime(self.df.time)

        pass

    def which_game(self, msg):

        is_wordle = not not re.search(r'Wordle \d+ (\d{1}|X)[/]6', msg.content)
        is_worldle = not not re.search(r'#Worldle #\d+ (\d{1}|X)[/]6', msg.content)
        is_nerdle = not not re.search(r"nerdlegame \d+ \d{1}[/]6", msg.content)
        is_quordle = not not re.search(r"Daily Quordle #\d+", msg.content)

        self.rdle_bools = [is_wordle, is_worldle, is_nerdle, is_quordle]

    def find_score(self, msg):

        self.is_hard_mode = 0

        if self.game != "Quordle":

            self.score = re.search(r'(\d{1}|X)[/]6', msg.content).group()[0]
            self.score = "X" if self.score == "X" else int(self.score)
            self.quordle_scores = [np.nan]*4

            if self.game == 'Wordle':
                self.is_hard_mode = int(
                    msg.content[
                        re.search(r'(\d{1}|X)[/]6', msg.content).end():
                        ][0] == '*'
                        )
            
        else:

            quordle_message_score_contents = (
                msg.content[
                    re.search(r'Daily Quordle #\d+', msg.content).end():
                    re.search(r'quordle.com', msg.content).start()
                ]
                .replace('\n', '')
            )

            self.quordle_scores = (
                [
                    "X" if z == '\U0001f7e5' else int(z)
                    for z in [
                        x for x in list(quordle_message_score_contents)
                        if x not in ('️', '⃣')
                        ]
                ]
            )

            self.score = np.array(self.quordle_scores).mean()*(2/3) # convert to max score of 6 scale


    def append_data(self):

        if (
            self.df[
                (self.df.author == self.author)
                 & (self.df.day == int(self.msg_day))
                 & (self.df.game == self.game)
                 ].shape[0]
            ) == 0:

            self.df = self.df.append(pd.DataFrame([[
                self.author, self.author_name, self.msg_day,
                self.game, self.is_hard_mode, self.score] + self.quordle_scores
            ], columns = self.df.columns))

            self.df.to_csv("./coverdle_data.csv", index=None)

    async def on_message(self, msg):

        #####################################
        # first, checks db and updates with history

        hist = msg.channel.history()
        pass

        #####################################

        # ignore if the bot sent the message
        if msg.author == client.user:
            return None

        # ignore if message is not in wordle channel
        if msg.channel.name != 'wordle':
            return None

        # trigger command
        if msg.content.startswith("$420"):
            self.on_command(msg)

            await msg.channel.send(self.report)

        self.which_game(msg)
        self.rdle_names = ["Wordle", "Worldle", "Nerdle", "Quordle"]

        # add to 
        if max(self.rdle_bools) == 1:
            self.on_wordle_entry(msg)

        # regular chat
        else:
            return None
        

class Reporting:

    def __init__(self, cmd_args:list):

        self.df = pd.read_csv("./coverdle_data.csv")
        self.df.day = pd.to_datetime(self.df.day)

        self.report_msg = ''

        self.game_filter = cmd_args[0]
        self.stats_filter = cmd_args[1]
        if cmd_args[2] != 'all_time':
            self.date_filter = dt.datetime.strptime(cmd_args[2], "%b%y")
        else:
            self.date_filter = cmd_args[2]
        
        self.define_fn_dicts()

        self.compile_report()
        
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
        # self.date_filter_fns = {
        #     "all_time": self.unspecified_date,
        #     self.date_filter: self.specified_month
        # }

        pass



    def specified_game(self):

        games = (
            self.df.game.unique().tolist()
            if self.game_filter == 'all_games'
            else [self.game_filter]
        )

        self.df = (
            self.df[
                self.df.game.str.lower().isin(games)
            ]
        )

    def specified_month(self):

        # another input: table that results from filtering/melting/whatever based on secondary arg

        # self.report_msg += f'{monthyear}\n--------\n'

        one_month_before = self.date_filter - relativedelta(months=1)

        self.df = (
            self.df[
                (self.df.day >= self.date_filter) &
                (self.df.day < one_month_before)
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
        ).to_string()

        self.report_msg += f"""\n
        ===User Performance===\n
        {self.user_performance_stats}
        """

    def stoke_meter(self):
        # (num games done) / (X days of that month)
        # possible to have 400% stoke level

        if self.date_filter == 'all_time':
            self.report_msg += """\n
            ===Stoke Meter===\n
            Stoke meter stats not available for 'all_time'.
            """
            return

        self.stoke_meter_stats = (
            (
                self.df.name.value_counts() / (
                    self.date_filter + relativedelta(months=1) - relativedelta(days=1)
                ).day * 100
                )
                .astype(str)
                + ' %'
        ).to_string()

        self.report_msg += f"""\n
        ===Stoke Meter===\n
        {self.stoke_meter_stats}
        """


    def game_popularity(self):

        self.game_popularity_stats = (
            self.df.game
            .value_counts().astype(str) 
            + ' (' + (
                self.df.game.value_counts() / self.df.shape[0] * 100
                )
                .astype(int)
                .astype(str)
                 + ' %)'
        ).to_string(index=False)

        self.report_msg += f"""\n
        ===Game Popularity===\n
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

        self.report_msg += f"""\n
        ===Team Performance===\n
        {self.team_performance_stats}
        """

    def all_stats(self):

        self.game_popularity()
        self.stoke_meter()
        self.team_performance()
        self.user_performance()

    def compile_report(self):

        self.report_msg += f"""\n
        {self.game_filter}: {self.stats_filter}\n
        {self.date_filter}
        """

        self.specified_game()
        
        if self.date_filter != 'all_time':
            self.specified_month()

        self.stats_fns[self.stats_filter]()
        


client = CoverdleClient()
guild = discord.Guild
channel = client.get_channel(id_dict['channel-id'])

client.run(id_dict['bot-token'])