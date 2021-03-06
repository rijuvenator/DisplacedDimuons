#include "DisplacedDimuons/Tupler/interface/PATMuonBranches.h"

bool PATMuonBranches::alreadyPrinted_ = false;

void PATMuonBranches::Fill(const edm::Handle<pat::MuonCollection> &muonsHandle,
    const edm::ESHandle<TransientTrackBuilder>& ttB,
    const edm::Handle<reco::VertexCollection> &verticesHandle,
    const edm::Handle<reco::BeamSpot> &beamspotHandle,
    const edm::ESHandle<Propagator>& propagator,
    const edm::ESHandle<MagneticField>& magfield)
{
  static bool debug = false;

  Reset();

  // Check if failed to get
  if (FailedToGet(muonsHandle)) return;
  const pat::MuonCollection &muons = *muonsHandle;

  unsigned int idx = 0;
  DisplacedMuonFiller muf;
  for (const auto &mu : muons) {
    bool isGlobal     = mu.isGlobalMuon();
    bool isTracker    = mu.isTrackerMuon();
    bool isStandalone = mu.isStandAloneMuon();
    bool isPF         = mu.isPFMuon();

    // Only save global and arbitrated tracker muons
    if (!isGlobal && !(isTracker && mu.muonID("TrackerMuonArbitrated")))
      continue;

    // "Medium" muon id
    bool isMedium = isMediumMuon(mu);

    const reco::Track* tk = mu.tunePMuonBestTrack().get();
    //const reco::Track* tk = mu.combinedMuon().get();
    //const reco::Track* tk = mu.innerTrack().get();
    if (!tk) {
      std::cout << "+++ PATMuonBranches::Fill warning: tuneP track for muon # "
        << idx++ << " is not found +++" << std::endl;
      continue;
    }

    DisplacedMuon muon_cand =
      muf.Fill(*tk, ttB, verticesHandle, beamspotHandle, true);
    muon_cand.idx = idx++;

    // If tunePMuonBestTrack is a tracker track, muon hit variables
    // are not filled.  Get them from the corresponding global muon.
    if (tk->hitPattern().numberOfMuonHits() == 0 && isGlobal) {
      const reco::Track* tk_glb = mu.globalTrack().get();
      muon_cand.n_MuonHits    = tk_glb->hitPattern().numberOfValidMuonHits()   ;
      muon_cand.n_DTHits      = tk_glb->hitPattern().numberOfValidMuonDTHits() ;
      muon_cand.n_CSCHits     = tk_glb->hitPattern().numberOfValidMuonCSCHits();
      muon_cand.n_DTStations  = tk_glb->hitPattern().dtStationsWithValidHits() ;
      muon_cand.n_CSCStations = tk_glb->hitPattern().cscStationsWithValidHits();
    }

    // chi2 of the global-muon track
    int   globndof = -999;
    float globchi2 = -999.;
    if (isGlobal) {
      globchi2 = mu.globalTrack()->chi2();
      globndof = mu.globalTrack()->ndof();
    }

    // Detector-based isolation variables.
    // The summed track pT in a cone of deltaR < 0.3
    float trackIso = mu.trackIso();
    // The summed ET of all recHits in the ECAL in a cone of deltaR <
    // 0.3
    float ecalIso  = mu.ecalIso();
    // The summed ET of all caloTowers in the HCAL in a cone of deltaR
    // < 0.4
    float hcalIso  = mu.hcalIso();

    // Number of muon stations with matched segments (tracker muons only)
    int n_MatchedStations = mu.numberOfMatchedStations();

    // Whether the track is "high purity" (i.e., good quality) or not
    int isHighPurity = tk->quality(reco::TrackBase::TrackQuality::highPurity);

    if (debug) {
      std::cout << " PAT muon info:"
        << " global? "       << (isGlobal     ? "yes" : "no")
        << "; tracker? "     << (isTracker    ? "yes" : "no")
        << "; standalone? "  << (isStandalone ? "yes" : "no")
        << "; PF? "          << (isPF         ? "yes" : "no")
        << "; medium? "      << (isMedium     ? "yes" : "no")
        << "; high purity? " << (isHighPurity ? "yes" : "no")
	<< "; tuneP track type: " << mu.tunePMuonBestTrackType() << std::endl;
      std::cout << " " << muon_cand;
      std::cout << "  N(matched muon stations) = " << n_MatchedStations;
      if (isGlobal)
	std::cout << "  global chi2/ndof = " << globchi2 << "/" << globndof
		  << " = " << globchi2/globndof;
      std::cout<< " track iso = " << mu.trackIso()
	       << " ecal iso = "  << mu.ecalIso()
	       << " hcal iso = "  << mu.hcalIso() << std::endl;
    }

#ifdef ONCE_STA_SEGMENTS_ARE_AVAILABLE
    // Extract the list of segments belonging to a global muon
    // if (isStandalone) {
    if (isGlobal) {
      reco::TrackRef outTrack = mu.outerTrack();

      trackingRecHit_iterator recHitIt  = outTrack->recHitsBegin();
      trackingRecHit_iterator recHitEnd = outTrack->recHitsEnd();
      for (; recHitIt != recHitEnd; ++recHitIt) {
	if (!(*recHitIt)->isValid()) continue;
	DetId id = (*recHitIt)->geographicalId();
	if (id.det() != DetId::Muon) continue;
	int muonSubdetId = id.subdetId();
	if (muonSubdetId == MuonSubdetId::DT ||
	    muonSubdetId == MuonSubdetId::CSC) {
	  int station;
	  if (muonSubdetId == MuonSubdetId::DT) {
	    DTChamberId segId(id.rawId());
	    station = segId.station();
	  }
	  else if (muonSubdetId == MuonSubdetId::CSC) {
	    CSCDetId segId(id.rawId());
	    station = segId.station();
	  }

	  if (debug)
	    std::cout << "STA muon segment: subdet "
                      << ((muonSubdetId == MuonSubdetId::DT) ? "DT" : "CSC")
		      << " station = " << station
		      << " id = " << id.rawId()
		      << " x = " << (*recHitIt)->localPosition().x()
		      << " y = " << (*recHitIt)->localPosition().y()
		      << std::endl;
	}
      }
    }
#endif

    // Fill the Tree
    patmu_idx    .push_back(muon_cand.idx);
    patmu_px     .push_back(muon_cand.px);
    patmu_py     .push_back(muon_cand.py);
    patmu_pz     .push_back(muon_cand.pz);
    patmu_ptError.push_back(muon_cand.ptError);
    patmu_eta    .push_back(muon_cand.eta);
    patmu_phi    .push_back(muon_cand.phi);
    patmu_charge .push_back(muon_cand.charge);
    patmu_chi2   .push_back(muon_cand.chi2);
    patmu_ndof   .push_back(muon_cand.ndof);

    patmu_x      .push_back(muon_cand.x);
    patmu_y      .push_back(muon_cand.y);
    patmu_z      .push_back(muon_cand.z);

    patmu_nMuonHits       .push_back(muon_cand.n_MuonHits);
    patmu_nDTHits         .push_back(muon_cand.n_DTHits);
    patmu_nCSCHits        .push_back(muon_cand.n_CSCHits);
    patmu_nDTStations     .push_back(muon_cand.n_DTStations);
    patmu_nCSCStations    .push_back(muon_cand.n_CSCStations);

    // these are unique to PAT muons
    patmu_nMatchedStations.push_back(n_MatchedStations);
    patmu_isGlobal        .push_back(isGlobal);
    patmu_isTracker       .push_back(isTracker);
    patmu_isMedium        .push_back(isMedium);
    patmu_nPixelHits      .push_back(muon_cand.n_PxlHits);
    patmu_nTrackerHits    .push_back(muon_cand.n_TrkHits);
    patmu_nTrackerLayers  .push_back(muon_cand.n_TrkLayers);
    patmu_trackIso        .push_back(trackIso);
    patmu_ecalIso         .push_back(ecalIso);
    patmu_hcalIso         .push_back(hcalIso);
    patmu_globchi2        .push_back(globchi2);
    patmu_globndof        .push_back(globndof);
    patmu_hpur            .push_back(isHighPurity);

    patmu_d0_pv       .push_back(fabs(muon_cand.d0_pv      ));
    patmu_d0_bs       .push_back(fabs(muon_cand.d0_bs      ));
    patmu_d0_pv_lin   .push_back(fabs(muon_cand.d0_pv_lin  ));
    patmu_d0_bs_lin   .push_back(fabs(muon_cand.d0_bs_lin  ));
    patmu_d0sig_pv    .push_back(     muon_cand.d0sig_pv    );
    patmu_d0sig_bs    .push_back(     muon_cand.d0sig_bs    );
    patmu_d0sig_pv_lin.push_back(     muon_cand.d0sig_pv_lin);
    patmu_d0sig_bs_lin.push_back(     muon_cand.d0sig_bs_lin);

    patmu_dz_pv       .push_back(fabs(muon_cand.dz_pv      ));
    patmu_dz_bs       .push_back(fabs(muon_cand.dz_bs      ));
    patmu_dz_pv_lin   .push_back(fabs(muon_cand.dz_pv_lin  ));
    patmu_dz_bs_lin   .push_back(fabs(muon_cand.dz_bs_lin  ));
    patmu_dzsig_pv    .push_back(     muon_cand.dzsig_pv    );
    patmu_dzsig_bs    .push_back(     muon_cand.dzsig_bs    );
    patmu_dzsig_pv_lin.push_back(     muon_cand.dzsig_pv_lin);
    patmu_dzsig_bs_lin.push_back(     muon_cand.dzsig_bs_lin);

    const reco::GenParticle * gen = mu.genLepton();
    if (gen != 0)
    {
      patmu_gen_pdgID .push_back(gen->pdgId ());
      patmu_gen_pt    .push_back(gen->pt    ());
      patmu_gen_eta   .push_back(gen->eta   ());
      patmu_gen_phi   .push_back(gen->phi   ());
      patmu_gen_mass  .push_back(gen->mass  ());
      patmu_gen_energy.push_back(gen->energy());
      patmu_gen_charge.push_back(gen->charge());
      patmu_gen_x     .push_back(gen->vx    ());
      patmu_gen_y     .push_back(gen->vy    ());
      patmu_gen_z     .push_back(gen->vz    ());
    }
    else
    {
      patmu_gen_pdgID .push_back(-999);
      patmu_gen_pt    .push_back(-999);
      patmu_gen_eta   .push_back(-999);
      patmu_gen_phi   .push_back(-999);
      patmu_gen_mass  .push_back(-999);
      patmu_gen_energy.push_back(-999);
      patmu_gen_charge.push_back(-999);
      patmu_gen_x     .push_back(-999);
      patmu_gen_y     .push_back(-999);
      patmu_gen_z     .push_back(-999);
    }
  }
}

// "Medium" muon id
// Implementing according to the description in
// https://twiki.cern.ch/twiki/bin/viewauth/CMS/SWGuideMuonIdRun2
bool PATMuonBranches::isMediumMuon(const pat::Muon & mu) {
  static bool debug = false;

  bool goodGlob = mu.isGlobalMuon() &&
    mu.globalTrack()->normalizedChi2() < 3. &&
    mu.combinedQuality().chi2LocalPosition < 12. &&
    mu.combinedQuality().trkKink < 20.;

  bool isMedium =
    mu.isPFMuon() &&
    (mu.isGlobalMuon() || (mu.isTrackerMuon() && mu.muonID("TrackerMuonArbitrated"))) &&
    mu.innerTrack()->validFraction() > 0.8 &&
    muon::segmentCompatibility(mu) > (goodGlob ? 0.303 : 0.451);

  if (debug) {
    std::cout << "  isMedium tests:"
	      << " chi2/ndof = "       << (mu.isGlobalMuon() ? mu.globalTrack()->normalizedChi2() : -999.)
	      << " trk-sta match = "   << mu.combinedQuality().chi2LocalPosition
	      << " trk kink = "        << mu.combinedQuality().trkKink
	      << " % of valid hits = " << mu.innerTrack()->validFraction()
	      << " segm. comp. = "     << muon::segmentCompatibility(mu)
	      << std::endl;
  }

  return isMedium;
}
