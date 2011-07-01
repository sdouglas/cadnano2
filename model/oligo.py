import styles

class Oligo(QObject):
    """
    Model 2.0: DNAPart >> Oligo >> Segments
    Oligo is comprised of a list of segments under the invariant
    segments(i).next3() == segments(i+1).prev5()
    """
	
	def __init__(self):
	    QObject.__init__(self)
	    self._sequence = ""
	    self._segments = []
	    self._color = None
	    self._sequence = None
	
	########################## Notification API ##########################

    # Args are oligo, segment, index
	oligoWillAddSegmentAtIndex = pyqtSignal(object, int)
	# Args are oligo, segment
	oligoDidAddSegment = pyqtSignal(object, object)

    # Args are oligo, segment
	oligoWillRemoveSegment = pyqtSignal(object, object)
	# Args are oligo, segment
	oligoDidRemoveSegment = pyqtSignal(object, object)

    # Arg is oligo
    oligoColorDidChange = pyqtSignal(object)
    oligoSequenceDidChange = pyqtSignal(object)
	
	########################## Public Read API ##########################

	def segments(self, i=None):
	    """
	    Returns the segments self is composed of in 5' to 3' order (that
	    is, self.segments()[0] should have no prev5() and self.segments()[-1]
	    should have no next3())
	    """
	    if i != None:
	        return self._segments[i]
	    return self._segments

    def length(self):
        """
        Every change in length should correspond to a
        """
        return sum(seg.length() for seg in self._segments)

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

	def addSegment(self, newSeg, idx=False):
	    """
	    Adds a segment to self's segment list such that
	    self.segments()[idx] = newSeg
	    """
	    if idx == False:
	        idx = len(self._segments)
	    assert(newSeg not in self._segments)
	    assert(newSeg.oligo() == None)
	class AddSegmentCommand(QUndoCommand):
	    def __init__(self, oligo, seg, idx):
	        self._oligo = oligo
	        self._seg = seg
	        self._idx = idx
	    def redo(self):
	        oligo, seg, idx = self._oligo, self._seg, self._idx
	        oligo.oligoWillAddSegmentAtIndex.emit(oligo, seg, idx)
	        oligo._segments.insert(idx, seg)
	        newSeg._setOligo(self)
	        self.oligoDidAddSegment(self, newSeg)

    def removeSegment(self, seg):
        """
        Removes a segment
        """
        assert(seg in self._segments)
        self.oligoWillRemoveSegment(self, seg)
        self._segments.remove(seg)
        seg._setOligo(None)
        self.oligoDidRemoveSegment(self, seg)

    ########################## Private Write API ##########################

    def _setPart(self, newPart):
        self._part = newPart

    ########################## Bookkeeping ##########################

    def fsck(self):
        """
        Returns True if self obeys all the invariants it should.
        Prints messages helpful to debugging if it doesn't.
        """
        segs = self.segments():
        if segs:
            if segs[0].prev5() != None:
                print "Segment 0 of %s has illegal 5' ptr"%self
                return False
            if segs[-1].next3() != None:
                print "Last segment of %s has illegal 3' ptr"%self
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