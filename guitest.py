#!/usr/bin/env python
import wx

ID_ABOUT = wx.NewId()
ID_EXIT  = wx.NewId()

class MainWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size = (400, 200),
          style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.control = wx.TextCtrl(self, 1, style = wx.TE_MULTILINE)
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
        for i in ["List players", "Play a game", "Exit", "Do the other thing"]:
            self.buttons[i] = wx.Button(self, -1, i)
            self.sizer.Add(self.buttons[i], 1, wx.EXPAND)

        self.outerSizer = wx.BoxSizer(wx.VERTICAL)
        self.outerSizer.Add(self.control, 1, wx.EXPAND)
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
