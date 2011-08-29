import styles

class Oligo(QObject):
    """
    Model 2.0: DNAPart >> Oligo >> Strands
    Oligo is comprised of a list of strands under the invariant
    strands(i).next3() == strands(i+1).prev5()
    """
    
    def __init__(self):
        QObject.__init__(self)
        self._sequence = ""
        self._color = None

    ########################## Notification API ##########################

    # Args are oligo, strand, index
    oligoWillAddStrandAtIndex = pyqtSignal(object, int)
    # Args are oligo, strand
    oligoDidAddStrand = pyqtSignal(object, object)

    # Args are oligo, strand
    oligoWillRemoveStrand = pyqtSignal(object, object)
    # Args are oligo, strand
    oligoDidRemoveStrand = pyqtSignal(object, object)

    # Arg is oligo
    oligoColorDidChange = pyqtSignal(object)
    oligoSequenceDidChange = pyqtSignal(object)
    
    ########################## Public Read API ##########################

    def strands(self, i=None):
        """
        Returns the strands self is composed of in 5' to 3' order (that
        is, self.strands()[0] should have no prev5() and self.strands()[-1]
        should have no next3())
        """
        if i != None:
            return self._strands[i]
        return self._strands

    def length(self):
        """
        Every change in length should correspond to a
        """
        return sum(seg.length() for seg in self._strands)

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

    def addStrand(self, newSeg, idx=False):
        """
        Adds a strand to self's strand list such that
        self.strands()[idx] = newSeg
        """
        if idx == False:
            idx = len(self._strands)
        assert(newSeg not in self._strands)
        assert(newSeg.oligo() == None)
    class AddStrandCommand(QUndoCommand):
        def __init__(self, oligo, seg, idx):
            self._oligo = oligo
            self._seg = seg
            self._idx = idx
        def redo(self):
            oligo, seg, idx = self._oligo, self._seg, self._idx
            oligo.oligoWillAddStrandAtIndex.emit(oligo, seg, idx)
            oligo._strands.insert(idx, seg)
            newSeg._setOligo(self)
            self.oligoDidAddStrand(self, newSeg)

    def removeStrand(self, seg):
        """
        Removes a strand
        """
        assert(seg in self._strands)
        self.oligoWillRemoveStrand(self, seg)
        self._strands.remove(seg)
        seg._setOligo(None)
        self.oligoDidRemoveStrand(self, seg)

    ########################## Private Write API ##########################

    def _setPart(self, newPart):
        """ Should only be called by newPart itself """
        self._part = newPart

    ########################## Bookkeeping ##########################

    def fsck(self):
        """
        Returns True if self obeys all the invariants it should.
        Prints messages helpful to debugging if it doesn't.
        """
        segs = self.strands():
        if segs:
            if segs[0].prev5() != None:
                print "Strand 0 of %s has illegal 5' ptr"%self
                return False
            if segs[-1].next3() != None:
                print "Last strand of %s has illegal 3' ptr"%self
                return False
        for i in range(0, len(segs) - 1):
            if segs[i].next3() != segs[i + 1].prev5():
                print "Doubly Linked List condition of %s broken; %i.3 != %i.5"%(i, i+1)
                return False
        return True

    def palette(self):
        if self.part():
            return self.part().palette()
        return styles.default_palette