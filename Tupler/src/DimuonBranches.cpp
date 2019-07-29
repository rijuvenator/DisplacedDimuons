#include "DisplacedDimuons/Tupler/interface/DimuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

#include "DataFormats/Math/interface/deltaPhi.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/RecoCandidate/interface/IsoDepositDirection.h"
#include "RecoMuon/MuonIsolation/plugins/TrackSelector.h"
//TODO: Figure out how to just include library
#include "RecoMuon/MuonIsolation/plugins/TrackSelector.cc"

#include "TrackingTools/PatternTools/interface/TwoTrackMinimumDistance.h"
#include "PhysicsTools/RecoUtils/interface/CheckHitPattern.h"
#include "RecoVertex/VertexTools/interface/InvariantMassFromVertex.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include <assert.h>

bool DimuonBranches::alreadyPrinted_ = false;

void DimuonBranches::Fill(const edm::EventSetup& iSetup,
			  const edm::Handle<reco::TrackCollection> &dsamuonsHandle,
			  const edm::ESHandle<TransientTrackBuilder>& ttB,
			  const edm::Handle<reco::VertexCollection> &verticesHandle,
			  const edm::Handle<reco::BeamSpot> &beamspotHandle,
			  const edm::Handle<pat::MuonCollection> &patmuonsHandle,
			  const edm::ESHandle<MagneticField>& magfield,
			  const edm::Handle<reco::TrackCollection> &generalTracksHandle)
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
      FillDimuon(i, j, *ptk, *qtk, iSetup, ttB, verticesHandle, beamspotHandle, magfield, generalTracksHandle, debug);
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
      FillDimuon(1000+i, 1000+j, *ptk, *qtk, iSetup, ttB, verticesHandle, beamspotHandle, magfield, generalTracksHandle, debug);

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
      FillDimuon(i, 1000+j, *ptk, *qtk, iSetup, ttB, verticesHandle, beamspotHandle, magfield, generalTracksHandle, debug);
    }
  }
}

void DimuonBranches::FillDimuon(int i, int j,
				const reco::Track& tk1, const reco::Track& tk2,
				const edm::EventSetup& iSetup,
				const edm::ESHandle<TransientTrackBuilder>& ttB,
				const edm::Handle<reco::VertexCollection> &verticesHandle,
				const edm::Handle<reco::BeamSpot> &beamspotHandle,
				const edm::ESHandle<MagneticField>& magfield,
				const edm::Handle<reco::TrackCollection> &generalTracksHandle,
				bool debug)
{
  static bool gtWarning = false;
  static float muon_mass = .105658375;
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

  CachingVertex<5> cv;
  TransientVertex tv;
  try
  {
    //tv = kvf.vertex(trackVector);
    // Find CachingVertex vertex first in order to calculate inv. mass uncertainty
    cv = kvf.vertex(trackVector);
    tv = TransientVertex(cv);
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
    //hitPattern = checkHitPattern.analyze(iSetup, tk1, tv.vertexState(), true);
    hitPattern = checkHitPattern.analyze(iSetup, tk1, tv.vertexState(), false);
    cand1_hitsInFrontOfVert = hitPattern.hitsInFrontOfVert;
    cand1_missHitsAfterVert = hitPattern.missHitsAfterVert;
  }
  if (j >= 1000) {
    //checkHitPattern.print(tk2);
    //hitPattern = checkHitPattern.analyze(iSetup, tk2, tv.vertexState(), true);
    hitPattern = checkHitPattern.analyze(iSetup, tk2, tv.vertexState(), false);
    cand2_hitsInFrontOfVert = hitPattern.hitsInFrontOfVert;
    cand2_missHitsAfterVert = hitPattern.missHitsAfterVert;
  }

  // Refitted transient tracks
  reco::TransientTrack rtt1 = tv.refittedTrack(ott1);
  reco::TransientTrack rtt2 = tv.refittedTrack(ott2);
  TLorentzVector rt1_p4(rtt1.track().px(), rtt1.track().py(), rtt1.track().pz(), sqrt(pow(rtt1.track().p(),2.)+pow(muon_mass,2.)));
  TLorentzVector rt2_p4(rtt2.track().px(), rtt2.track().py(), rtt2.track().pz(), sqrt(pow(rtt2.track().p(),2.)+pow(muon_mass,2.)));

  // Dimuon 4-vector
  TLorentzVector dimu_p4 = rt1_p4 + rt2_p4;

  // delta phi
  float dPhi = fabs(deltaPhi(diffP.Phi(), dimu_p4.Phi()));

  // cosine 3D opening angle: P1 . P2 / |P1| |P2|
  float cosAlpha = rt1_p4.Vect().Dot(rt2_p4.Vect())/rt1_p4.P()/rt2_p4.P();

  // delta R between the tracks
  float dR = rt1_p4.DeltaR(rt2_p4);

  // Dimuon invariant mass and its uncertainty
  InvariantMassFromVertex imfv;
  Measurement1D dimuon_mass = imfv.invariantMass(cv, muon_mass);

  // cos(alpha) and dR between the original tracks
  TLorentzVector ot1_p4(ott1.track().px(), ott1.track().py(), ott1.track().pz(), sqrt(pow(ott1.track().p(),2.)+pow(muon_mass,2.)));
  TLorentzVector ot2_p4(ott2.track().px(), ott2.track().py(), ott2.track().pz(), sqrt(pow(ott2.track().p(),2.)+pow(muon_mass,2.)));
  TLorentzVector dimu_orig_p4 = ot1_p4 + ot2_p4;
  float cosAlpha_orig = ot1_p4.Vect().Dot(ot2_p4.Vect())/ot1_p4.P()/ot2_p4.P();
  float dR_orig = ot1_p4.DeltaR(ot2_p4);

  // minimum distance between two original tracks (two helices)
  FreeTrajectoryState fts1(GlobalPoint(tk1.vx(), tk1.vy(), tk1.vz()),
			   GlobalVector(tk1.px(), tk1.py(), tk1.pz()),
			   tk1.charge(), magfield.product());
  FreeTrajectoryState fts2(GlobalPoint(tk2.vx(), tk2.vy(), tk2.vz()),
			   GlobalVector(tk2.px(), tk2.py(), tk2.pz()),
			   tk2.charge(), magfield.product());
  // TwoTrackMinimumDistance ttMinDist(TwoTrackMinimumDistance::SlowMode);
  TwoTrackMinimumDistance ttMinDist;
  bool dca_ok = ttMinDist.calculate(fts1, fts2);
  float dca = -999.;
  GlobalPoint pca;
  if (dca_ok) {
    // minimum distance in 3D
    dca = ttMinDist.distance();
    // arithmetic mean of the two points of closest approach
    pca = ttMinDist.crossingPoint();
  }
  else
    std::cout
      << "+++ Warning: TwoTrackMinimumDistance failed to calculate dca +++"
      << std::endl;

  // refitted muon candidates
  DisplacedMuon muon_cand1 = muf.Fill(rtt1.track(), ttB, verticesHandle, beamspotHandle, false);
  DisplacedMuon muon_cand2 = muf.Fill(rtt2.track(), ttB, verticesHandle, beamspotHandle, false);
  muon_cand1.idx = i;
  muon_cand2.idx = j;

  //testing DSA isolation criteria
  //const bool iso_debug = Lxysig_pv  > 10 && i < 1000 && j < 1000;
  const bool iso_debug = false;

  // Calculate dimuon isolation if generalTracks collection is available
  float dimuon_isoPmumu = -999., dimuon_isoLxy = -999.;
  float muon_cand1_iso = -999., muon_cand2_iso = -999.;
  if (!generalTracksHandle.failedToGet()) {
    const reco::TrackCollection &generalTracks = *generalTracksHandle;

    if(debug||iso_debug) {
      std::cout << "-------- Looking at Isolation --------" << std::endl;
      std::cout << "dim-pT: " << dimu_p4.Pt() << " eta: " << dimu_p4.Eta() << " phi: " << dimu_p4.Phi() << std::endl;
      std::cout << "mu1-pT: " << tk1.pt() << " eta: "<< tk1.eta() << " phi: " << tk1.phi() << std::endl;
      std::cout << "mu2-pT: " << tk2.pt() << " eta: "<< tk2.eta() << " phi: " << tk2.phi() << std::endl;
    }

    //clean up the general tracks so that they don't contain the muons we are using
    std::vector<reco::Track> muonTracks;
    muonTracks.push_back(tk1);
    muonTracks.push_back(tk2);

    const reco::TrackCollection& cleanedTracks = RemoveTracksFromCollection(generalTracks,muonTracks,debug||iso_debug);
    if(debug||iso_debug)
      std::cout << "generalTracks.size(): "  << generalTracks.size()
		<< " cleanedTracks.size(): " << cleanedTracks.size() << std::endl;

    // using momentum direction to define cone
    reco::isodeposit::Direction pmumuDir(dimu_p4.Eta(), dimu_p4.Phi());
    if(debug||iso_debug) std::cout << "== Isolating Dimuon Around Pmumu == " << std::endl;
    dimuon_isoPmumu = Isolation(pmumuDir, pv,dimu_p4, beamspot, cleanedTracks, debug||iso_debug);

    // using SV-PV to define cone
    reco::isodeposit::Direction lxyDir(diffP.Eta(), diffP.Phi());
    if(debug||iso_debug) std::cout << "== Isolating Dimuon Around Lxy == " << std::endl;
    dimuon_isoLxy = Isolation(lxyDir, pv,dimu_p4, beamspot, cleanedTracks, debug||iso_debug);

    //first muon individually
    reco::isodeposit::Direction muon1Dir(tk1.eta(), tk1.phi());
    if(debug||iso_debug) std::cout << "== Isolating Mu1 == " << std::endl;
    muon_cand1_iso = Isolation(muon1Dir, pv, ot1_p4, beamspot, cleanedTracks,debug||iso_debug);

    //second muon individually
    reco::isodeposit::Direction muon2Dir(tk2.eta(), tk2.phi());
    if(debug||iso_debug) std::cout << "== Isolating Mu2 == " << std::endl;
    muon_cand2_iso = Isolation(muon2Dir, pv, ot2_p4, beamspot, cleanedTracks,debug||iso_debug);
  }
  else {
    if (gtWarning == false) {
      edm::LogWarning("DimuonBranches")
	<< "+++ Warning: generalTracks collection is not found +++";
      gtWarning = true;
    }
  }

  // Attempt to refit the primary vertex w/o the candidate muon
  // tracks.  Requires "reco::Tracks generalTracks" collection,
  // so disabled for now.
  // reco::Vertex rpv = RefittedVertex(ttB, pv, beamspot, ott1, ott2, debug);

  // fill tree
  // dimuon variables
  dim_pt       .push_back(dimu_p4.Pt ());
  dim_eta      .push_back(dimu_p4.Eta());
  dim_phi      .push_back(dimu_p4.Phi());
  dim_p        .push_back(dimu_p4.P  ());
  dim_mass     .push_back(dimuon_mass.value());
  dim_massunc  .push_back(dimuon_mass.error());
  dim_x        .push_back(rv_x         );
  dim_y        .push_back(rv_y         );
  dim_z        .push_back(rv_z         );
  dim_dca      .push_back(dca          );
  dim_pca_x    .push_back(pca.x()      );
  dim_pca_y    .push_back(pca.y()      );
  dim_pca_z    .push_back(pca.z()      );
  dim_normChi2 .push_back(rv_normChi2  );
  dim_Lxy_pv   .push_back(Lxy_pv       );
  dim_LxySig_pv.push_back(Lxysig_pv    );
  dim_Lxy_bs   .push_back(Lxy_bs       );
  dim_LxySig_bs.push_back(Lxysig_bs    );
  dim_deltaPhi .push_back(dPhi         );
  dim_deltaR   .push_back(dR           );
  dim_cosAlpha .push_back(cosAlpha     );
  dim_cosAlphaOrig.push_back(cosAlpha_orig);
  dim_isoPmumu .push_back(dimuon_isoPmumu );
  dim_isoLxy   .push_back(dimuon_isoLxy   );

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
  dim_mu1_iso				 .push_back(muon_cand1_iso			    );

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
  dim_mu2_iso				 .push_back(muon_cand2_iso		        );

  //if (debug)
  if (debug||iso_debug)
  {
    std::cout << "Dimuon info: muon id's = " << i << " " << j
	      << " pt = "  << dimu_p4.Pt()  << " p = "   << dimu_p4.P()
	      << " eta = " << dimu_p4.Eta() << " phi = " << dimu_p4.Phi()
	      << " mass = " << dimuon_mass.value()
	      << " +/- "    << dimuon_mass.error() << std::endl;
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
    std::cout << "  dR_orig = "         << dR_orig
	      << " cos(alpha_orig) = "  << cosAlpha_orig
	      << " mass = "             << dimu_orig_p4.M()
	      << " min dist = " << dca << " pca (x; y; z): ("
	      << pca.x() << ";" << pca.y() << ";" << pca.z() << ")"
	      << std::endl;
    if (dimuon_isoPmumu > -99. || dimuon_isoLxy > -99.)
      std::cout << "  iso(Pmumu) = " << dimuon_isoPmumu
		<< " iso(Lxy) = " << dimuon_isoLxy
		<< " iso(mu1) = " << muon_cand1_iso
		<< " iso(mu2) = " << muon_cand2_iso << std::endl;
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


/* @brief Determines if a track, described with primary vertex pv, and momentum momentum
 * pointing in direction isoConeDirection is isolated with respect to other tracks found within the event.
 *
 * Function modelled from:
 *
 * https://github.com/cms-sw/cmssw/blob/f092629e3aac118bcf206450291a0c042c87769d/RecoMuon/MuonIsolation/plugins/TrackExtractor.cc
 *
 * returns (Sum of other tracks transverse momentum in cone) / (track transverse momentum)
 */
float DimuonBranches::Isolation(
		const reco::isodeposit::Direction& isoConeDirection,
		const reco::Vertex& pv,
		const TLorentzVector& momentum,
		const reco::BeamSpot &beamspot,
		const reco::TrackCollection &cleanedTracks,
		bool debug)
{
	const float dRmax = 0.3;

	/* Taken from
	 *
	 * https://github.com/cms-sw/cmssw/blob/02d4198c0b6615287fd88e9a8ff650aea994412e/RecoMuon/MuonIsolationProducers/python/trackExtractorBlocks_cff.py
	 */
	const float diffZ = 0.2;
	const float diffR = 0.1;
	const int nHitsMin = 0;
	const int chi2NdofMax = 1e9;
	const float chi2ProbMin = -1;
	const float ptMin = -1;

	const float vtx_z = pv.z();


	muonisolation::TrackSelector::Parameters pars(muonisolation::TrackSelector::Range(vtx_z-diffZ, vtx_z+diffZ),
			diffR, isoConeDirection, dRmax, beamspot.position());

	pars.nHitsMin = nHitsMin;
	pars.chi2NdofMax = chi2NdofMax;
	pars.chi2ProbMin = chi2ProbMin;
	pars.ptMin = ptMin;

	muonisolation::TrackSelector selection(pars);
	muonisolation::TrackSelector::result_type sel_tracks = selection(cleanedTracks);

	if (debug) {
	    std::cout << "Isolation - All Tracks: " << cleanedTracks.size()
		      << " Selected tracks for  Isolation: " << sel_tracks.size() << std::endl;
	    std::cout << " Isolation: zmin = " << vtx_z-diffZ
		      << " zmax = " << vtx_z+diffZ << " d0max = " << diffR
		      << " axis eta = " << isoConeDirection.eta()
		      << " axis phi = " << isoConeDirection.phi() << std::endl;

	    std::vector<float> nSelectedTracksPt;
	    unsigned int itrk = 0;
	    for (auto it = cleanedTracks.begin(); it != cleanedTracks.end(); ++it, itrk++) {
	    	double pt = it->pt();

	    	double z   = it->vz();
	    	double d0  = fabs(it->dxy(beamspot.position()));
	    	double eta = it->eta();
	    	double phi = it->phi();
	    	double dr  = pars.dir.deltaR(reco::isodeposit::Direction(eta, phi));
	    	/*
	    	if(pt >2)std::cout << "  general track #" << itrk
	    			<< " pT = " << pt << " d0 = " << d0 << " z = " << z
					<< " eta = " << eta << " phi = " << phi << " dR = " << dr <<std::endl;
					*/
	    	if(!pars.zRange.inside(z)) continue;
	    	if(pt < pars.ptMin) continue;
	    	if(!pars.rRange.inside(d0)) continue;
	    	if(dr > pars.drMax) continue;
	    	if(it->normalizedChi2() > pars.chi2NdofMax) continue;

	    	if(pt >1)std::cout << "  general track #" << itrk
	    			<< " selected! pT = " << pt << " d0 = " << d0 << " z = " << z
					<< " eta = " << eta << " phi = " << phi << " dR = " << dr <<std::endl;

	    	nSelectedTracksPt.push_back(pt);
	    }

	    if(sel_tracks.size() != nSelectedTracksPt.size()){
	    	std::cout << "self_selected_pt" << std::endl;
	    	for(auto pt: nSelectedTracksPt){
	    		std::cout << pt << std::endl;
	    	}
	    	std::cout << "auto_selected_pt" << std::endl;
	    	for(auto it = sel_tracks.begin(); it != sel_tracks.end(); ++it){
	    		std::cout << (*it)->pt() << std::endl;
	    	}
	    	std::cout << "object pT: " << momentum.Perp() << std::endl;
	    }
	    assert(sel_tracks.size() == nSelectedTracksPt.size() && "Error: Isolation Algorithms give different answers!");
	}

	// total pT from all other tracks within cone
	float sumGeneralPt = 0;
	for(auto it = sel_tracks.begin(); it != sel_tracks.end(); ++it){
		sumGeneralPt += (*it)->pt();
	}
	if(debug) std::cout << "isolation = " << sumGeneralPt/momentum.Perp() <<  " = " << sumGeneralPt << "/" << momentum.Perp() << std::endl;
	return sumGeneralPt/momentum.Perp();
}

/* @brief Remove a subset of tracks (tracksToRemove) from a general
 * collection of tracks (trackCollection), returning a collection
 * without those in tracksToRemove if matches are found in the main
 * collection.
 */
const reco::TrackCollection DimuonBranches::RemoveTracksFromCollection(
		const reco::TrackCollection& trackCollection,
		const std::vector<reco::Track>& tracksToRemove,	bool debug)
{
  //for now, just use dR matching
  //float DR_THRESHOLD = 0.1;
  float DR_THRESHOLD = 0.0;

  // Temp: dump all general tracks with pT > 5 GeV
  // unsigned int itrk = 0;
  // for (auto& track : trackCollection) {
  //   if (track.pt() > 5.)
  //     std::cout << " *** General track #" << itrk << " eta = " << track.eta()
  // 		<< " phi = " << track.phi() << " pT = " << track.pt()
  //		<< " ***" << std::endl;
  //   itrk++;
  // }

  reco::TrackCollection cleanedCollection;
  //this algorithm could remove more tracks in the collection than
  //there are tracks to remove, if the dR is small enough to match to
  //multiple tracks
  for(auto& trackInCollection : trackCollection){
    bool isClean = true;
    for(auto& trackToRemove: tracksToRemove){
      if (deltaR(trackInCollection.eta(), trackInCollection.phi(),
		 trackToRemove.eta(), trackToRemove.phi()) < DR_THRESHOLD) {
	isClean=false;
	break;
      }
    }
    if(isClean) {
      cleanedCollection.push_back(trackInCollection);
    }else{
      if(debug) std::cout << "removed track from collection with"
			  << " pT:" << trackInCollection.pt()
			  << " eta: " << trackInCollection.eta()
			  << " phi: " << trackInCollection.phi() << std::endl;
    }
  }
  return cleanedCollection;
}
