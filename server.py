#!/usr/bin/env python
import SocketServer
import json
import threading
import logging
# import enum

# Server Thread
class RPSServerHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        self.logInfo = {
          "clientIP": self.client_address[0],
          "clientName": "-"
          }
        self.currentGame = None
        self.clientID = None
        logging.info("new connection!", extra=self.logInfo)

        disconnectRequest = False
        while not disconnectRequest:
            data = self.request.recv(1024).strip()
            logging.debug("Got message: %s", data, extra=self.logInfo)
            try:
                message = json.loads(data)
                if "action" in message:
                    # Register client
                    if message['action'] == "register":
                        self.register(message)
                    # Unregister Client
                    elif message['action'] == "disconnect":
                        disconnectRequest = True
                        logging.info("Got disconnect request", extra=self.logInfo)
                    # List challengers
                    # Breaks the protocol
                    elif self.clientID != None:
                        if message['action'] == "list":
                            self.listPlayers()
                        elif message['action'] == "glist":
                            self.listGames()
                        elif message['action'] == "create":
                            self.create()
                        elif message['action'] == "join":
                            self.join(message)
                        else:
                            logging.warning("Received request for unrecognized action %s",
                              message['action'],
                              extra=self.logInfo)
                            self.request.sendall(json.dumps({
                              "result": "error",
                              "excuse": "Unrecognized action"
                            }))
                    else:
                        logging.warning("Tried to %s without first registering",
                          message['action'],
                          extra=self.logInfo)
                        self.request.sendall(json.dumps({
                          "result": "error",
                          "excuse": "Please register first"
                        }))
                else:
                    logging.warning("Made a request but did not specify an action",
                      extra=self.logInfo)
                    self.request.sendall(json.dumps({
                      "result": "error",
                      "excuse": "No action specified"
                }))
            except ValueError:
                logging.warning("Invalid JSON received: %s", data,
                  extra=self.logInfo)
                self.request.sendall(json.dumps(
                  {
                    "result":"error",
                    "excuse": "Unreadable message, please try again."
                  }))

    def finish(self):
        logging.info("Disconnecting...", extra=self.logInfo)
        try:
            clients.pop(self.clientID)
        except AttributeError:
            pass

    def register(self, message):
        logging.info("Attempting to register...", extra=self.logInfo)
        if "name" in message:
            if len(message['name']) < 21:
                if not message['name'] in clients:
                    self.logInfo['clientName'] = message['name']
                    self.clientID = message['name']
                    logging.info("Name is valid! Registration succssful", extra=self.logInfo)
                    clients[self.clientID] = {}
                    clients[self.clientID]['inGame'] = False
                    clients[self.clientID]['name'] = message['name']
                    clients[self.clientID]['score'] = 0;
                    logging.debug("Informing client registration was successful", extra=self.logInfo)
                    self.request.sendall(json.dumps({
                      "result": "success",
                      "clientid": self.clientID
                    }))
                else:
                    logging.info("Tried to take an in use name", extra=self.logInfo)
                    self.request.sendall(json.dumps({
                      "result": "error",
                      "excuse": "That name is in use."
                    }))
            else:
                logging.info("Tried to use an oversized name", extra=self.logInfo)
                self.request.sendall(json.dumps({
                  "result": "error",
                  "excuse": "That name is too long (max 20 characters)"
                }))
        else:
            logging.warning("Tried to register, but didnt specify a name!", extra=self.logInfo)
            self.request.sendall(json.dumps({
              "result": "error",
              "excuse": "Please specify a name"
            }))

    # Note: for some reason it sends the json in reverse order, not sure why
    def listPlayers(self):
        """Lists all available opponents"""
        playerList = []
        for client in clients:
            # Don't list ourselves
            if client != self.clientID:
                entry = {}
                entry['name'] = clients[client]['name']
                entry['id'] = client
                entry['score'] = clients[client]['score']
                playerList.append(entry)
        logging.debug("Sending list of %i clients", len(playerList), extra=self.logInfo)
        self.request.sendall(json.dumps({
          "result": "success",
          "list": playerList
        }))

    # Mainly a dev function, prints out the list of all game slots
    # Note: for some reason it sends the json in reverse order, not sure why
    def listGames(self):
        """Lists all available game"""
        gameList = []
        for game in RPSgames:
            entry = {}
            entry['gameid'] = game['gameID']
            entry['state'] = game['state']
            entry['playerOne'] = game['playerOne']
            entry['playerTwo'] = game['playerTwo']
            gameList.append(entry)
        self.request.sendall(json.dumps({
          "result": "success",
          "list": gameList
        }))

    # needs logging info
    def create(self):
        noOtherGames = True
        foundGameSlot = False
        # Check if the user has aleady opened a game
        for game in RPSgames:
            if game['playerOne'] == self.clientID:
              noOtherGames = False

        if noOtherGames:
            # Check for an empty game slot
            for game in RPSgames:
                # If there is, put player creating creating as p1
                if game['state'] == gameStates['empty']:
                    game['state'] = gameStates['open']
                    game['playerOne'] = self.clientID
                    # logging.debug("Sending creation confirmation...")
                    self.request.sendall(json.dumps({
                    "result": "success",
                    "gameid": game['gameID']
                    }))
                    foundGameSlot = True
                    runRPSGame(game['gameID'],RPSgames,self.request,1)
                    if RPSgames[game['gameID']]['winner'] == self.clientID:
                        clients[self.clientID]['score'] += 1
                        RPSgames[game['gameID']]['state'] = gameStates["empty"],
                        RPSgames[game['gameID']]['playerOne'] = "empty",
                        RPSgames[game['gameID']]['throwOne'] = gameThrow["blank"],
                        RPSgames[game['gameID']]['playerTwo'] = "empty",
                        RPSgames[game['gameID']]['throwTwo'] = gameThrow["blank"],
                        RPSgames[game['gameID']]['winner'] = "empty"
                    break
                # else:
                #    print "Game %s is currently %s..." % (game['gameID'], game['state'])

            if not foundGameSlot:
                # logging.debug("failed to create a game at this time...")
                self.request.sendall(json.dumps({
                "result": "error",
                "excuse": "the straw that broke the camel's back..."
                }))
        else:
            self.request.sendall(json.dumps({
            "result": "error",
            "excuse": "You can't have two games!"
            }))
            print "You can't have two games!"

    def join(self,message):

        # print "Count me in!"
        if "gameid" in message:
          gameid = int(message['gameid'])
          RPSgames[gameid]['playerTwo'] = self.clientID
          self.request.sendall(json.dumps({
          "result": "success",
          "playerid": "playerTwo"
          }))
          RPSgames[gameid]['state'] = gameStates['closed']
          runRPSGame(gameid,RPSgames,self.request,2)
          if RPSgames[gameid]['winner'] == self.clientID:
              clients[self.clientID]['score'] += 1
              RPSgames[gameid]['state'] = gameStates["empty"],
              RPSgames[gameid]['playerOne'] = "empty",
              RPSgames[gameid]['throwOne'] = gameThrow["blank"],
              RPSgames[gameid]['playerTwo'] = "empty",
              RPSgames[gameid]['throwTwo'] = gameThrow["blank"],
              RPSgames[gameid]['winner'] = "empty"

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# Game Master Thread
class gameMaster(threading.Thread):
    def __init__(self,threadID,gamePool):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.gamePool = gamePool

    def run(self):
      print "Lets play!"

# Run a game
def runRPSGame(gameID, gamePool, sock, playerid):
    isWinner = False
    aTie = False
    # Have players play until a winner
    while not isWinner:
      try:
        # Request throw from player one
        if playerid == 1 and gamePool[gameID]['state'] == gameStates['closed']:
            if not aTie:
              sock.sendall(json.dumps({
              "request": "throw",
              "reason": "the game has begun!"
              }))
            elif aTie:
              sock.sendall(json.dumps({
              "request": "throw",
              "reason": "there was a tie!"
              }))
            logging.debug("request sent to player 1")
            data = sock.recv(1024).strip()
            logging.debug("Player 1 sent back %s", data)
            message = json.loads(data)
            gamePool[gameID]['throwOne'] = int(message['type'])
            # if "throw" in message and "type" in message:
            #   if message['type'] == "rock":
            #     gamePool[gameID]['throwOne'] = gameThrow['rock']
            #   elif message['type'] == "paper":
            #     gamePool[gameID]['throwOne'] = gameThrow['paper']
            #   elif message['type'] == "scissors":
            #     gamePool[gameID]['throwOne'] = gameThrow['scissors']
            gamePool[gameID]['state'] = gameStates['playing']
        # Request throw from player two
        elif playerid == 2 and gamePool[gameID]['state'] == gameStates['playing']:
            if not aTie:
              sock.sendall(json.dumps({
              "request": "throw",
              "reason": "the game has begun!"
              }))
            elif aTie:
              sock.sendall(json.dumps({
              "request": "throw",
              "reason": "there was a tie!"
              }))
            logging.debug("request sent to player 2")
            data = sock.recv(1024).strip()
            logging.debug("Player 2 sent back %s", data)
            message = json.loads(data)
            gamePool[gameID]['throwTwo'] = int(message['type'])
            print "player two's throw is %s" % message['type']
            #if "throw" in message and "type" in message:
            #  if message['type'] == "rock":
            #    gamePool[gameID]['throwTwo'] = gameThrow['rock']
            #  elif message['type'] == "paper":
            #    gamePool[gameID]['throwTwo'] = gameThrow['paper']
            #  elif message['type'] == "scissors":
            #    gamePool[gameID]['throwTwo'] = gameThrow['scissors']
            gamePool[gameID]['state'] = gameStates['results']
      except KeyboardInterrupt:
        if playerid == 1:
            gamePool[gameID]['throwOne'] = gameThrow['forfeit']
            gamePool[gameID]['state'] = gameStates['playing']

        elif playerid == 2:
            gamePool[gameID]['throwTwo'] = gameThrow['forfeit']
            gamePool[gameID]['state'] = gameStates['results']

        # Determine winner
      if gamePool[gameID]['state'] == gameStates['results']:
          if gamePool[gameID]['throwOne'] == gameThrow['forfeit']:
              print "%s left..." % gamePool[gameID]['playerOne']
              gamePool[gameID]['winner'] = gamePool[gameID]['playerTwo']
              isWinner = True

          elif gamePool[gameID]['throwTwo'] == gameThrow['forfeit']:
              print "%s left..." % gamePool[gameID]['playerTwo']
              gamePool[gameID]['winner'] = gamePool[gameID]['playerOne']
              isWinner = True

          elif gamePool[gameID]['throwOne'] == gamePool[gameID]['throwTwo']:
              print "Tie!"
              gamePool[gameID]['state'] = gameStates['closed']
              aTie = True

          elif gamePool[gameID]['throwOne'] == gameThrow['rock']:
              if gamePool[gameID]['throwTwo'] == gameThrow['paper']:
                  print "Player two is the winner!"
                  gamePool[gameID]['winner'] = gamePool[gameID]['playerTwo']
                  isWinner = True

              elif gamePool[gameID]['throwTwo'] == gameThrow['scissors']:
                  print "Player one is the winner!"
                  gamePool[gameID]['winner'] = gamePool[gameID]['playerOne']
                  isWinner = True

          elif gamePool[gameID]['throwOne'] == gameThrow['paper']:
              if gamePool[gameID]['throwTwo'] == gameThrow['rock']:
                  print "Player one is the winner!"
                  gamePool[gameID]['winner'] = gamePool[gameID]['playerOne']
                  isWinner = True

              elif gamePool[gameID]['throwTwo'] == gameThrow['scissors']:
                  print "Player two is the winner"
                  gamePool[gameID]['winner'] = gamePool[gameID]['playerTwo']
                  isWinner = True

          elif gamePool[gameID]['throwOne'] == gameThrow['scissors']:
              if gamePool[gameID]['throwTwo'] == gameThrow['rock']:
                  print "Player two is the winner!"
                  gamePool[gameID]['winner'] = gamePool[gameID]['playerTwo']
                  isWinner = True

              elif gamePool[gameID]['throwTwo'] == gameThrow['paper']:
                  print "Player one is the winner!"
                  gamePool[gameID]['winner'] = gamePool[gameID]['playerOne']
                  isWinner = True
    # Send response back to client
    sock.sendall(json.dumps({
    "result": "finished",
    "message": "%s was the winner" % gamePool[gameID]['winner']
    }))

# enum for throw types
# from enum import Enum
# class GThrow(Enum):
#    blank = 0
#    rock = 1
#    paper = 2
#    scissors = 3
# Dictionary of game states
gameStates = {
  "empty": 0,
  "open": 1,
  "closed": 2,
  "playing": 3,
  "results": 4
}

# Define rps throws
gameThrow = {
  "blank": 0,
  "rock": 1,
  "paper": 2,
  "scissors": 3,
  "forfeit": 4
}

if __name__ == "__main__":
    logformat = "[%(asctime)s][%(levelname)s][%(threadName)s][%(clientIP)s][%(clientName)s] %(message)s"
    # First, configure the logger to dump to server.log
    logging.basicConfig(filename="server.log", level=logging.DEBUG, format=logformat)
    HOST, PORT = "0.0.0.0", 22066
    clients = {}

    # Pool of game objects to use
    RPSgames = []
    for k in range(5):
        RPSgames.append({
        "gameID": k,
        "state": gameStates["empty"],
        "playerOne": "empty",
        "throwOne":gameThrow["blank"],
        "playerTwo":"empty",
        "throwTwo":gameThrow["blank"],
        "winner":"empty"})

    server = ThreadedTCPServer((HOST, PORT), RPSServerHandler)

    # Start a thread with the server -- that thread will then start one
    # more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "Server is running. Press CTRL-C to stop. tailf server.log for extra fun technobabble"
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "\nOMG U PRESSED CTRL-C"
        server.shutdown()
