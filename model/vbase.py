from enum import StrandType

class VBase(object):
    """
    Base is a convenience class that holds information identifying
    a certain base on a virtual helix, namely its coordinates:
        (part, virtual helix coords, virtual strand, index)
            part:                 a DNAPart
            virtual helix coords: (row, col) or whatever is used by DNAPart
            vStrand:                 model.enum.StrandType.{Scaffold, Staple}
            index:                increasing values go rightward in path view
    It also has convenience methods for getting other Base objects
    and relevant model objects (oligos, segments, etc).
    """
    def __init__(self, vHelix, vStrand, index):
        object.__init__()
        self._vHelix = vHelix
        self._vStrand = vStrand
        self._index = index
    
    def copy(self):
        return VBase(*self.coords())

    def coords(self):
        return (self._vHelix,\
                self._vStrand,\
                self._index)

    def vHelix(self):
        return self._vHelix

    def vStrand(self):
        return self._vStrand

    def idx(self):
        return self._index

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
        Base corresponding to 
        """
        if self._strandType == StrandType.Scaffold:
            strandType = StrandType.Staple
        else:
            strandType = StrandType.Scaffold
        return self.virtualHelix.base(strandType, self._index)

    def next5(self):
        """
        Shifts self one base in 5' direction on the vhelix
        """
        if self.drawn5To3():
            return self.prevL()
        else:
            return self.prevR()

    def prev3(self):
        """
        Shifts self one base in 3' direction on the vhelix
        """
        if self.drawn5To3():
            return self.nextR()
        else:
            return self.prevL()

    def nextR(self):
        """
        Shifts self one base rightwards in path view
        """
        return VBase(self._dnaPart,\
                     self._virtualHelixCoords,\
                     self._vStrand,\
                     self._index + 1)

    def prevL(self):
        """
        Shifts self one base leftwards in path view
        """
        return VBase(self._dnaPart,\
                     self._virtualHelixCoords,\
                     self._vStrand,\
                     self._index - 1)
