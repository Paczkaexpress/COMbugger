import os
import wx
import serial.tools.list_ports
import io
import time
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy
from wxmplot import PlotApp
import wxmplot
from MenuItem import MenuItem
from wxmplot import ImageFrame
import wx.lib.plot as plot
from wxmplot import BaseFrame
from wxmplot import ImagePanel
ser = serial.Serial()
sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))
from matplotlib.backends.backend_wxagg import Toolbar, FigureCanvasWxAgg
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import \
    FigureCanvasWxAgg as FigCanvas, \
    NavigationToolbar2WxAgg as NavigationToolbar
import numpy as np
import pylab
import random


class DataGen(object):
    """ A silly class that generates pseudo-random data for
        display in the plot.
    """
    def __init__(self, init=50):
        self.dataTest = self.init = init
        
    def next(self):
        self._recalc_data()
        return self.dataTest
    
    def _recalc_data(self):
        delta = random.uniform(-0.5, 0.5)
        r = random.random()

        if r > 0.9:
            self.dataTest += delta * 15
        elif r > 0.8: 
            # attraction to the initial value
            delta += (0.5 if self.init > self.dataTest else -0.5)
            self.dataTest += delta
        else:
            self.dataTest += delta
            
class ReadCOMPort():
    def __init__(self,*args):
        pass
        self.COMData = 0
        self.newDataRead = False
        
    def readLine(self):
        while True:
            time.sleep(0.1)
            
            if ser.is_open == True:
                sio.flush() # it is buffering. required to get the data out *now*
                print("done")
                #self.COMData = sio.readline()
                self.COMData = ser.read()  
                self.newDataRead = True
                print(self.COMData) 
                
    def getValue(self):
        if self.newDataRead == True:
            newDataRead = False
            return self.COMData
    def isDataReady(self):
            return self.newDataRead
        
class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1000,800))

        self.panel = wx.Panel(self)
        
        bs_console = wx.BoxSizer(wx.HORIZONTAL)
        bs_connetion = wx.BoxSizer(wx.HORIZONTAL)
        bs_plot = wx.BoxSizer(wx.VERTICAL)
        bs_main = wx.BoxSizer(wx.HORIZONTAL)
        bs_window = wx.BoxSizer(wx.VERTICAL)
        
        self.terminalRawText = wx.TextCtrl(self.panel,size = (150,750),style = wx.TE_MULTILINE)
        self.terminalInterpretedText = wx.TextCtrl(self.panel,size = (300,750),style = wx.TE_MULTILINE)
        self.button1 = wx.Button(self.panel, label="Connect")
        self.button2 = wx.Button(self.panel, label="Disconnect")
        
        COMPort = [d.device for d in serial.tools.list_ports.comports()]
        self.COMPortList = wx.ComboBox(self.panel,choices = COMPort) 
        self.COMPortChoice = wx.Choice(self.panel,choices = COMPort)
        
        COMPortBaudrate = ["300", "1200", "2400", "4800", "9600", "14400", "19200", "28800", "38400", "57600" ,"115200" ,"230400"]
        self.COMPortBaudrateList = wx.ComboBox(self.panel,choices = COMPortBaudrate) 
        self.COMPortBaudrateChoice = wx.Choice(self.panel,choices = COMPortBaudrate)
        
        self.datagen = DataGen()
        self.dataTest = []
        
        self.create_figure()
        self.draw_plot()
        
        bs_main.Add(bs_window, 0)
        bs_main.Add(bs_plot, 0)
        bs_window.Add(bs_connetion, 0, wx.ALL|wx.EXPAND)
        bs_window.Add(bs_console, 0, wx.ALL|wx.EXPAND)
        bs_console.Add(self.terminalRawText, 1, wx.EXPAND)   
        bs_console.Add(self.terminalInterpretedText, 1, wx.EXPAND)  
        bs_connetion.Add(self.button1, 1)
        bs_connetion.Add(self.button2, 1)
        bs_connetion.Add(self.COMPortList, 1)
        bs_connetion.Add(self.COMPortBaudrateList, 1)
        bs_plot.Add(self.canvas, 1, flag=wx.LEFT | wx.TOP | wx.GROW)

        self.Layout()
        
        self.panel.SetSizer(bs_main)
        self.CreateStatusBar() # A StatusBar in the bottom of the window
        
        self.timer = wx.Timer(self)
        self.timer.Start(100)    # 1 second interval
        # Setting up the menu.
        self.createMenu()
        self.eventsMenu()
         
        self.Show(True)
        
        self.F = ReadCOMPort()
        self.thread = Thread(target=self.F.readLine,args=())
        self.thread.daemon = True
        self.thread.start()
    
    def createMenu(self):
        #File
        menuItemFile = wx.Menu()
        menuItemFile.Append(wx.ID_NEW, '&New')
        menuItemFile.AppendSeparator()  
        MenuItem(self, menuItemFile, 'COM Port', '', self.onTest)
        MenuItem(self, menuItemFile, 'Boudwith', '', self.onTest)
        MenuItem(self, menuItemFile, 'Save Image', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemFile, 'Copy', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemFile, 'Import Data', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemFile, 'Export Data', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemFile, 'Print', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemFile, 'Exit', 'Quick Reference for WXMPlot', self.onTest)
        
        
        #Setup
        menuItemSetup = wx.Menu()
        
        #Data
        menuItemData = wx.Menu()
        MenuItem(self, menuItemData, 'Set Limits', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemData, 'Record Data', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemData, 'Set Scale', 'Quick Reference for WXMPlot', self.onTest)

        #Image
        menuItemImage = wx.Menu()
        MenuItem(self, menuItemImage, 'Zoom Out', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemImage, 'Scale Horizontaly', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemImage, 'Scale Veritically', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemImage, 'Auto-scale', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemImage, 'Legend', 'Quick Reference for WXMPlot', self.onTest)
        MenuItem(self, menuItemImage, 'Freez', 'Quick Reference for WXMPlot', self.onTest)
        
        #help
        menuItemHelp= wx.Menu()
        MenuItem(self, menuItemHelp, 'About', 'About WXMPlot', self.onAbout)
        MenuItem(self, menuItemHelp, 'Help', 'About WXMPlot', self.onHelp)
        
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(menuItemFile,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(menuItemSetup,"&Setup") # Adding the "filemenu" to the MenuBar
        menuBar.Append(menuItemData,"&Data") # Adding the "filemenu" to the MenuBar
        menuBar.Append(menuItemImage,"&Image") # Adding the "filemenu" to the MenuBar
        menuBar.Append(menuItemHelp, "&Help")
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
    def eventsMenu(self):
        # Set events.
        self.Bind(wx.EVT_BUTTON, self.OnConnect, self.button1)
        self.Bind(wx.EVT_BUTTON, self.OnDisconnect, self.button2)
        self.Bind(wx.EVT_TIMER, self.UpdateTerminalData, self.timer)
        
    def onTest(self, e):
        dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.
        
    def onHelp(self, e):
        dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.
        
    def onAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "A small text editor", "About Sample Editor", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.
    
    def OnConnect(self,e):  
        if self.COMPortList.GetCurrentSelection() == -1 or self.COMPortBaudrateList.GetCurrentSelection() == -1:
            dlg = wx.MessageDialog( self, "Please choose COM port / boudrate", "Warrning", wx.OK)
            dlg.ShowModal() # Show it
            dlg.Destroy() # finally destroy it when finished.
            
        ser.port = self.COMPortList.GetString(self.COMPortList.GetCurrentSelection())
        ser.baudrate = int(self.COMPortBaudrateList.GetString(self.COMPortBaudrateList.GetCurrentSelection()))
        ser.open()
        ser.write(b'hello')
    
    def OnDisconnect(self,e):
        ser.close()
    
    def UpdateTerminalData(self, event):
        

                
        if self.F.isDataReady() == True:
            self.channel_oneData = self.F.getValue()
            self.dataTest.append(int(ord(self.channel_oneData)))
            #self.dataTest.append(self.datagen.next())
            self.draw_plot()
            try:
                self.channel_oneData = str(ord(self.channel_oneData))
                self.terminalRawText.WriteText(self.channel_oneData)
                self.terminalRawText.WriteText(' ')
                print(self.channel_oneData)
                print(' ')

                
            except:
                raise
            
            
    def init_plot(self):
        self.dpi = 100
        self.fig = Figure((4.0, 7.0), dpi=self.dpi)

        self.axes = self.fig.add_subplot(111)
        #self.axes.set_axis_bgcolor('black')
        self.axes.set_title('COM Port output', size=12)
        
        self.axes.set_xbound(-10, 50)
        self.axes.set_ybound(-50, 50)
        
        pylab.setp(self.axes.get_xticklabels(), fontsize=8)
        pylab.setp(self.axes.get_yticklabels(), fontsize=8)

        # plot the data as a line series, and save the reference 
        # to the plotted line series
        #
        #self.dataTest = []
        
        self.plot_data = self.axes.plot(
            self.dataTest, 
            linewidth=1,
            color=(0, 0, 1),
            )[0]
     
    def create_figure(self):

        self.init_plot()
        self.canvas = FigCanvas(self.panel, -1, self.fig)
        
    def draw_plot(self):
       
        
        xmax = len(self.dataTest) if len(self.dataTest) > 50 else 50
        #ymax = round(max(self.dataTest), 0) + 1
        ymax = 100
        self.axes.set_xbound(0, xmax)
        self.axes.set_ybound(0, ymax)
        
        self.plot_data.set_xdata(np.arange(len(self.dataTest)))
        self.plot_data.set_ydata(np.array(self.dataTest))
        
        self.canvas.draw()
        
app = wx.App(False)
frame = MainWindow(None, "Sample editor")
frame = ImageFrame(mode='intensity')
COMPort = [d.device for d in serial.tools.list_ports.comports()]

app.MainLoop()
