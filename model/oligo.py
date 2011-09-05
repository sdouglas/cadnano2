import util
from views import styles
from views.styles import bright_palette as sharedPalette
from random import Random
util.qtWrapImport('QtCore', globals(), ['QObject', 'pyqtSignal'] )

class Oligo(QObject):
    """
    Model 2.0: DNAPart >> Oligo >> Strands
    Oligo is comprised of a list of strands under the invariant
    strands(i).next3() == strands(i+1).prev5()
    """
    
    def __init__(self):
        QObject.__init__(self)
        self._sequence = ""
        # We're going to need a more sophisticated way of acquiring colors.
        # Since tools work by undo/redo every time the proposed operation
        # changes, each redo must assign colors in the same order the previous
        # redo assigned colors in order to prevent the rainbow effect.
        # The mechanism this used to work with was via a palette:
        # each redo would get colors via palette[0], palette[1], etc.
        # The colors in the palette wouldn't change between redo steps, so
        # colors were consistently assigned and the rainbow effect was avoided.
        # Then, when the "drag operation" (the old model didn't actually have
        # an explicit concept of a drag operation) completed, the palette would
        # be palette.shuffle()d so that the next drag operation would have
        # novel colors.
        self._color = sharedPalette.pop()
        self._5pstrand = None  # End of the linked list that has an exposed 5'

    ########################## Notification API ##########################

    # Arg is oligo
    oligoColorDidChange = pyqtSignal(object)
    oligoSequenceDidChange = pyqtSignal(object)

    ########################## Public Read API ##########################

    def length(self):
        """
        Every change in length should correspond to a
        """
        strand, total = self._5pstrand, 0
        while strand != None:
            total += strand.length()
            strand = strand.conn3()
        return total

    def color(self):
        if self._color == None:
            return self.palette().pop()
        return self._color

    def sequence(self):
        return self._sequence

    ########################## Public Write API ##########################

    def setColor(self, newColor):
        self._color = newColor
        self.oligoColorDidChange(self)

    def setSequence(self, newSeq):
        self._sequence = newSeq
        self.oligoSequenceDidChange(self)

class RainbowOligoProvider(object):
    """ Doesn't respect drag sessions, just lets the default (random) color
    of the newly created oligo become its official color. During a drag session,
    this causes a newly created oligo to get a different color every time the
    drag operation pushes / pops (which happens whenever the mouse moves or
    base changes), thus creating the eponymous rainbow effect. """
    def getOligo(self):
        return Oligo()
class DragOperationOligoProvider(object):
    """ Ensures that two consecutive similar actions result in assigning similar
    colors to any new oligos that get created, defeating the rainbow effect. """
    def __init__(self):
        self.returnedOligos = []
        self.nextIdx = 0
    def getOligo(self):
        nextIdx = self.nextIdx
        if nextIdx < len(self.returnedOligos):
            self.nextIdx = nextIdx + 1
            return self.returnedOligos[nextIdx]
        newOligo = Oligo()
        self.returnedOligos.append(newOligo)
        self.nextIdx = len(self.returnedOligos)
        return newOligo
    def rewind(self):
        self.nextIdx = 0
defaultOligoProvider = RainbowOligoProvider()