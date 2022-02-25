import discord

import pandas as pd, re, json, numpy as np, datetime as dt

id_dict = json.load(open("ids.json"))

class coverdle_client(discord.Client):

    def read_coverdle_data(self):

        self.df = pd.read_csv("./coverdle_data.csv")

        # self.df.date = pd.to_datetime(self.df.date)
        # self.df.time = pd.to_datetime(self.df.time)

    def which_game(self, msg):

        is_wordle = not not re.search(r'Wordle \d+ \d{1}[/]6', msg.content)
        is_worldle = not not re.search(r'#Worldle #\d+ \d{1}[/]6', msg.content)
        is_nerdle = not not re.search(r"nerdlegame \d+ \d{1}[/]6", msg.content)
        is_quordle = not not re.search(r"Daily Quordle #\d+", msg.content)

        self.rdle_bools = [is_wordle, is_worldle, is_nerdle, is_quordle]

    def find_score(self, msg):

        if self.game != "Quordle":

            self.score = int(re.search(r'\d{1}[/]6', msg.content).group()[0])
            self.quordle_scores = [np.nan]*4
            
        else:

            self.score = np.nan
            self.quordle_scores = list(
                msg.content
                [
                    re.search(r'Daily Quordle #\d+', msg.content)
                    .end():
                    ]
                .replace('\n', '')
                [::3][:4]
                )

    def append_data(self):

        self.df = self.df.append(pd.DataFrame([[
            self.author, self.msg_day,
            self.game, self.score] + self.quordle_scores
        ], columns = self.df.columns))

        self.df.to_csv("./coverdle_data.csv", index=None)

    async def on_message(self, msg):

        if msg.author == client.user:
            return None

        if msg.channel.name != 'wordle':
            return None

        self.which_game(msg)
        rdle_names = ["Wordle", "Worldle", "Nerdle", "Quordle"]

        if max(self.rdle_bools) == 0:
            return None
        
        self.author = msg.author
        self.author_name = msg.author.name
        self.msg_day = msg.created_at.strftime("%Y%m%d")
        self.game = rdle_names[self.rdle_bools.index(True)]

        self.read_coverdle_data()
        self.find_score(msg)
        self.append_data()

        await msg.channel.send("data saved!")


class reporting:

    def __init__(self):

        self.df = coverdle_client.read_coverdle_data()

    def map_author_to_username(self):

        pass

    def user_performance(self):

        pass

    def aggregate_over_month(self):

        pass

    def aggregate_all_time(self):

        pass



client = coverdle_client()
guild = discord.Guild
channel = client.get_channel(id_dict['channel-id'])

client.run(id_dict['bot-token'])