#!/usr/bin/env python
import wx
import random

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()

names = ["Finn", "JP", "Proly A Hacker", "`; DROP TABLE players;", "player1", "quickjp1", "quickjp2", "quickjp3"]

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (400, 200),
          style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)


        # Build a player list
        self.playerList = wx.ListCtrl(self, id, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.playerList.Show(True)
        self.playerList.InsertColumn(0, "Name")
        self.playerList.InsertColumn(1, "Score")

        # Populate the player list with BS data
        for i in range(0, random.randint(2,10)):
            name = random.choice(names)
            line = self.playerList.InsertStringItem(0, name)
            self.playerList.SetStringItem(line, 1, str(random.randint(0,500)))
        # Create a status bar
        self.CreateStatusBar()
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

        # Make the sizers
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.buttons = {}
        for i in ["Invite to play", "Exit"]:
            self.buttons[i] = wx.Button(self, -1, i)
            self.sizer.Add(self.buttons[i], 1, wx.EXPAND)

        self.outerSizer = wx.BoxSizer(wx.VERTICAL)
        self.outerSizer.Add(self.playerList, 1, wx.EXPAND)
        self.outerSizer.Add(self.sizer, 0, wx.EXPAND)

        self.SetSizer(self.outerSizer)
        self.SetAutoLayout(1)
        self.outerSizer.Fit(self)

        # Show the window
        self.Show()

    def OnAbout(self, event):
        d = wx.MessageDialog(self, "A shitty game to demonstrate our CRRRRAAAZZZYY networking skillzz",
              "About Rock, Paper, Scissors", wx.OK)
        d.ShowModal()
        d.Destroy()

    def OnExit(self, event):
        self.Close(True)

app = wx.PySimpleApp()
frame = MainWindow(None, -1, "Rock, Paper, Scissors")
#frame.Show(1)
app.MainLoop()
