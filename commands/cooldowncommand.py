from commands.command import Command
from utils.time import format_seconds, format_time

class CooldownCommand(Command):
    def get_banned_word_text(self, ban, current_time):
        timeoutRemaining = format_time(ban.timeout_expiration_time, current_time)
        if ban.is_cooldown_active:
            return "I'll be able to issue another alert for '{}' in {}.".format(ban.banned_word, timeoutRemaining)
        else:
            return "I'm ready to issue another warning for '{}' now.".format(ban.banned_word)

    def execute(self, current_server, current_time, message=None, author=None):
        timeout_length = format_seconds(current_server.timeout_duration_seconds)
        msg_to_send = "The cooldown period is {}.\n".format(timeout_length)
        msg_to_send += "\n".join(map(lambda ban: self.get_banned_word_text(ban, current_time), current_server.banned_words))
        return msg_to_send