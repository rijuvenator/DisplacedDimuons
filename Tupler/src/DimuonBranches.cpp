#include "DisplacedDimuons/Tupler/interface/DimuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

#include "DataFormats/Math/interface/deltaPhi.h"
#include "DataFormats/Math/interface/deltaR.h"

#include "PhysicsTools/RecoUtils/interface/CheckHitPattern.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

bool DimuonBranches::alreadyPrinted_ = false;

void DimuonBranches::Fill(const edm::EventSetup& iSetup,
    const edm::Handle<reco::TrackCollection> &dsamuonsHandle,
    const edm::ESHandle<TransientTrackBuilder>& ttB,
    const edm::Handle<reco::VertexCollection> &verticesHandle,
    const edm::Handle<reco::BeamSpot> &beamspotHandle,
    const edm::Handle<pat::MuonCollection> &patmuonsHandle)
{
  Reset();
  static bool debug = false;

  // already checked if muons, vertices, and beamspot are valid
  const reco::TrackCollection &dsamuons = *dsamuonsHandle;
  const pat::MuonCollection   &patmuons = *patmuonsHandle;

  // Dimuons made of a pair of DSA muons.
  unsigned int i, j;
  reco::TrackCollection::const_iterator ptk, qtk;
  for (i = 0, ptk = dsamuons.begin(); ptk != dsamuons.end(); ptk++, i++) {
    for (j = i+1, qtk = ptk+1; qtk != dsamuons.end(); qtk++, j++) {
      FillDimuon(i, j, *ptk, *qtk, iSetup, ttB, verticesHandle, beamspotHandle, debug);
    }
  }

  // Dimuons made of a pair of global and/or tracker muons.
  pat::MuonCollection patmuons_fltd;
  pat::MuonCollection::const_iterator pmu, qmu;
  // First pre-filter the PAT muon collection by keeping only global
  // and arbitrated tracker muons, as is done in the DSA-PAT matching.
  // This is necessary to ensure that the indices of PAT muons match.
  for (pmu = patmuons.begin(); pmu != patmuons.end(); pmu++) {
    if (pmu->isGlobalMuon() ||
        (pmu->isTrackerMuon() && pmu->muonID("TrackerMuonArbitrated"))) {
      patmuons_fltd.push_back(*pmu);
    }
  }

  // Now try to make dimuons.  Skip tracker muons with only one
  // segment matched.
  for (i = 0, pmu = patmuons_fltd.begin(); pmu != patmuons_fltd.end(); pmu++, i++) {
    if (!pmu->isGlobalMuon() && pmu->numberOfMatchedStations() <= 1)
      continue;
    const reco::TrackRef ptk = pmu->tunePMuonBestTrack();

    for (j = i+1, qmu = pmu+1; qmu != patmuons_fltd.end(); qmu++, j++) {
      if (!qmu->isGlobalMuon() && qmu->numberOfMatchedStations() <= 1)
        continue;
      const reco::TrackRef qtk = qmu->tunePMuonBestTrack();

      // Increment the muon index by 1000 to flag global/tracker
      // muons.
      FillDimuon(1000+i, 1000+j, *ptk, *qtk, iSetup, ttB, verticesHandle, beamspotHandle, debug);

    }
  }

  // Dimuons made of one DSA muon and one global and/or tracker muon.
  // Again skip tracker muons with only one segment matched.
  // Note that mu1 will ALWAYS be the DSA muon and mu2 will ALWAYS be the PAT muon
  for (i = 0, ptk = dsamuons.begin(); ptk != dsamuons.end(); ptk++, i++) {
    for (j = 0, qmu = patmuons_fltd.begin(); qmu != patmuons_fltd.end(); qmu++, j++) {
      if (!qmu->isGlobalMuon() && qmu->numberOfMatchedStations() <= 1)
        continue;
      const reco::TrackRef qtk = qmu->tunePMuonBestTrack();
      FillDimuon(i, 1000+j, *ptk, *qtk, iSetup, ttB, verticesHandle, beamspotHandle, debug);
    }
  }
}

void DimuonBranches::FillDimuon(int i, int j,
    const reco::Track& tk1, const reco::Track& tk2,
    const edm::EventSetup& iSetup,
    const edm::ESHandle<TransientTrackBuilder>& ttB,
    const edm::Handle<reco::VertexCollection> &verticesHandle,
    const edm::Handle<reco::BeamSpot> &beamspotHandle,
    bool debug)
{
  static float mass = .105658375;
  DisplacedMuonFiller muf;
  const reco::BeamSpot &beamspot = *beamspotHandle;

  reco::TransientTrack ott1 = ttB->build(tk1);
  if (!ott1.isValid()) return;
  // Not sure we need to set the beam spot, but do it to be on the safe side
  ott1.setBeamSpot(beamspot);

  reco::TransientTrack ott2 = ttB->build(tk2);
  if (!ott2.isValid()) return;
  ott2.setBeamSpot(beamspot);

  // fit the secondary vertex
  std::vector<reco::TransientTrack> trackVector = {ott1, ott2};

  // Setup Kalman vertex fitter and activate the refit of the tracks.
  // Uncomment the next 4 lines if you want to change the default fitter
  // parameters.
  // edm::ParameterSet kvfPSet;
  // kvfPSet.addParameter<double>("maxDistance", 0.01);   // default is 0.01
  // kvfPSet.addParameter<int>("maxNbrOfIterations", 10); // default is 10
  // KalmanVertexFitter kvf(kvfPSet, true);
  // Default fitter settings
  KalmanVertexFitter kvf(true);

  TransientVertex tv;
  try
  {
    tv = kvf.vertex(trackVector);
  }
  catch ( VertexException & e )
  {
    edm::LogWarning("DimuonBranches")
      << "exception in common-vertex fit caught: " << e.what();
    return;
  }

  // Only store those dimuons for which the common-vertex fit
  // converged.  If the fit failed, all dimuon quantities can be
  // calculated later on from the info available in the single-muon
  // branches.
  if (!tv.isValid()) {
    if (debug)
      std::cout << "Dimuon info: common-vertex fit failed for muon id's = "
        << i << " / " << j << std::endl;
    return;
  }

  reco::Vertex rv = tv;
  float rv_x = rv.x();
  float rv_y = rv.y();
  float rv_z = rv.z();
  float rv_normChi2 = rv.normalizedChi2();

  // Primary vertex
  const reco::VertexCollection &vertices = *verticesHandle;
  reco::Vertex pv = vertices.front();

  // SV-PV vector (math::XYZPoint)
  auto diffP = rv.position() - pv.position();

  // Distance between the primary and the dilepton vertices in the
  // transverse plane and its uncertainty
  VertexDistanceXY vdxy;
  Measurement1D vdist2d = vdxy.distance(pv, rv);
  float Lxy_pv    = vdist2d.value();
  float Lxysig_pv = vdist2d.significance();

  // Distance w.r.t. the beam spot and its uncertainty
  VertexState beamSpotState(beamspot);
  vdist2d = vdxy.distance(beamSpotState, rv);
  float Lxy_bs    = vdist2d.value();
  float Lxysig_bs = vdist2d.significance();

  // Check if hit pattern of each track is consistent with it being
  // produced at a given vertex.
  CheckHitPattern checkHitPattern;
  CheckHitPattern::Result hitPattern;
  int cand1_hitsInFrontOfVert = 0, cand2_hitsInFrontOfVert = 0;
  int cand1_missHitsAfterVert = 0, cand2_missHitsAfterVert = 0;
  // These methods work only for hits in the tracker, so skip this for
  // DSA muons.
  if (i >= 1000) {
    //checkHitPattern.print(tk1);
    hitPattern = checkHitPattern.analyze(iSetup, tk1, tv.vertexState(), true);
    cand1_hitsInFrontOfVert = hitPattern.hitsInFrontOfVert;
    cand1_missHitsAfterVert = hitPattern.missHitsAfterVert;
  }
  if (j >= 1000) {
    //checkHitPattern.print(tk2);
    hitPattern = checkHitPattern.analyze(iSetup, tk2, tv.vertexState(), true);
    cand2_hitsInFrontOfVert = hitPattern.hitsInFrontOfVert;
    cand2_missHitsAfterVert = hitPattern.missHitsAfterVert;
  }

  // Refitted transient tracks
  reco::TransientTrack rtt1 = tv.refittedTrack(ott1);
  reco::TransientTrack rtt2 = tv.refittedTrack(ott2);
  TLorentzVector rt1_p4(rtt1.track().px(), rtt1.track().py(), rtt1.track().pz(), sqrt(pow(rtt1.track().p(),2.)+pow(mass,2.)));
  TLorentzVector rt2_p4(rtt2.track().px(), rtt2.track().py(), rtt2.track().pz(), sqrt(pow(rtt2.track().p(),2.)+pow(mass,2.)));

  // Dimuon 4-vector
  TLorentzVector dimu_p4 = rt1_p4 + rt2_p4;

  // delta phi
  float dPhi = fabs(deltaPhi(diffP.Phi(), dimu_p4.Phi()));

  // cosine 3D opening angle: P1 . P2 / |P1| |P2|
  float cosAlpha = rt1_p4.Vect().Dot(rt2_p4.Vect())/rt1_p4.P()/rt2_p4.P();

  // delta R between the tracks
  float dR = rt1_p4.DeltaR(rt2_p4);

  // refitted muon candidates
  DisplacedMuon muon_cand1 = muf.Fill(rtt1.track(), ttB, verticesHandle, beamspotHandle, false);
  DisplacedMuon muon_cand2 = muf.Fill(rtt2.track(), ttB, verticesHandle, beamspotHandle, false);
  muon_cand1.idx = i;
  muon_cand2.idx = j;

  // Attempt to refit the primary vertex w/o the candidate muon
  // tracks.  Requires "reco::Tracks generalTracks" collection,
  // so disabled for now.
  // reco::Vertex rpv = RefittedVertex(ttB, pv, beamspot, ott1, ott2, debug);

  // fill tree
  // dimuon variables
  dim_pt       .push_back(dimu_p4.Pt ());
  dim_eta      .push_back(dimu_p4.Eta());
  dim_phi      .push_back(dimu_p4.Phi());
  dim_mass     .push_back(dimu_p4.M  ());
  dim_p        .push_back(dimu_p4.P  ());
  dim_x        .push_back(rv_x         );
  dim_y        .push_back(rv_y         );
  dim_z        .push_back(rv_z         );
  dim_normChi2 .push_back(rv_normChi2  );
  dim_Lxy_pv   .push_back(Lxy_pv       );
  dim_LxySig_pv.push_back(Lxysig_pv    );
  dim_Lxy_bs   .push_back(Lxy_bs       );
  dim_LxySig_bs.push_back(Lxysig_bs    );
  dim_deltaPhi .push_back(dPhi         );
  dim_deltaR   .push_back(dR           );
  dim_cosAlpha .push_back(cosAlpha     );

  // First muon candidate resulting from the common-vertex fit.  The
  // refitted track does not have chi2, ndof, and hitpattern set; the
  // reference point of the track is identical to the position of the
  // refitted vertex.
  dim_mu1_idx                .push_back(     muon_cand1.idx         );
  dim_mu1_px                 .push_back(     muon_cand1.px          );
  dim_mu1_py                 .push_back(     muon_cand1.py          );
  dim_mu1_pz                 .push_back(     muon_cand1.pz          );
  dim_mu1_ptError            .push_back(     muon_cand1.ptError     );
  dim_mu1_eta                .push_back(     muon_cand1.eta         );
  dim_mu1_phi                .push_back(     muon_cand1.phi         );
  dim_mu1_charge             .push_back(     muon_cand1.charge      );
  dim_mu1_d0_pv              .push_back(fabs(muon_cand1.d0_pv      ));
  dim_mu1_d0_bs              .push_back(fabs(muon_cand1.d0_bs      ));
  dim_mu1_d0_pv_lin          .push_back(fabs(muon_cand1.d0_pv_lin  ));
  dim_mu1_d0_bs_lin          .push_back(fabs(muon_cand1.d0_bs_lin  ));
  dim_mu1_d0sig_pv           .push_back(     muon_cand1.d0sig_pv    );
  dim_mu1_d0sig_bs           .push_back(     muon_cand1.d0sig_bs    );
  dim_mu1_d0sig_pv_lin       .push_back(     muon_cand1.d0sig_pv_lin);
  dim_mu1_d0sig_bs_lin       .push_back(     muon_cand1.d0sig_bs_lin);
  dim_mu1_dz_pv              .push_back(fabs(muon_cand1.dz_pv      ));
  dim_mu1_dz_bs              .push_back(fabs(muon_cand1.dz_bs      ));
  dim_mu1_dz_pv_lin          .push_back(fabs(muon_cand1.dz_pv_lin  ));
  dim_mu1_dz_bs_lin          .push_back(fabs(muon_cand1.dz_bs_lin  ));
  dim_mu1_dzsig_pv           .push_back(     muon_cand1.dzsig_pv    );
  dim_mu1_dzsig_bs           .push_back(     muon_cand1.dzsig_bs    );
  dim_mu1_dzsig_pv_lin       .push_back(     muon_cand1.dzsig_pv_lin);
  dim_mu1_dzsig_bs_lin       .push_back(     muon_cand1.dzsig_bs_lin);
  dim_mu1_hitsBeforeVtx      .push_back(cand1_hitsInFrontOfVert     );
  dim_mu1_missingHitsAfterVtx.push_back(cand1_missHitsAfterVert     );

  // second muon candidate resulting from the common-vertex fit
  dim_mu2_idx                .push_back(     muon_cand2.idx         );
  dim_mu2_px                 .push_back(     muon_cand2.px          );
  dim_mu2_py                 .push_back(     muon_cand2.py          );
  dim_mu2_pz                 .push_back(     muon_cand2.pz          );
  dim_mu2_ptError            .push_back(     muon_cand2.ptError     );
  dim_mu2_eta                .push_back(     muon_cand2.eta         );
  dim_mu2_phi                .push_back(     muon_cand2.phi         );
  dim_mu2_charge             .push_back(     muon_cand2.charge      );
  dim_mu2_d0_pv              .push_back(fabs(muon_cand2.d0_pv      ));
  dim_mu2_d0_bs              .push_back(fabs(muon_cand2.d0_bs      ));
  dim_mu2_d0_pv_lin          .push_back(fabs(muon_cand2.d0_pv_lin  ));
  dim_mu2_d0_bs_lin          .push_back(fabs(muon_cand2.d0_bs_lin  ));
  dim_mu2_d0sig_pv           .push_back(     muon_cand2.d0sig_pv    );
  dim_mu2_d0sig_bs           .push_back(     muon_cand2.d0sig_bs    );
  dim_mu2_d0sig_pv_lin       .push_back(     muon_cand2.d0sig_pv_lin);
  dim_mu2_d0sig_bs_lin       .push_back(     muon_cand2.d0sig_bs_lin);
  dim_mu2_dz_pv              .push_back(fabs(muon_cand2.dz_pv      ));
  dim_mu2_dz_bs              .push_back(fabs(muon_cand2.dz_bs      ));
  dim_mu2_dz_pv_lin          .push_back(fabs(muon_cand2.dz_pv_lin  ));
  dim_mu2_dz_bs_lin          .push_back(fabs(muon_cand2.dz_bs_lin  ));
  dim_mu2_dzsig_pv           .push_back(     muon_cand2.dzsig_pv    );
  dim_mu2_dzsig_bs           .push_back(     muon_cand2.dzsig_bs    );
  dim_mu2_dzsig_pv_lin       .push_back(     muon_cand2.dzsig_pv_lin);
  dim_mu2_dzsig_bs_lin       .push_back(     muon_cand2.dzsig_bs_lin);
  dim_mu2_hitsBeforeVtx      .push_back(cand2_hitsInFrontOfVert     );
  dim_mu2_missingHitsAfterVtx.push_back(cand2_missHitsAfterVert     );

  if (debug)
  {
    std::cout << "Dimuon info: muon id's = " << i << " " << j
      << " pt = "  << dimu_p4.Pt()  << " p = "   << dimu_p4.P()
      << " eta = " << dimu_p4.Eta() << " phi = " << dimu_p4.Phi()
      << " mass = " << dimu_p4.M() << std::endl;
    std::cout << "  Common vertex: (x; y; z): ("
      << rv_x << ";" << rv_y << ";" << rv_z 
      << ") chi2/ndof = "
    // << rv.chi2() << "/" << rv.ndof() << " = "
      << rv_normChi2 << std::endl;
    std::cout << "  Lxy(PV) = "             << Lxy_pv
      << " Lxy(PV) significance = " << Lxysig_pv
      << " Lxy(BS) = "              << Lxy_bs
      << " Lxy(BS) significance = " << Lxysig_bs << std::endl;
    std::cout << "  dR = "         << dR       << " dphi = " << dPhi
      << " cos(alpha) = "  << cosAlpha << std::endl;
    std::cout << " hitsInFrontOfVert mu1 / mu2: " << cand1_hitsInFrontOfVert
      << " / " << cand2_hitsInFrontOfVert
      << " missHitsAfterVert mu1 / mu2: " << cand1_missHitsAfterVert
      << " / " << cand2_missHitsAfterVert << std::endl;
    std::cout << "Refitted DSA muon info:" << muon_cand1;
    std::cout << "Refitted DSA muon info:" << muon_cand2;
  }
}


// Refit primary vertex w/o the two lepton candidates
reco::Vertex DimuonBranches::RefittedVertex(
    const edm::ESHandle<TransientTrackBuilder>& ttB,
    const reco::Vertex& pv, const reco::BeamSpot& bs,
    const reco::TransientTrack& tt1,
    const reco::TransientTrack& tt2, const bool debug)
{
  reco::Vertex newvtx = pv;
  bool need_to_refit = false;
  const static float dRcut = 0.1; // not tuned

  // Check whether the lepton candidates are matched to tracks
  // included in the vertex fit and if yes take these tracks out
  std::vector<reco::TransientTrack> vtracks;
  //int itrk = 0;
  for (reco::Vertex::trackRef_iterator it = pv.tracks_begin(); it != pv.tracks_end(); it++)
  {
    //std::cout << "vtrk # " << ++itrk << " pt = " << (**it).pt() << std::endl;
    const reco::Track & track = *(it->get());

    // Match tracks by proximity.  Perhaps we should extrapolate them
    // to some common surface at some point...
    double dR1 = deltaR(track.eta(), track.phi(), tt1.track().eta(), tt1.track().phi());
    double dR2 = deltaR(track.eta(), track.phi(), tt2.track().eta(), tt2.track().phi());
    // To be refined later... currently more than track can be matched
    // to the same candidate and removed, so we should perhaps use the
    // smallest dR
    if (dR1 < dRcut || dR2 < dRcut)
    {
      if (debug)
      {
        if (dR1 < dRcut)
        {
          double deta1 = fabs(track.eta() - tt1.track().eta());
          double dphi1 = deltaPhi(track.phi(), tt1.track().phi());
          std::cout << "PV refit: remove track 1: pt = " << track.pt()
            << " deta = " << deta1 << " dphi = " << dphi1
            << " dR = " << dR1 << std::endl;
        }
        if (dR2 < dRcut)
        {
          double deta2 = fabs(track.eta() - tt2.track().eta());
          double dphi2 = deltaPhi(track.phi(), tt2.track().phi());
          std::cout << "PV refit: remove track 2: pt = " << track.pt()
            << " deta = " << deta2 << " dphi = " << dphi2
            << " dR = " << dR2 << std::endl;
        }
      }
      need_to_refit = true;
    }
    else
    {
      reco::TransientTrack ttrack = ttB->build(track);
      ttrack.setBeamSpot(bs);
      vtracks.push_back(ttrack);
    }
  }

  // Re-fit the vertex
  if (need_to_refit)
  {
    AdaptiveVertexFitter* fitter = new AdaptiveVertexFitter();
    TransientVertex tv = fitter->vertex(vtracks, bs);
    newvtx = tv;
    if (debug)
      std::cout << "Refitted primary vtx: ("
        << newvtx.x() << "+/-" << newvtx.xError() << "; "
        << newvtx.y() << "+/-" << newvtx.yError() << "; "
        << newvtx.z() << "+/-" << newvtx.zError()
        << ") chi2/ndof = " << newvtx.chi2() << "/" << newvtx.ndof()
        << " ntracks = " << newvtx.nTracks() << std::endl;
  }

  return newvtx;
}
