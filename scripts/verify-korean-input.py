#!/usr/bin/python3
"""Verify actual Hangul composition through the live IBus engine."""
import os
import time
import sys
os.environ['IBUS_ADDRESS'] = f'unix:abstract=wsl-notes-ibus-{os.getuid()}'
import gi
gi.require_version('IBus', '1.0')
from gi.repository import IBus, GLib

IBus.init()
bus = IBus.Bus.new()
assert bus.is_connected(), 'IBus is disconnected'
context = bus.create_input_context('wsl-notes-korean-verification')
committed = []
context.connect('commit-text', lambda _, text: committed.append(text.get_text()))
context.set_capabilities(IBus.Capabilite.PREEDIT_TEXT | IBus.Capabilite.FOCUS)
context.focus_in()
context.set_engine('hangul')

def drain():
    end = time.monotonic() + 0.15
    while time.monotonic() < end:
        while GLib.MainContext.default().iteration(False):
            pass
        time.sleep(0.005)

drain()
assert context.get_engine().get_name() == 'hangul'
# Ensure Latin mode, then exercise the configured Shift+Space toggle.
context.process_key_event(IBus.KEY_Escape, 0, 0)
toggle = sys.argv[1] if len(sys.argv) > 1 else 'Shift+Space'
if toggle == 'Alt_R':
    context.process_key_event(IBus.KEY_Alt_R, 108 - 8, 0)
    context.process_key_event(IBus.KEY_Alt_R, 108 - 8,
                              IBus.ModifierType.MOD1_MASK | IBus.ModifierType.RELEASE_MASK)
elif toggle == 'Hangul':
    context.process_key_event(IBus.KEY_Hangul, 130 - 8, 0)
    context.process_key_event(IBus.KEY_Hangul, 130 - 8, IBus.ModifierType.RELEASE_MASK)
else:
    context.process_key_event(IBus.KEY_space, 0, IBus.ModifierType.SHIFT_MASK)
for char in 'gksrmf':
    context.process_key_event(ord(char), 0, 0)
    context.process_key_event(ord(char), 0, IBus.ModifierType.RELEASE_MASK)
context.process_key_event(IBus.KEY_space, 0, 0)
drain()
result = ''.join(committed)
assert result.strip() == '한글', repr(result)
context.focus_out()
context.destroy()
print(f'PASS: {toggle} + gksrmf → {result.strip()} (live IBus composition)')
