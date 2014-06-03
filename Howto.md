# How-to Play RPS
In the following sections, we'll walk you through how to start a server, how to
connect to a server, how to create a game, and finally how to join and play a
game.

## Starting a Server:
Prior to starting the server, you need to make sure that python scripts are
allowed to run on your machine.

To start the server, simply run the python script on the machine that you would
like the server to run on. The server will then be open to communications on
port 22066. Since the current version of the client is hardcoded to attach to a
specific server, you will need to change the connection ip to your server's ip
addr to allow the client to connect to your server.

Thats it. If you would like to suggest commands you would like to see the server
preform, please email finn@finn.io. For complaints, please see the Muffin Man.
He lives on Drury Lane.

## Starting a client
To start a connection with the server, currently, you simply have to start the
client.py. The client will then prompt you for a username, which it then checks
if the username is unique within the server. If the username is found to be
unique, you will then be registered within the server.

After successfully registering with the server, you will then be prompted with
the game menu. Upon the prompt, type the letter assigned to each option then
press enter. The following are a list of the different letters and their
respective options:

s - Show the scoreboard
c - Create a new game
l - List games
j - Join an existing game
e - Exit

## Creating a game
First, assuming you have followed all of the client steps so far, at the main
menu, type `c` then press enter. This will then allow you to create a game, and
then it will wait for another player to join the game. Once another player has
joined the game, the server will ask you for you move. Input 1 for rock, 2 for
paper, or 3 for scissors, then press enter. After receiving both your throw and
your opponents throw, it will then determine who won or if there was a tie. If a
tie occurred, the server will ask for both throws again, in the same order as
previously. Once a winner is found the server will announce the winner, then
send both players back to the main menu.

## Joining a game
First, assuming you have followed all of the client steps so far, at the main
menu, type `j` then press enter. The client will then print out a list of games
on the server, then ask you for a game id. Upon entering a game, you will wait
for player one to cast his throw, then be asked for yours. Input 1 for rock, 2
for paper, or 3 for scissors, then press enter. Once your thrown is cast, the
server will determine a winner and ask you to throw again upon a tie. Once a
winner is found, the server will announce the winner and send both players back
to the home screen.

## Other commands
The other three commands are fairly self-explainitory. To finish up, to remove
unregister yourself, simply type `e` , press enter, and have a nice day!
