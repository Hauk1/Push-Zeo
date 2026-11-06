Push-Zeo
========

Removed pushing to Singly, now it gives json in the terminal ready to be explored.

Built an interface for Beau's code.

Usage:
Enter API key and the domain connected to the key. Then run the file in an interactive terminal and type username and password. Password input is hidden; the program stops if it cannot disable terminal echo.

It gathers the last 14 days, but that can be alterd under DAYS_TO_GATHER.


Run it once a day from an interactive terminal. Unattended `cron` execution is not supported by the current password prompt.
