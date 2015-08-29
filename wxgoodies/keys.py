import wx, sys
from collections import OrderedDict

_tables = {} # Control:table pairs.
mods = OrderedDict() # List of modifiers.

if sys.platform == 'darwin':
 mods[wx.ACCEL_CTRL] = 'CMD'
 mods[wx.ACCEL_ALT] = 'OPT'
else:
 mods[wx.ACCEL_CTRL] = 'CTRL'
 mods[wx.ACCEL_ALT] = 'ALT'
mods[wx.ACCEL_SHIFT] = 'SHIFT'

def key_to_str(modifiers, key):
 """Returns a human-readable version of numerical modifiers and key."""
 if not key:
  key_str = 'NONE'
 else:
  key_str = None
 res = ''
 for value, name in mods.items():
  if (modifiers & value) == value:
   res += name + '+'
 for x in dir(wx):
  if x.startswith('WXK_'):
   if getattr(wx, x) == key:
    key_str = x[len('WXK_'):]
 if not key_str:
  key_str = chr(key)
 res += key_str
 return res

def str_to_key(value):
 """Turns a string like "CTRL_ALT+K" into (3, 75)."""
 modifiers = 0
 key = 0
 split = value.split('+')
 for v in split:
  a = 'ACCEL_%s' % v.upper()
  k = 'WXK_%s' % v.upper()
  if hasattr(wx, a):
   modifiers = modifiers | getattr(wx, a)
  elif hasattr(wx, k):
   if key:
    raise ValueError('Multiple keys specified.')
   else:
    key = getattr(wx, k)
 if not key:
  key = ord(split[-1])
 return (modifiers, key)

def add_accelerator(control, key, func, id = None):
 """
 Adds a key to the control.
 
 control: The control that the accelerator should be added to.
 key: A string like "CTRL+F", or "CMD+T" that specifies the key to use.
 func: The function that should be called when key is pressed.
 id: The id to Bind the event to. Defaults to wx.NewId().
 """
 if id == None:
  id = wx.NewId()
 control.Bind(wx.EVT_MENU, func, id = id)
 t = _tables.get(control, [])
 modifiers, key_int = str_to_key(key)
 t.append((modifiers, key_int, id))
 _tables[control] = t
 update_accelerators(control)

def remove_accelerator(control, key):
 """
 Removes an accelerator from control.
 
 control: The control to affect.
 key: The key to remove.
 """
 key = str_to_key(key)
 t = _tables.get(control, [])
 for a in t:
  if a[:2] == key:
   t.remove(a)
   _tables[control] = t
   update_accelerators(control)
   return True
 return False

def update_accelerators(control):
 """Update the accelerator table for control."""
 control.SetAcceleratorTable(wx.AcceleratorTable(_tables.get(control, [])))

