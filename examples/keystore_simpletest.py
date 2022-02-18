from keystore import Keystore

config = Keystore("/.conf", pin=False, foo="bar", baz=3)
foo, bar = config.foo, config.baz

config.print()
