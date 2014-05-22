#!/usr/bin/env python
import wx
import random
import socket
import json
import logging

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()

names = ["Finn", "JP", "Proly A Hacker", "`; DROP TABLE players;", "player1", "quickjp1", "quickjp2", "quickjp3"]

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (400, 200),
          style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        # Create a status bar
        self.CreateStatusBar()
        self.id = id

        # Build the file menu
        filemenu = wx.Menu()
        filemenu.Append(ID_ABOUT, "&About", "Information about this game")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT, "E&xit", "Quit this shtty game")

        # Build the menu bar
        menubar = wx.MenuBar()
        menubar.Append(filemenu, "&File")

        # Show the menu bar
        self.SetMenuBar(menubar)

        # Connect the menu bar's events
        wx.EVT_MENU(self, ID_ABOUT, self.OnAbout)
        wx.EVT_MENU(self, ID_EXIT, self.OnExit)

        self.outerSizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self.outerSizer)
        self.SetAutoLayout(1)
        self.outerSizer.Fit(self)

        # Show the window
        self.Show()

        self.connect("127.0.0.1", 22066)
        self.register()
        self.listPlayers()

    def listPlayers(self):
        self.sock.sendall(json.dumps({'action':'list'}))
        response = json.loads(self.sock.recv(1024))


        # Build a player list
        self.playerList = wx.ListCtrl(self, self.id, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.playerList.Show(True)
        self.playerList.InsertColumn(0, "Name")
        self.playerList.InsertColumn(1, "Score")

        if "list" in response:
            print "Name\tID\tScore"
            for player in response['list']:
                line = self.playerList.InsertStringItem(0, player['name'])
                self.playerList.SetStringItem(line, 1, str(player['score']))
                print "%s\t%s\t%s" % (player['name'], player['id'], player['score'])
        else:
            print response

        # Make the sizers
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = {}
        for i in ["Invite to play", "Exit"]:
            self.buttons[i] = wx.Button(self, -1, i)
            self.sizer.Add(self.buttons[i], 1, wx.EXPAND)

        self.outerSizer.Add(self.playerList, 1, wx.EXPAND)
        self.outerSizer.Add(self.sizer, 0, wx.EXPAND)

    # Connect to a host and port
    def connect(self, hostname, port):
        # Eventually, we should loop through all results and use the first one that
        # works, but for now
        server = socket.getaddrinfo(hostname, port)[0]
        logging.debug("Conectiong to %s:%d", server[4][0], server[4][1])

        # server[0] will have the socket family (ie INET or INET6)
        self.sock = socket.socket(server[0], socket.SOCK_STREAM)

        # server[4] is a tuple in form (ip, port)
        self.sock.connect(server[4])

    ## Old register function
    def register(self):
        registered = False
        clientid = None
        while not registered:
            logging.debug("Registering with server...")
            name = raw_input("Choose a name: ")
            logging.debug("Name set to %s", name)
            print "Registering...."
            logging.info("Registering as %s", name)
            self.sock.send(json.dumps({"action": "register", "name": name}))
            rawresponse = self.sock.recv(1024).strip()
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


    ### Menu Events ###
    # File -> About
    def OnAbout(self, event):
        d = wx.MessageDialog(self, "A shitty game to demonstrate our CRRRRAAAZZZYY networking skillzz",
              "About Rock, Paper, Scissors", wx.OK)
        d.ShowModal()
        d.Destroy()
    # File -> Exit, Exit button
    def OnExit(self, event):
        self.Close(True)

app = wx.PySimpleApp()
frame = MainWindow(None, -1, "Rock, Paper, Scissors")
#frame.Show(1)
app.MainLoop()
