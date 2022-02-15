"""
`keystore`
====================================================

A simple keystore object useful for storing
config files to storage

* Author(s): Jesse Lieberg
"""

import storage
import os
import digitalio


class Keystore:
    """"""

    def __init__(self, filename="/.config", pin=None, _debug=False, **kwargs):
        self._debug = _debug  # Use underscore to still allow users to store "debug"
        self._persistent = False
        self._dirty = False
        self._filename = filename
        path = self._filename.split(os.sep)
        self._file = path.pop()
        self._path = os.sep.join(path) + os.sep
        self._storage_pin = pin

        self._store = dict(kwargs)
        for key, value in self._store.items():
            setattr(self, key, value)

        self._remount_storage()
        self._load()

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
                for key, value in self._store.items():
                    out_file.write(f"{key}={value}\n")
        except Exception:
            self._print(f"Error writing to {self._filename}")

        self._dirty = False

    def _load(self):
        if self._file in os.listdir(self._path):
            with open(self._filename, "r") as in_file:
                for line in in_file.read().strip().split("\n"):
                    parts = line.split("=")
                    key = parts.pop(0)
                    value = "=".join(parts)
                    self._store[key] = value
                    setattr(self, key, value)
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
