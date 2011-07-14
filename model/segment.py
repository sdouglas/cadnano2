class Segment(QObject):
    """
    Represents a segment of DNA that
    1) Has a length (# nucleotides)
    2) Has a 3' and 5' endpoint (Bases)
    3) The set of vhelix which contain bases of the segment
       is a nonproper subset of {startVB.vHelix(), endVB.vHelix()}
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

    def endL(self, vHelix):
        """
        Returns the leftmost end self has on vHelix
        """
        a, b = self._3pBase, self._5pBase
        if a.end3().vHelix