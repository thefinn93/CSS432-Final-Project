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
    sock.send(goodbyeMsg)
    sock.close()

def listOpponents(sock, clientid):
    logging.info("Looking for opponents")
    sock.send(json.dumps({'action':'list', 'clientid': clientid}))
    rawresponse = sock.recv(1024).strip()
    logging.info("Received back %s", rawresponse)
    response = json.loads(rawresponse)
    logging.debug("Successfully Parsed response")
    if "list" in response:
        print "Name\tID\tScore"
        for player in response['list']:
            print "%s\t%s\t%s" % (player['name'], player['id'], player['score'])
    else:
        print response

def listGames(sock, clientid):
    logging.info("Looking for games")
    sock.send(json.dumps({'action':'glist'}))
    logging.info("Sent request")
    rawresponse = sock.recv(1024).strip()
    logging.info("Received back %s", rawresponse)
    response = json.loads(rawresponse)
    logging.debug("Successfully Parsed response")
    if "list" in response:
        print "Game ID\tState\tPlayer One\tPlayer Two"
        for game in response['list']:
            print "%s\t%s\t%s\t%s" % (game['gameid'], game['state'], game['playerOne'], game['playerTwo'])
    else:
        print response

# Plays 1 game of rock paper scissors
def playGame(sock, clientid):
    logging.warning("Attempting to play game I don't know how to play!")
    print "Sorry, I don't know how to play :("
    return True

# The function used to request a game be created
def createGame(sock, clientid):
    logging.info("Let's build it!")
    sock.send(json.dumps({
      "action": "create",
      "clientid": clientid
    }))
    print "Please wait..."
    response = json.loads(sock.recv(1024).strip())
    if "result" in response:
        if response['result'] == "success":
            gameid = response["gameid"]
            print gameid
        else:
            print "Please try again later..."
            print response['excuse']
            return
    print "Waiting for an opponent..."

    while True:
        response = json.loads(sock.recv(1024).strip())
        if "request" in response:
            if response['request'] == "throw":
                screenMessage = "1. rock\t2. paper\t3. scissors\nWhat do you throw because %s\n" % (response['reason'])
                throw = raw_input(screenMessage)
                sock.send(json.dumps({
                  "action": "throw",
                  "type": throw
                }))
        elif "result" in response:
          if response['result'] == "finished":
            print response['message']
            return

def joinGame(sock, clientid):
    print "I wanna play too!"
    gameid = raw_input("What is the game id of the game you want to play?")
    sock.send(json.dumps({
      "action": "join",
      "gameid": gameid
    }))
    print "Request sent...please wait..."
    response = json.loads(sock.recv(1024).strip())
    if "result" in response:
        if response['result'] == "success":
            playerid = response['playerid']
            print "Your are %s" % (playerid)
        else:
            print "Please try again later..."
            print response['excuse']
            return

    while True:
        response2 = json.loads(sock.recv(1024).strip())
        if "request" in response2:
            if response2['request'] == "throw":
                screenMessage = "1. rock\t2. paper\t3. scissors\nWhat do you throw because %s" % (response2['reason'])
                throw = raw_input(screenMessage)
                sock.send(json.dumps({
                  "action": "throw",
                  "type": throw
                }))
        elif "result" in response2:
          if response2['result'] == "finished":
            print response2['message']
            return

if __name__ == "__main__":
    # First, configure the logger to dump to client.log
    logformat = "[%(asctime)s][%(levelname)s] %(message)s"
    logging.basicConfig(filename="client.log", level=logging.DEBUG, format=logformat)
    # Function to connect and authenticate with the server
    sock = connect('localhost', 22066)

    # We don't really need to send this with each packet, do we....
    clientid = register(sock)

    # Play until the user doesn't want to anymore
    exit = False
    while not exit:
        print """OMG ITS TEH MENUZ!
        The following options are available:

        l    List other people available to play
        c    Challenage someone
        n    Create a new game
        j    Join an existing game
        e    Exit"""
        action = raw_input("What would you like to do? ")
        if action == "l":
            listOpponents(sock, clientid)
        elif action == "c":
            playGame(sock, clientid)
        elif action == "n":
            createGame(sock, clientid)
        elif action == "j":
            joinGame(sock, clientid)
        elif action == "lg":
            listGames(sock, clientid)
        elif action == "e":
            exit = True
        else:
            print "Dude, not an option. Cmon."

    # Close the socket (maybe we should say goodbye?)
    disconnect(sock, clientid)
