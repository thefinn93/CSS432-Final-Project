#!/usr/bin/env python
import SocketServer
import json

class RPSServerHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        print "Got connecton from somewhere!"
        # self.request is the TCP socket connected to the client
        registered = False
        while not registered:
            print "Attempting to register"
            self.data = self.request.recv(1024).strip()
            try:
                message = json.loads(self.data)
                if "action" in message:
                    if message['action'] == "register":
                        if "name" in message:
                            if len(message['name']) < 21:
                                if not message['name'] in clients:
                                    id = message['name']
                                    clients[id] = {}
                                    registered = True
                                    clients[id]['status'] = 0
                                    self.request.sendall(json.dumps({
                                      "result": "success",
                                      "clientid": id
                                    }))
                                    print "Registered as %s" % id
                                else:
                                    self.request.sendall(json.dumps({
                                      "result": "error",
                                      "excuse": "That name is in use."
                                    }))
                            else:
                                self.request.sendall(json.dumps({
                                  "result": "error",
                                  "excuse": "That name is too long (max 20 characters)"
                                }))
                        else:
                            self.request.sendall(json.dumps({
                              "result": "error",
                              "excuse": "Please specify a name"
                            }))
                    else:
                        self.request.sendall(json.dumps({
                          "result": "error",
                          "excuse": "Please register first"
                        }))
                else:
                    self.request.sendall(json.dumps({
                      "result": "error",
                      "excuse": "No action specified"
                    }))
            except ValueError:
                print "Received invalid JSON from client"
                self.request.sendall(json.dumps(
                  {
                    "result":"error",
                    "excuse": "Unreadable message, please try again."
                  }))
        print "Clients:"
        print clients
        print "There's really nothing else I know how to do yet :("


if __name__ == "__main__":
    HOST, PORT = "localhost", 22066
    clients = {}
    server = SocketServer.TCPServer((HOST, PORT), RPSServerHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    print "Server is running. Press CTRL-C to stop."
    server.serve_forever()
