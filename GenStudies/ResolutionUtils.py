
class ResolutionParam:
    'Sample with resolution information'
    def __init__(self):
        self.matchedEtaResolution = []
        self.matchedPhiResolution = []
        self.matchedPtResolution = []
        self.matchedMassResolution = []
        self.matchedDeltaRResolution = []
        self.matchedDeltaEtaResolution = []
        self.matchedDeltaPhiResolution = []
        self.matchedRecoMassMother1 = []
        self.matchedRecoMassMother2 = []
                

    def getMatchedEtaResolution(self):
        return self.matchedEtaResolution
    def getMatchedPhiResolution(self):
        return self.matchedPhiResolution
    def getMatchedPtResolution(self):
        return self.matchedPtResolution
    def getMatchedMassResolution(self):
        return self.matchedMassResolution
    def getMatchedDeltaRResolution(self):
        return self.matchedDeltaRResolution
    def getMatchedDeltaEtaResolution(self):
        return self.matchedDeltaEtaResolution
    def getMatchedDeltaPhiResolution(self):
        return self.matchedDeltaPhiResolution
    def getMatchedRecoMassMother1(self):
        return self.matchedRecoMassMother1
    def getMatchedRecoMassMother2(self):
        return self.matchedRecoMassMother2

