# vore-tracker
A simple discord bot designed to keep track of however long a server can go without referencing vore.

The bot can be added to your server [here](https://discordapp.com/oauth2/authorize?client_id=355144450437021697&scope=bot&permissions=3072).

The bot provides a few commands: "!vthelp" which lists all available commands. "!vt" which will tell you how long the server has gone without mentioning the word "vore." "!vtsilence" for which the administrator permission is required, which will silence the bot while active. "!vtalert" which requires the administrator permission and unsilences the bot.

The bot also monitors all messages for a message like "vore" (specifically, case-insensitive, accent-insensitive, ensuring there are word-breaks on either side of the phrase), and will reset the server's counter if it finds a message containing a match after calling out the user publically. After calling out one user, the bot will silently reset the counter until a half hour has passed since its last callout (This may change to be admin configurable later).

