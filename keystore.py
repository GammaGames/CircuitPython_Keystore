# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2022 Jesse Lieberg
#
# SPDX-License-Identifier: MIT
"""
`keystore`
================================================================================

CircuitPython helper library to store data to a microcontroller's internal storage


* Author(s): Jesse Lieberg

Implementation Notes
--------------------

**Hardware:**

Tested with the RP2040 Feather

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads
"""

import storage
import os
import digitalio
import json


class Keystore:
    """The object that manages the file and attributes for the object

    :param string filename: path of the keystore file. Default: `/.config`
    :param microcontroller.Pin pin: connect this pin to ground to save the config to storage
    :param boolean _debug: enable `print` debug information
    :param kwargs: keys to store with their defaults
    """
    def __init__(self, filename="/.config", pin=None, _debug=False, **kwargs):
        self._debug = _debug  # Use underscore to still allow users to store "debug"
        self._persistent = False
        self._dirty = False
        self._filename = filename
        path = self._filename.split(os.sep)
        self._file = path.pop()
        self._path = os.sep.join(path) + os.sep
        self._storage_pin = pin

        self._default = dict(kwargs)
        self._store = dict(kwargs)
        for key, value in self._store.items():
            setattr(self, key, value)

        self._remount_storage()
        self._load()

    @property
    def is_persistent(self):
        return self._persistent

    @property
    def is_dirty(self):
        return self._dirty


    def _remount_storage(self):
        def _remount(ro):
            try:
                storage.remount("/", ro)
                self._persistent = not ro
            except:
                self._print("Mounted via USB, not remounting storage")

        if self._storage_pin is None:
            self._print("Pin must be provided as a safety precaution.")
            self._print(
                "https://learn.adafruit.com/circuitpython-essentials/circuitpython-storage"
            )
            self._print("To bypass this check, pass the pin as `False`")
        elif self._storage_pin is False:
            _remount(False)
        else:
            switch = digitalio.DigitalInOut(self._storage_pin)
            switch.switch_to_input(pull=digitalio.Pull.UP)
            _remount(switch.value)

    def _print(self, *args):
        if self._debug:
            print(*args)

    def set(self, **kwargs):
        for key, value in kwargs.items():
            self._store[key] = value
            setattr(self, key, value)
        self._dirty = True

    def remove(self, *args):
        for key in args:
            try:
                del self._store[key]
                delattr(self, key)
            except KeyError:
                pass
        self._dirty = True

    def save(self, **kwargs):
        self.set(**kwargs)
        try:
            with open(self._filename, "w") as out_file:
                out_file.write(json.dumps(self._store))
        except Exception:
            self._print(f"Error writing to {self._filename}")

        self._dirty = False

    def _load(self):
        if self._file in os.listdir(self._path):
            with open(self._filename, "r") as in_file:
                self._store = json.loads(in_file.read())
            for key, value in self._store.items():
                if key in self._default:
                    setattr(self, key, value)
                else:
                    del(self._store[key])
        else:
            self._print(f"File does not exist: {self._filename}")

    def print(self):
        print(f"Filename: {self._filename}")
        for key, value in self._store.items():
            print(f"{key}: {value}")
        if self._dirty:
            print("File is dirty")
        if not self._persistent:
            print("Storage is not persistent")
