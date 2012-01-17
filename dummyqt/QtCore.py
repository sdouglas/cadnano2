QObject = object

class Qt(object):
    pass

class pyqtSignal(object):
    def __init__(self, *args):
        """ We don't actually do anything with argtypes because
        the real Qt will perform checks in the Gui version of
        cadnano which should suffice. """
        self.argtypes = args
        self.targets = set()
    def connect(self, target):
        self.targets.add(target)
    def disconnect(self, target):
        self.targets.remove(target)
    def emit(self, *args):
        for t in self.targets:
            t(*args)