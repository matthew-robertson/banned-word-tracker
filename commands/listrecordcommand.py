from commands.command import Command
from utils.time import format_seconds

class ListRecordCommand(Command):
    def get_banned_word_text(self, ban, current_time):
        established_record = ban.record_seconds
        potential_record = (current_time - ban.infracted_at).total_seconds()

        times_infracted = "The server has said '{}' {} time".format(ban.banned_word, ban.infraction_count)
        if not ban.infraction_count == 1:
            times_infracted += "s"
        times_infracted += "."

        if established_record < potential_record:
            record_time = format_seconds(potential_record)
            return times_infracted + "\nThe server's currently on its longest streak without saying '{}': {}.".format(ban.banned_word, record_time)
        else:
            record_time = format_seconds(established_record)
            return times_infracted + "\nThe server's longest streak without saying '{}' is {}.".format(ban.banned_word, record_time)

    def execute(self, current_server, current_time, message, author):
        msg_to_send = ""
        banned_words = current_server.banned_words

        try:
            requested_index = int(message.split(" ")[1]) - 1
            if requested_index < 0 or requested_index >= len(banned_words): raise
            msg_to_send += self.get_banned_word_text(banned_words[requested_index], current_time)
        except:
            msg_to_send += "\n\n".join(map(lambda ban: self.get_banned_word_text(ban, current_time), banned_words))
        return msg_to_send