#!/usr/bin/env python
import socket
import json

def connect(hostname, port):
    # Eventually, we should loop through all results and use the first one that
    # works, but for now
    server = socket.getaddrinfo(hostname, port)[0]

    # server[0] will have the socket family (ie INET or INET6)
    sock = socket.socket(server[0], socket.SOCK_STREAM)

    # server[4] is a tuple in form (ip, port)
    sock.connect(server[4])

    return sock

def register(sock):
    registered = False
    clientid = None
    while not registered:
        name = raw_input("Choose a name: ")
        print "Registering...."
        sock.send(json.dumps({"action": "register", "name": name}))
        rawresponse = sock.recv(1024).strip()
        try:
            response = json.loads(rawresponse)
            if "result" in response:
                if response["result"] == "success":
                    if "clientid" in response:
                        clientid = response["clientid"]
                        registered = True
                    else:
                        print "No clientid recieved. Weird, trying again..."
                elif response["result"] == "error":
                    if "excuse" in response:
                        print "Failed to register: %s" % response['excuse']
                    else:
                        print "Failed to register (unknown reason)"
                else:
                    print "Unrecognized result from server: %s" % response['result']
        except ValueError:
            print "Received unreadable message from the server :("
            print rawresponse
    return clientid

def disconnect(sock, clientid):
    goodbyeMsg = json.dumps({'client': clientid, 'action': 'disconnect'})
    sock.send(goodbyeMsg)
    sock.close()

# Plays 1 game of rock paper scissors
def playGame(sock, clientid):
     print "Sorry, I don't know how to play :("
     return True

if __name__ == "__main__":
    # Function to connect and authenticate with the server
    sock = connect('localhost', 22066)

    clientid = register(sock)

    # Play until the user doesn't want to anymore
    donePlaying = False
    while not donePlaying:
        donePlaying = playGame(sock, clientid)

    # Close the socket (maybe we should say goodbye?)
    sock.close()
