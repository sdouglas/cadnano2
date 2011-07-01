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

    def __init__(self, startVB, endVB):
        assert(startVB.vStrand() == endVB.vStrand())
        # Location of the first base that belongs to self
        # with a 3' connection to the previous segment
        self._3pBase = startVB
        # Location of the last base that belongs to self
        # with a 5' connection to the next segment
        self._5pBase = endVB

    def length(self):
        if self._3pBase
            
    def end3(self):
        return self._3pBase

    def end5(self):
        return self._5pBase

    def endL(self, vHelix):
        """
        Returns the leftmost end self has on vHelix
        """
        a, b = self._3pBase, self._5pBase
        if a.end3().vHelix