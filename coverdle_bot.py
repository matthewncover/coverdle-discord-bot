import discord

import pandas as pd, re, json, numpy as np

from wordle_reports import Reporting

import warnings
warnings.simplefilter('ignore')

id_dict = json.load(open("ids_aof.json"))

# id_dict = json.load(open("ids_aof.json"))

class CoverdleClient(discord.Client):

    def on_command(self, msg):

        self.cmd_args = msg.content.split(' ')[1:]

        if self.cmd_args[0] == 'help':
            self.report = self.help_command()
            return
        
        for cmd_arg, arg_name in zip(
            self.cmd_args, list(id_dict['cmd-args'].keys())
            ):
            if not cmd_arg in id_dict['cmd-args'][arg_name]:
                try:
                    pd.to_datetime([self.cmd_args[2]], format='%b%y')
                except:
                    self.report = self.invalid_command(cmd_arg)
                    return

        self.read_coverdle_data()
        self.report_obj = Reporting(self.cmd_args, self.df)
        self.report = self.report_obj.report_msg

    def invalid_command(self, cmd_arg:str):

        return f"""
        {cmd_arg} is an invalid command in that position.
        Type "{self.cmd_start_str} help" for a list of commands.
        """

    def help_command(self):

        return f"""
        Command format:
        {self.cmd_start_str} <game option> <stat option> <date option>

        game options:
            all_games, wordle, worldle, nerdle, quordle
        
        stat options:
            all_stats, user_performance, game_popularity,
            team_performance, stoke_meter
        
        date options:
            all_time, abbreviated month-year (ex. Feb22)

        examples:
            {self.cmd_start_str} quordle user_performance all_time
            {self.cmd_start_str} all_games stoke_meter Mar22
        """

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

        self.df = pd.read_csv(f"./{id_dict['csv-fn']}")


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

            try:
                self.quordle_scores = (
                    [
                        "X" if z == '\U0001f7e5' else int(z)
                        for z in [
                            x for x in list(quordle_message_score_contents)
                            if x not in ('️', '⃣')
                            ]
                    ]
                )
            except:
                self.quordle_scores = ["X", "X", "X", "X"]

            # convert to max score of 6 scale
            self.score = (
                'X' if 'X' in self.quordle_scores
                else np.array(self.quordle_scores).mean()*(2/3)
                ) 


    def append_data(self):

        if (
            self.df[
                (self.df.name == self.author_name)
                 & (self.df.day == int(self.msg_day))
                 & (self.df.game == self.game)
                 ].shape[0]
            ) == 0:

            self.df = self.df.append(pd.DataFrame([[
                self.author, self.author_name, self.msg_day,
                self.game, self.is_hard_mode, self.score] + self.quordle_scores
            ], columns = self.df.columns))

            self.df.to_csv("./coverdle_data.csv", index=None)

            print(f"{self.game} entry added - {self.author_name} on {self.msg_day}")

    async def on_message(self, msg):

        self.read_coverdle_data()
        self.rdle_names = ["Wordle", "Worldle", "Nerdle", "Quordle"]

        # first, checks db and updates with history
        self.last_entry = self.df.loc[self.df.shape[0]-1, ['name', 'day', 'game']].values.tolist()
        hist = msg.channel.history(limit=1000)
        async for h in hist:

            if h.author == client.user:
                continue

            if h.channel.name != 'wordle':
                continue

            self.which_game(h)

            if max(self.rdle_bools) == 1:

                hist_name = id_dict['author-ids'][f"{h.author.name}#{h.author.discriminator}"]
                hist_day = int(h.created_at.strftime("%Y%m%d"))
                hist_game = self.rdle_names[self.rdle_bools.index(True)]

                if self.last_entry == [hist_name, hist_day, hist_game]:
                    break
                else:
                    self.on_wordle_entry(h)

        # ignore if the bot sent the message
        if msg.author == client.user:
            return None

        # ignore if message is not in wordle channel
        if msg.channel.name != 'wordle':
            return None

        self.cmd_start_str = "$420"

        # trigger command
        if msg.content.startswith(self.cmd_start_str):
            self.on_command(msg)

            await msg.channel.send(self.report)

        self.which_game(msg)

        # add to 
        if max(self.rdle_bools) == 1:
            self.on_wordle_entry(msg)

        # regular chat
        else:
            return None       


client = CoverdleClient()
guild = discord.Guild
channel = client.get_channel(id_dict['channel-id'])

client.run(id_dict['bot-token'])