#!/usr/bin/env python
import SocketServer
import json
import logging

class RPSServerHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        self.logInfo = {"clientIP": self.client_address[0], "clientName": "-"}
        logging.info("new connection!", extra=self.logInfo)
        # self.request is the TCP socket connected to the client
        registered = False
        while not registered:
            logging.info("Attempting to register", extra=self.logInfo)
            self.data = self.request.recv(1024).strip()
            logging.debug("Got message: %s", self.data, extra=self.logInfo)
            try:
                message = json.loads(self.data)
                if "action" in message:
                    if message['action'] == "register":
                        if "name" in message:
                            if len(message['name']) < 21:
                                if not message['name'] in clients:
                                    self.logInfo['clientName'] = message['name']
                                    self.clientid = message['name']
                                    logging.info("Name is valid! Registration succssful", extra=self.logInfo)
                                    clients[self.clientid] = {}
                                    registered = True
                                    clients[self.clientid]['status'] = 0
                                    logging.debug("Informing client registration was successful", extra=self.logInfo)
                                    self.request.sendall(json.dumps({
                                      "result": "success",
                                      "clientid": self.clientid
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
                    else:
                        logging.warning("Tried to %s without first registering", message['action'], extra=self.logInfo)
                        self.request.sendall(json.dumps({
                          "result": "error",
                          "excuse": "Please register first"
                        }))
                else:
                    logging.warning("Made a request but did not specify an action", extra=self.logInfo)
                    self.request.sendall(json.dumps({
                      "result": "error",
                      "excuse": "No action specified"
                    }))
            except ValueError:
                logging.warning("Invalid JSON received: %s", self.data, extra=self.logInfo)
                self.request.sendall(json.dumps(
                  {
                    "result":"error",
                    "excuse": "Unreadable message, please try again."
                  }))
        logging.info("Successfully registered, but actual gameplay has not yet been coded!! OH NOEZ!", extra=self.logInfo)

    def finish(self):
        logging.info("Disconnecting...", extra=self.logInfo)
        try:
            clients.pop(self.clientid)
        except AttributeError:
            pass



if __name__ == "__main__":
    logformat = "[%(asctime)s][%(levelname)s][%(clientIP)s][%(clientName)s] %(message)s"
    # First, configure the logger to dump to server.log
    logging.basicConfig(filename="server.log", level=logging.DEBUG, format=logformat)
    HOST, PORT = "localhost", 22066
    clients = {}
    server = SocketServer.TCPServer((HOST, PORT), RPSServerHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "Server is running. Press CTRL-C to stop. tailf server.log for extra fun technobabble"
    server.serve_forever()
