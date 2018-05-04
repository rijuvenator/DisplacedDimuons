from math import *

def isTrackType(RecoMuon, TrackType = 'STA'):

    if TrackType == 'STA':
        if RecoMuon.standAloneMuon().isNonnull():
            staMuonTrack = RecoMuon.standAloneMuon()
            staMuonTrackNumberOfValidMuonDTHits = staMuonTrack.hitPattern().numberOfValidMuonDTHits()
            staMuonTrackNumberOfValidMuonCSCHits = staMuonTrack.hitPattern().numberOfValidMuonCSCHits()
            staMuonTrackNumberOfValidMuonRPCHits = staMuonTrack.hitPattern().numberOfValidMuonRPCHits()
            staMuonTrackNumberOfValidMuonHits = staMuonTrack.hitPattern().numberOfValidMuonHits()
            staMuonTracknormalizedChi2 = staMuonTrack.normalizedChi2()
            if staMuonTrackNumberOfValidMuonHits > 16 and staMuonTracknormalizedChi2 <10:
                return True

        else:
            return False


    if TrackType == 'STA-NoPixel':
        if RecoMuon.standAloneMuon().isNonnull() and pfMuonTrack.hitPattern().numberOfValidPixelHits() == 0:
            staMuonTrack = RecoMuon.standAloneMuon()
            staMuonTrackNumberOfValidMuonDTHits = staMuonTrack.hitPattern().numberOfValidMuonDTHits()
            staMuonTrackNumberOfValidMuonCSCHits = staMuonTrack.hitPattern().numberOfValidMuonCSCHits()
            staMuonTrackNumberOfValidMuonRPCHits = staMuonTrack.hitPattern().numberOfValidMuonRPCHits()
            staMuonTrackNumberOfValidMuonHits = staMuonTrack.hitPattern().numberOfValidMuonHits()
            staMuonTracknormalizedChi2 = staMuonTrack.normalizedChi2()
            if staMuonTrackNumberOfValidMuonHits > 16 and staMuonTracknormalizedChi2 <10:
                return True

        else:
            return False


    if TrackType == 'PFTrack':
        if RecoMuon.muonBestTrack().isNonnull():
            pfMuonTrack = RecoMuon.muonBestTrack()
            pfMuonTrackNumberOfValidPixelHits = pfMuonTrack.hitPattern().numberOfValidPixelHits()
            pfMuonTrackTrackerLayersWithMeasurement = pfMuonTrack.hitPattern().trackerLayersWithMeasurement()
            
            if pfMuonTrackNumberOfValidPixelHits > 1 and pfMuonTrackTrackerLayersWithMeasurement >5:
                return True
                
        else:
            return False


    
