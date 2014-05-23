#!/usr/bin/env python
import wx
import random
import socket
import json
import logging

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()

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

        self.SetAutoLayout(1)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        # Show the window
        self.Show()

        self.connect("127.0.0.1", 22066)
        self.register()

        #self.listPlayers()

    def listPlayers(self):
        self.sock.sendall(json.dumps({'action':'list'}))
        response = json.loads(self.sock.recv(1024))


        # Build a player list
        self.playerList = wx.ListCtrl(self, self.id, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.playerList.Show(True)
        self.playerList.InsertColumn(0, "Name")
        self.playerList.InsertColumn(1, "Score")

        if "list" in response:
            for player in response['list']:
                line = self.playerList.InsertStringItem(0, player['name'])
                self.playerList.SetStringItem(line, 1, str(player['score']))

        # Make the sizers
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = {}
        for i in ["Invite to play", "Exit"]:
            self.buttons[i] = wx.Button(self, -1, i)
            self.buttonSizer.Add(self.buttons[i], 1, wx.EXPAND)

        self.sizer.Add(self.playerList, 1, wx.EXPAND)
        self.sizer.Add(self.sizer, 0, wx.EXPAND)
        self.sizer.Fit(self)
        self.SetSizer(self.sizer)

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


    # Register with the server (prompt the user for a name and send it)
    def register(self, error=None):
        self.sizer.DeleteWindows()
        self.registratonTextBox = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
        if error is not None:
            errorLabel = wx.StaticText(self, label=error)
            errorLabel.SetForegroundColour((255,0,0))
            errorFont = wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.NORMAL, wx.BOLD)
            errorLabel.SetFont(errorFont)
            self.sizer.Add(errorLabel)
        label = wx.StaticText(self, label="Please tell the server your name:")
        gobtn = wx.Button(self, -1, "Register")
        self.sizer.Add(label, 0)
        self.sizer.Add(self.registratonTextBox, 1, wx.EXPAND)
        self.sizer.Add(gobtn, 2)
        self.sizer.Fit(self)

        self.Bind(wx.EVT_BUTTON, self.OnRegister, gobtn)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnRegister, self.registratonTextBox)

    # Registration Callback function
    def OnRegister(self, event):
        logging.debug("Registering with server...")
        name = self.registratonTextBox.GetLineText(0)
        logging.info("Registering as %s", name)
        self.sock.send(json.dumps({"action": "register", "name": name}))
        rawresponse = self.sock.recv(1024).strip()
        logging.debug("Received back %s", rawresponse)
        registrationSuccessful = False
        errorMsg = None
        try:
            response = json.loads(rawresponse)
            if "result" in response:
                if response["result"] == "success":
                    logging.info("Successfully registered!")
                    if "clientid" in response:
                        self.clientid = response["clientid"]
                        registrationSuccessful = True
                    else:
                        errorMsg = "No clientid recieved. Weird, trying again..."
                        logging.warning("No client ID received. Trying again.")
                elif response["result"] == "error":
                    if "excuse" in response:
                        errorMsg = "Failed to register: %s" % response['excuse']
                        logging.warning("Failed to register. Excuse: %s", response['excuse'])
                    else:
                        errorMsg = "Failed to register (unknown reason)"
                        logging.warning("Failed to register, no excuse given")
                else:
                    errorMsg = "Unrecognized result from server: %s" % response['result']
                    logging.warning("Unrecognized result from server: %s", response['result'])
        except ValueError:
            logging.warning("Failed to parse %s", rawresponse)
            errorMsg = "Received unreadable message from the server :("
            print rawresponse
        if registrationSuccessful:
            self.listPlayers()
        else:
            self.register(errorMsg)


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
