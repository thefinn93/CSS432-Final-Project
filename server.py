#!/usr/bin/env python
import SocketServer
import json
import threading
import logging
# import enum

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
                            self.list(message)
                        elif message['action'] == "challange":
                            self.challange(message)
                        elif message['action'] == "create":
                            self.create(message)
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

    def challange(self, message):
        logging.warning("Shit shit I don't know how to do this thing!",
          extra=self.logInfo)
        self.request.sendall(json.dumps({
          "result": "error",
          "excuse": "Shit shit I don't know how to do this thing!"
        }))

    def list(self, message):
        """Lists all available opponents"""
        list = []
        for client in clients:
            # Don't list ourselves
            if client != self.clientID:
                entry = {}
                entry['name'] = clients[client]['name']
                entry['id'] = client
                entry['score'] = 9999
                list.append(entry)
        logging.debug("Sending list of %i clients", len(list), extra=self.logInfo)
        self.request.sendall(json.dumps({
          "result": "success",
          "list": list
        }))

    # needs logging info
    def create(self,message):
        noOtherGames = True
        foundGameSlot = False
        # Check if the user has aleady opened a game
        for game in PRSgames:
            if game['playerOne'] == self.clientID:
              noOtherGame = False

        if noOtherGames:
            # Check for an empty game slot
            for game in RPSgames:
                # If there is, put player creating creating as p1
                if game['state'] == "empty":
                    game['state'] = gameStates['open']
                    game['playerOne'] = self.clientID
                    logging.debug("Sending creation confirmation...")
                    self.request.sendall(json.dumps({
                    "result": "success",
                    "gameid": game['gameID']
                    }))
                    foundGameSlot = True

            if not foundGameSlot:
                logging.debug("failed to create a game at this time...")
                self.request.sendall(json.dumps({
                "result": "error",
                "excuse": "the straw that broke the camel's back..."
                }))


    def join(self,message):

        print "Count me in!"
        if "gameid" in message:
          RPSgames[message['gameid']]['state'] = gameStates['closed']
          RPSgames[message['gameid']]['playerTwo'] = self.clientID

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

# enum for throw types
# from enum import Enum
# class GThrow(Enum):
#    blank = 0
#    rock = 1
#    paper = 2
#    scissors = 3

if __name__ == "__main__":
    logformat = "[%(asctime)s][%(levelname)s][%(threadName)s][%(clientIP)s][%(clientName)s] %(message)s"
    # First, configure the logger to dump to server.log
    logging.basicConfig(filename="server.log", level=logging.DEBUG, format=logformat)
    HOST, PORT = "localhost", 22066
    clients = {}
    # Define rps throws
    gameThrow = {
      "blank": 0,
      "rock": 1,
      "paper": 2,
      "scissors": 3
      }

    # Dictionary of game states
    gameStates = {
      "empty": 0,
      "open": 1,
      "closed": 2,
      "playing": 3,
      "results": 4
    }

    # Pool of game objects to use
    RPSgames = []
    for k in range(20):
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
