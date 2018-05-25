#ifndef DISPLACEDMUONFILLER_H
#define DISPLACEDMUONFILLER_H

// CMSSW includes
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/DisplacedMuon.h"

// muon branch collection
class DisplacedMuonFiller
{
 public:
  // constructor
  DisplacedMuonFiller() {}

  // members

  // methods
  DisplacedMuon Fill(const reco::Track& track,
		     const edm::ESHandle<TransientTrackBuilder>& ttB,
		     const edm::Handle<reco::VertexCollection> &verticesHandle,
		     const edm::Handle<reco::BeamSpot> &beamspotHandle);
};

#endif
