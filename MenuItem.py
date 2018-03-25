import wx
import sys
import matplotlib
from matplotlib.path import Path

def MenuItem(parent, menu, label='', longtext='', action=None, **kws):
    """Add Item to a Menu, with action
    m = Menu(parent, menu, label, longtext, action=None)
    """
    wid = wx.NewId()
    item = menu.Append(wid, label, longtext, **kws)
    if callable(action):
        parent.Bind(wx.EVT_MENU, action, item)
    return item