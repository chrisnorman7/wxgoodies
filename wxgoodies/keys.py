"""Hotkey-related routines."""

import wx, sys, logging
try:
 import win32con
except ImportError:
 win32con = None # Not available on this system.
from collections import OrderedDict

logger = logging.getLogger(__name__)

_tables = {} # Control:table pairs.
_hotkeys = {} # control: [hotkey, id] pairs.

mods = OrderedDict() # List of modifiers.
global_mods = OrderedDict()
converts = OrderedDict() # Give command keys their proper names.

logger.debug('Creating command keys.')
if sys.platform == 'darwin':
 logger.debug('OS X detected.')
 mods[wx.MOD_CONTROL] = 'CMD'
 mods[wx.MOD_ALT] = 'OPT'
 # Don't bother with global hotkeys... They don't work on OS X anyways.
 converts['WXK_CONTROL'] = 'CMD'
 converts['WXK_RAW_CONTROL'] = 'CTRL'
 converts['WXK_ALT'] = 'OPT'
else:
 logger.debug('%s detected.', sys.platform.title())
 mods[wx.MOD_CONTROL] = 'CTRL'
 mods[wx.MOD_ALT] = 'ALT'
 if win32con:
  global_mods[win32con.MOD_CONTROL] = 'CTRL'
  global_mods[win32con.MOD_ALT] = 'ALT'
 converts['WXK_CONTROL'] = 'CTRL'
 converts['WXK_RAW_CONTROL'] = 'CTRL'
converts['VK_CONTROL'] = 'CTRL'
converts['VK_SHIFT'] = 'SHIFT'
converts['VK_ALT'] = 'ALT'
mods[wx.MOD_SHIFT] = 'SHIFT'
if win32con:
 global_mods[win32con.MOD_SHIFT] = 'SHIFT'

def key_to_str(modifiers, key, mods_table = mods, key_table = wx, key_prefix = 'WXK_'):
 """
 Returns a human-readable version of numerical modifiers and key.
 
 To make the key suitable for global hotkey usage, supply:
 mods_table = global_mods, key_table = win32con, key_prefix = 'VK_'
 """
 logger.debug('Converting (%s, %s) to string.', modifiers, key)
 if not key:
  key_str = 'NONE'
 else:
  key_str = None
 res = ''
 for value, name in mods_table.items():
  if (modifiers & value):
   res += name + '+'
 for x in dir(key_table):
  if x.startswith(key_prefix):
   if getattr(key_table, x) == key:
    key_str = converts.get(x, x[len(key_prefix):])
 if not key_str:
  key_str = chr(key)
 res += key_str
 return res

def str_to_key(value, key_table = wx, accel_format = 'ACCEL_%s', key_format = 'WXK_%s', key_transpositions = {}):
 """
 Turns a string like "CTRL_ALT+K" into (3, 75).
 
 To get a global hotkey, try passing:
 key_table = win32con, accel_format = 'MOD_%s', key_format = 'VK_%s', key_transpositions = {'CTRL': 'CONTROL'}
 """
 logger.debug('Converting "%s" to integers.', value)
 modifiers = 0
 key = 0
 split = value.split('+')
 for v in split:
  v = v.upper()
  a = accel_format % key_transpositions.get(v, v)
  logger.debug('Accelerator format = %s.', a)
  k = key_format % key_transpositions.get(v, v)
  logger.debug('Key format = %s.', k)
  if hasattr(key_table, a):
   logger.debug('Found accelerator on %r.', key_table)
   modifiers = modifiers | getattr(key_table, a)
  elif hasattr(key_table, k):
   logger.debug('Found key on %r.', key_table)
   if key:
    raise ValueError('Multiple keys specified.')
   else:
    key = getattr(key_table, k)
 if not key:
  logger.debug('No key yet, falling back to ord.')
  key = ord(split[-1])
 return (modifiers, key)

def get_id(id):
 """Get a new id if the provided one is None."""
 if id == None:
  id = wx.NewId()
  logger.debug('Generated new ID %s.', id)
 else:
  logger.debug('Using provided id %s.', id)
 return id

def add_accelerator(control, key, func, id = None):
 """
 Adds a key to the control.
 
 control: The control that the accelerator should be added to.
 key: A string like "CTRL+F", or "CMD+T" that specifies the key to use.
 func: The function that should be called when key is pressed.
 id: The id to Bind the event to. Defaults to wx.NewId().
 """
 logger.debug('Adding key "%s" to control %s to call %s.', key, control, func)
 id = get_id(id)
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
   if t:
    _tables[control] = t
   else:
    del _tables[control]
   update_accelerators(control)
   return True
 return False

def add_hotkey(control, key, func, id = None):
 """
 Add a global hotkey bound to control via id that should call func.
 
 control: The control to bind to.
 key: The hotkey to use.
 func: The func to call.
 id: The new ID to use (defaults to creating a new ID.
 """
 if win32con is None:
  raise RuntimeError('win32con is not available.')
 logger.debug('Adding hotkey "%s" to control %s to call %s.', key, control, func)
 modifiers, keycode = str_to_key(key, key_table = win32con, accel_format = 'MOD_%s', key_format = 'VK_%s', key_transpositions = {'CTRL': 'CONTROL'})
 id = get_id(id)
 control.Bind(wx.EVT_HOTKEY, func, id = id)
 l = _hotkeys.get(control, [])
 l.append([key, id])
 _hotkeys[control] = l
 return control.RegisterHotKey(id, modifiers, keycode)

def remove_hotkey(control, key):
 """
 Remove a global hotkey.
 
 control - The control to affect
 key - The key to remove.
 """
 l = _hotkeys.get(control, [])
 for a in l:
  key_str, id = a
  if key_str == key:
   control.Unbind(wx.EVT_HOTKEY, id = id)
   control.UnregisterHotKey(id)
   l.remove(a)
   if l:
    _hotkeys[control] = l
   else:
    del _hotkeys[control]
 
def update_accelerators(control):
 """Update the accelerator table for control."""
 control.SetAcceleratorTable(wx.AcceleratorTable(_tables.get(control, [])))
