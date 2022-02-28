import discord
from discord.ext import commands

import pandas as pd, re, json, numpy as np

import datetime as dt
from dateutil.relativedelta import relativedelta

id_dict = json.load(open("ids.json"))

class CoverdleClient(discord.Client):

    # def __init__(self):

    #     # self.bot_cmd = commands.Bot(command_prefix = '$420')
    #     self.ass_eating = "all day"

    def on_command(self, msg):

        # self.bot_cmd = commands.Bot(command_prefix="$420")

        # @commands.command()
        # async def request_history(context, *args):

        #     await context.send(f'{len(args)}')

        # self.bot_cmd.add_command(request_history)
        

        self.cmd_args = msg.content.split(' ')[1:]
        self.cmd_arg_primary = self.cmd_args[0]

        self.report = Reporting(self.cmd_args)

        # if self.cmd_arg_primary == 'history':
            
            # self.report = Reporting(self.cmd_args)
            # pass

    def on_wordle_entry(self, msg):

        self.author = f"{msg.author.name}#{msg.author.discriminator}"

        try:
            self.author_name = id_dict['author-ids'][self.author]
        except:
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

        for m in msg.channel.history():
            print(m)

        #####################################

        if msg.author == client.user:
            return None

        if msg.channel.name != 'wordle':
            return None

        if msg.content.startswith("$420"):
            self.on_command(msg)

        self.which_game(msg)
        self.rdle_names = ["Wordle", "Worldle", "Nerdle", "Quordle"]

        if max(self.rdle_bools) == 1:
            self.on_wordle_entry(msg)

        # regular chat
        else:
            return None
        
        

class Reporting:

    def __init__(self, cmd_args:list):

        self.df = CoverdleClient.read_coverdle_data()
        self.df.date = pd.to_datetime(self.df.date)

        self.report_msg = ''

        self.game_filter = cmd_args[0]
        self.stats_filter = cmd_args[1]
        self.date_filter = dt.datetime.strptime(cmd_args[2], "%b%y")
        self.define_fn_dicts()
        
    def define_fn_dicts(self):

        # self.game_filter_fn_dict = {
        #     "all_games": 
        # }

        self.stats_fn_dict = {
            "all_stats": self.all_stats,
            "user_performance": self.user_performance,
            "game_popularity": self.game_popularity,
            "team_performance": self.team_performance,
        }
        self.date_filter_fn_dict = {
            "all_time": self.unspecified_date,
            self.date_filter: self.specified_month
        }


    def specified_game(self):

        games = (
            self.df.game.unique().tolist()
            if self.game_filter == 'all_games'
            else [self.game_filter]
        )

        self.df = (
            self.df[
                self.df.game.isin(games)
            ]
        )

    def specified_month(self):

        # another input: table that results from filtering/melting/whatever based on secondary arg

        # self.report_msg += f'{monthyear}\n--------\n'

        one_month_before = self.date_filter - relativedelta(months=1)

        self.df = (
            self.df[
                (self.df.date >= self.date_filter) &
                (self.df.date < one_month_before)
            ]
        )

    def unspecified_date(self):

        pass

    def user_performance(self):

        pass

    def game_popularity(self):

        pass

    def team_performance(self):

        pass

    def all_stats(self):

        pass

    def compile_report(self):

        pass


client = CoverdleClient()
guild = discord.Guild
channel = client.get_channel(id_dict['channel-id'])

client.run(id_dict['bot-token'])