#!/usr/bin/env python
import wx
import random
import socket
import json
import logging
import threading

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()
ID_REGISTRATION_SUCCESSFUL = wx.NewId()

# Events
class RegistrationSuccessEvent(wx.PyEvent):
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class RegistrationErrorEvent(wx.PyEvent):
    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data

class SocketThread(threading.Thread):
    """A thread to interact with the socket without blocking the GUI"""
    def __init__(self, notify_window, hostname, port):
        threading.Thread.__init__(self)
        self.notify_window = notify_window
        self.wants_abort = False
        self.connect(hostname, port)
        self.start()

    def receive(self):
        rawmsg = self.sock.recv(4096).strip()
        try:
            msg = json.loads(rawmsg)
            logging.debug("Received: %s" % json.dumps(msg))
        except ValueError:
            logging.error("Unreadable JSON received from server: %s" % rawmsg)
        return msg

    def send(self, action, args = {}):
        logging.info("Sending %s command: %s" % (action, json.dumps(args)))
        args['action'] = action
        self.sock.send(json.dumps(args))

    # Connect to a host and port
    def connect(self, hostname, port):
        # Eventually, we should loop through all results and use the first one that
        # works, but for now
        server = socket.getaddrinfo(hostname, port)[0]
        logging.debug("Connecting to %s:%d", server[4][0], server[4][1])

        # server[0] will have the socket family (ie INET or INET6)
        self.sock = socket.socket(server[0], socket.SOCK_STREAM)

        # server[4] is a tuple in form (ip, port)
        self.sock.connect(server[4])

    def register(self, name):
        self.send("register", {"name": name})
        response = self.receive()
        registrationSuccessful = False
        errorMsg = None
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
        else:
            logging.error("Did not receive a result from the server: %s" % response)
        if registrationSuccessful:
            wx.PostEvent(self.notify_window, RegistrationSuccessEvent)
            self.listPlayers()
        else:
            wx.PostEvent(self.notify_window, RegistrationErrorEvent)

    def run(self):
        """Run Worker Thread."""
        while not self.wants_abort:
            msg = self.receive()


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

        self.socket = SocketThread(self, "127.0.0.1", 22066)
        self.register()

        # self.listPlayers()

    def listPlayers(self):
        self.sizer.DeleteWindows()
        self.socket.send("list")
        response = self.socket.receive()


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
        buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        buttons = {}
        for i in ["Invite to play", "Exit"]:
            buttons[i] = wx.Button(self, -1, i)
            buttonSizer.Add(buttons[i], 1, wx.EXPAND)



        self.sizer.Add(self.playerList, 1, wx.EXPAND)
        self.sizer.Add(buttonSizer, 0, wx.EXPAND)
        self.sizer.Fit(self)


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
        self.sizer.DeleteWindows()
        self.sizer.Add(wx.StaticText(self, label="Registering as %s..." % name))
        self.socket.register(name)


    # Menu Events ###
    # File -> About
    def OnAbout(self, event):
        d = wx.MessageDialog(self, "A shitty game to demonstrate our CRRRRAAAZZZYY networking skillzz",
              "About Rock, Paper, Scissors", wx.OK)
        d.ShowModal()
        d.Destroy()

    # File -> Exit, Exit button
    def OnExit(self, event):
        self.Close(True)

if __name__ == "__main__":
    # First, configure the logger to dump to client.log
    logformat = "[%(asctime)s][%(levelname)s] %(message)s"
    logging.basicConfig(filename="client.log", level=logging.DEBUG, format=logformat)
    app = wx.App(False)
    frame = MainWindow(None, -1, "Rock, Paper, Scissors")
    app.MainLoop()
