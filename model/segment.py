class Segment(QObject):
    """
    Represents a segment of DNA that
    1) Has a length (# nucleotides, possibly 0)
    2) Has a 3' and 5' endpoint (VBase instances, which locate the
       endpoints in conceptual or 3D space (like coordinates))
    3) The set of vhelix which contain bases of the segment
       is a nonproper subset of {startVB.vHelix(), endVB.vHelix()}
    4) Might have another segment connected to either or both of
       its 3' and 5' ends
    Represens a horizontal (in the path view) stretch of connected
    bases
    """

    def __init__(self, VB3p, VB5p):
        assert(VB3p.vStrand() == endVB.vStrand())
        # Location of the first base that belongs to self
        # with a 3' connection to the previous segment
        # (VBases are like coordinates in that they specify
        # the location of a base)
        self._3pVBase = VB3p
        self._3pSegment = None
        
        # Location of the last base that belongs to self
        # with a 5' connection to the next segment
        self._5pVBase = VB5p
        self._5pSegment = None

    def length(self):
        if self._3pBase
            
    def vBase3p(self):
        return self._3pVBase

    def vBase5p(self):
        return self._5pVBase

    def segment3p(self):
        return self._3pSegment

    def segment5p(self):
        return self._5pSegment

