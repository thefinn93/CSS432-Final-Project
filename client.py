#!/usr/bin/env python
import socket
import json
import logging

def connect(hostname, port):
    # Eventually, we should loop through all results and use the first one that
    # works, but for now
    server = socket.getaddrinfo(hostname, port)[0]
    logging.debug("Conectiong to %s:%d", server[4][0], server[4][1])

    # server[0] will have the socket family (ie INET or INET6)
    sock = socket.socket(server[0], socket.SOCK_STREAM)

    # server[4] is a tuple in form (ip, port)
    sock.connect(server[4])

    return sock

def register(sock):
    registered = False
    clientid = None
    while not registered:
        logging.debug("Registering with server...")
        name = raw_input("Choose a name: ")
        logging.debug("Name set to %s", name)
        print "Registering...."
        logging.info("Registering as %s", name)
        sock.send(json.dumps({"action": "register", "name": name}))
        rawresponse = sock.recv(1024).strip()
        logging.info("Received back %s", rawresponse)
        try:
            response = json.loads(rawresponse)
            if "result" in response:
                if response["result"] == "success":
                    logging.info("Successfully registered!")
                    if "clientid" in response:
                        clientid = response["clientid"]
                        registered = True
                    else:
                        print "No clientid recieved. Weird, trying again..."
                        logging.warning("No client ID received. Trying again.")
                elif response["result"] == "error":
                    if "excuse" in response:
                        print "Failed to register: %s" % response['excuse']
                        logging.warning("Failed to register. Excuse: %s", response['excuse'])
                    else:
                        print "Failed to register (unknown reason)"
                        logging.warning("Failed to register, no excuse given")
                else:
                    print "Unrecognized result from server: %s" % response['result']
                    logging.warning("Unrecognized result from server: %s", response['result'])
        except ValueError:
            logging.warning("Failed to parse %s", rawresponse)
            print "Received unreadable message from the server :("
            print rawresponse
    return clientid

def disconnect(sock, clientid):
    logging.info("Sending disconnect message and closing socket")
    goodbyeMsg = json.dumps({'client': clientid, 'action': 'disconnect'})
    sock.sendall(goodbyeMsg)
    sock.close()

def pickOpponent(sock, clientid):
    logging.info("Looking for opponents")
    sock.sendall(json.dumps({'action':'list', 'clientid': clientid}))
    response = json.loads(sock.recv(1024))
    if "list" in response:
        print "Name\tID\tScore"
        for player in list:
            print "%s\t%s\t%s" % (player['name'], player['id'], player['score'])
    else:
        print response

# Plays 1 game of rock paper scissors
def playGame(sock, clientid):
    logging.warning("Attempting to play game I don't know how to play!")
    print "Sorry, I don't know how to play :("
    return True

if __name__ == "__main__":
    # First, configure the logger to dump to client.log
    logformat = "[%(asctime)s][%(levelname)s] %(message)s"
    logging.basicConfig(filename="client.log", level=logging.DEBUG, format=logformat)
    # Function to connect and authenticate with the server
    sock = connect('localhost', 22066)

    # We don't really need to send this with each packet, do we....
    clientid = register(sock)

    # List all other players
    pickOpponent(sock, clientid)

    # Play until the user doesn't want to anymore
    donePlaying = False
    while not donePlaying:
        donePlaying = playGame(sock, clientid)

    # Close the socket (maybe we should say goodbye?)
    disconnect(sock, clientid)
