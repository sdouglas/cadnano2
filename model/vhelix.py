class VHelix(object):
    def __init__(self):
        # Set by parent
        # self._part
        # self._coords
        # self._idnum
        self._scaf = []
        self._stap = []

    ########################## Public Read API ##########################

    def part(self):
        return self._part

    def coords(self):
        return self._coords

    def idnum(self):
        return self._idnum

    def strandDrawn5To3(self, vStrand):
        return self._part.strandDrawn5To3(vStrand)

    ########################## Private Write API ##########################

    def _setPart(self, part, coords, idnum):
        """
        Parts use this method to notify the receiver that it has been added to
        a part at coords with a given idnum.
        """
        self._part = newPart
        self._coords = coords
        self._idnum = idnum
