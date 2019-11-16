from commands.command import Command
from utils.time import format_time

class TimerCommand(Command):
    def execute(self, current_server, current_time, message=None, author=None):
        banned_words = current_server.banned_words
        timeLasted = format_time(current_time, banned_words[0].infracted_at)
        msg_to_send = "The server has gone {} without mentioning '{}'.".format(timeLasted, banned_words[0].banned_word)
        for banned_word in banned_words[1:]:
            timeLasted = format_time(current_time, banned_word.infracted_at)
            msg_to_send += "\nThe server has gone {} without mentioning '{}'.".format(timeLasted, banned_word.banned_word)

        return msg_to_send