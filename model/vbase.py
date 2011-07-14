from enum import StrandType

class VBase(object):
    """
    Base is a convenience class that holds information identifying
    a certain base on a virtual helix, namely its coordinates:
        (part, virtual helix coords, virtual strand, index)
            vHelix:               the virtualhelix of which this vBase is a member
            vStrand:              model.enum.StrandType.{Scaffold, Staple}
            index:                increasing values go rightward in path view
    It also has convenience methods for getting other Base objects
    and relevant model objects (oligos, segments, etc).
    """
    def __init__(self, vHelix, vStrand, vIndex):
        object.__init__()
        self._vHelix = vHelix
        self._vStrand = vStrand
        self._vIndex = vIndex

    def copy(self):
        return VBase(*self.coords())

    def coords(self):
        return (self._vHelix,\
                self._vStrand,\
                self._vIndex)

    def vHelix(self):
        return self._vHelix

    def vStrand(self):
        return self._vStrand

    def vIndex(self):
        return self._vIndex

    def part(self):
        return self.vHelix().

    def __eq__(self, other):
        return self.coords() == other.coords()

    def drawn5To3(self):
        """
        Returns True iff the vstrand on which 
        """
        return self._vHelix.strandDrawn5To3(self._vStrand)

    def partner(self):
        """
        Base on the same vhelix at the same vIndex but opposite strand
        """
        if self._strandType == StrandType.Scaffold:
            strandType = StrandType.Staple
        else:
            strandType = StrandType.Scaffold
        return self.virtualHelix.base(strandType, self._index)

    def vNext5(self):
        """
        Shifts self one base in 5' direction along the vhelix.
        """
        if self.drawn5To3():
            return self.prevL()
        else:
            return self.prevR()

    def vPrev3(self):
        """
        Shifts self one base in 3' direction along the vhelix.
        """
        if self.drawn5To3():
            return self.nextR()
        else:
            return self.prevL()

    def vNextR(self):
        """
        Shifts self one base rightwards along the vhelix in the path view.
        """
        return VBase(self._vHelix,\
                     self._vStrand,\
                     self._index + 1)

    def vPrevL(self):
        """
        Shifts self one base leftwards along the vhelix in the path view
        """
        return VBase(self._vHelix,\
                     self._vStrand,\
                     self._index - 1)
