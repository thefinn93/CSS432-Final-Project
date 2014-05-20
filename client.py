#!/usr/bin/env python
import socket
import json

def connect(hostname, port):
    # For now, the server is hard coded
    server = socket.getaddrinfo(hostname, port)

    # server[0] will have the socket family (ie INET or INET6)
    sock = socket.socket(server[0], socket.SOCK_STREAM)

    # server[4] is a tuple in form (ip, port)
    sock.connect(server[4])

    return (sock, 0)

# Plays 1 game of rock paper scissors
def playGame(sock, clientid):
     print "Sorry, I don't know how to play :("
     return False

if __name__ == "__main__":
    # Function to connect and authenticate with the server
    sock, clientid = connect('localhost', 22066)

    # Play until the user doesn't want to anymore
    donePlaying = False
    while not donePlaying:
        donePlaying = playGame(sock, clientid)

    # Close the socket (maybe we should say goodbye?)
    sock.close()
