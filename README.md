[![Build Status](https://travis-ci.com/matthew-robertson/banned-word-tracker.svg?branch=master)](https://travis-ci.com/matthew-robertson/banned-word-tracker) <a href="https://www.patreon.com/bePatron?u=19559602"><img alt="become a patron" src="https://c5.patreon.com/external/logo/become_a_patron_button.png" height="35px"></a>

# banned-word-tracker
A simple discord bot designed to keep track of however long a server can go without referencing a banned word.

The bot can be added to your server [here](https://discordapp.com/oauth2/authorize?client_id=355144450437021697&scope=bot&permissions=3072).

I have a support discord set up [here](https://discord.gg/nUZsfYS).

The bot monitors all messages for a message like the word the server has banned (specifically, case-insensitive, accent-insensitive, ensuring there are word-breaks on either side of the phrase). The bot will reset the server's timer if it finds a message containing a match, and call the user out publically. After calling out one user, the bot will silently reset the counter until a customizable amount of time has passed.

The default banned word is "defaultbannedword", and the default timeout is half an hour.
The bot provides a few commands which are available to all users: 
* "!vthelp" - List all available commands.
* "!vt" - Will list how long the server has gone without saying each currently banned word.
* "!vtct" - Will list how long the timeout is set for, and when/if another issue can be issued for each banned word.
* "!vtlast" - DEPRECATED, Will list how long it has been since a callout has been issued for each currently banned word.

The bot also provides a few commands available only to server admins:
* "!vtsilence" - Prevent the bot from sending messages calling out users.
* "!vtalert" - Allow the bot to send messages to call out users.
* "!vtban [word_to_ban]" - Change the currently banned word. For example, "!vtban bepis" will ban the word "bepis". If multiple words are mentioned, only the first one will be banned. 
* "!vtdelay hh:mm:ss" - Change the bot's timeout for the server to the specified amount. For example, "!vtdelay 23:59:59" will set the minimum time between callouts to just under a full day.
