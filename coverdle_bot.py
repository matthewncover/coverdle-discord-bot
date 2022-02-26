import discord

import pandas as pd, re, json, numpy as np, datetime as dt

id_dict = json.load(open("ids.json"))

class coverdle_client(discord.Client):

    def read_coverdle_data(self):

        self.df = pd.read_csv("./coverdle_data.csv")

        # self.df.date = pd.to_datetime(self.df.date)
        # self.df.time = pd.to_datetime(self.df.time)

    def which_game(self, msg):

        is_wordle = not not re.search(r'Wordle \d+ (\d{1}|X)[/]6', msg.content)
        is_worldle = not not re.search(r'#Worldle #\d+ (\d{1}|X)[/]6', msg.content)
        is_nerdle = not not re.search(r"nerdlegame \d+ \d{1}[/]6", msg.content)
        is_quordle = not not re.search(r"Daily Quordle #\d+", msg.content)

        self.rdle_bools = [is_wordle, is_worldle, is_nerdle, is_quordle]

    def find_score(self, msg):

        if self.game != "Quordle":

            self.score = re.search(r'(\d{1}|X)[/]6', msg.content).group()[0]
            self.score = 0 if self.score == "X" else int(self.score)
            self.quordle_scores = [np.nan]*4

            self.is_hard_mode = 0
            if self.game == 'Wordle':
                self.is_hard_mode = int(
                    msg.content[
                        re.search(r'(\d{1}|X)[/]6', msg.content).end():
                        ][0] == '*'
                        )
            
        else:

            self.score = np.nan

            quordle_message_score_contents = (
                msg.content[
                    re.search(r'Daily Quordle #\d+', msg.content).end():
                    re.search(r'quordle.com', msg.content).start()
                ]
                .replace('\n', '')
            )

            self.quordle_scores = (
                [
                    0 if z == '\U0001f7e5' else int(z)
                    for z in [
                        x for x in list(quordle_message_score_contents)
                        if x not in ('️', '⃣')
                        ]
                ]
            )


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

        if msg.author == client.user:
            return None

        if msg.channel.name != 'wordle':
            return None

        self.which_game(msg)
        rdle_names = ["Wordle", "Worldle", "Nerdle", "Quordle"]

        if max(self.rdle_bools) == 0:
            # check if command
            return None
        
        self.author = f"{msg.author.name}#{msg.author.discriminator}"

        try:
            self.author_name = id_dict['author-ids'][self.author]
        except:
            self.author_name = "Who?"
        
        self.msg_day = msg.created_at.strftime("%Y%m%d")
        self.game = rdle_names[self.rdle_bools.index(True)]

        self.read_coverdle_data()
        self.find_score(msg)
        self.append_data()

class reporting:

    def __init__(self):

        self.df = coverdle_client.read_coverdle_data()
        self.report_msg = ''

    def user_performance(self):

        pass

    def num_games_played(self):

        pass

    def aggregate_over_month(self, monthyear):

        self.report_msg += f'{monthyear}\n--------\n'

        pass

    def aggregate_all_time(self):

        pass



client = coverdle_client()
guild = discord.Guild
channel = client.get_channel(id_dict['channel-id'])

client.run(id_dict['bot-token'])