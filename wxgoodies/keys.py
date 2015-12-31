"""Hoekey-related routines."""

import wx, sys, logging
from collections import OrderedDict

logger = logging.getLogger(__name__)

_tables = {} # Control:table pairs.
mods = OrderedDict() # List of modifiers.
converts = OrderedDict() # Give command keys their proper names.

logger.debug('Creating command keys.')
if sys.platform == 'darwin':
 logger.debug('OS X detected.')
 mods[wx.MOD_CONTROL] = 'CMD'
 mods[wx.MOD_ALT] = 'OPT'
 converts['WXK_CONTROL'] = 'CMD'
 converts['WXK_RAW_CONTROL'] = 'CTRL'
 converts['WXK_ALT'] = 'OPT'
else:
 logger.debug('%s detected.', sys.platform.title())
 mods[wx.MOD_CONTROL] = 'CTRL'
 mods[wx.MOD_ALT] = 'ALT'
 converts['WXK_RAW_CONTROL'] = 'CTRL'
 converts['WXK_RAW_CONTROL'] = 'CTRL'
mods[wx.MOD_SHIFT] = 'SHIFT'

def key_to_str(modifiers, key):
 """Returns a human-readable version of numerical modifiers and key."""
 logger.debug('Converting (%s, %s) to string.', modifiers, key)
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
    key_str = converts.get(x, x[len('WXK_'):])
 if not key_str:
  key_str = chr(key)
 res += key_str
 return res

def str_to_key(value):
 """Turns a string like "CTRL_ALT+K" into (3, 75)."""
 logger.debug('Converting "%s" to integers.', value)
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
 logger.debug('Adding key "%s" to control %s to cal %s.', key, control, func)
 if id == None:
  id = wx.NewId()
  logger.debug('Generated new ID %s.', id)
 else:
  logger.debug('Using provided id %s.', id)
 control.Bind(wx.EVT_MENU, func, id = id)
 t = _tables.get(control, [])
 modifiers, key_int = str_to_key(key)
 t.append((modifiers, key_int, id))
 _tables[control] = t
 update_accelerators(control)
 return id

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

