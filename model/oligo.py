import styles
from styles import bright_palette as sharedPalette

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

