#include "DisplacedDimuons/Tupler/interface/DimuonBranches.h"

bool DimuonBranches::alreadyPrinted_ = false;

void DimuonBranches::Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
			  const edm::ESHandle<TransientTrackBuilder>& ttB,
			  const edm::Handle<reco::VertexCollection> &verticesHandle,
			  const edm::Handle<reco::BeamSpot> &beamspotHandle)
{
  Reset();
  static bool debug = false;
  static float mass = .105658375;

  // already checked if muons and vertices are valid
  const reco::TrackCollection &muons = *muonsHandle;
  const reco::VertexCollection &vertices = *verticesHandle;

  // Primary vertex
  reco::Vertex pv = vertices.front();

  // Setup Kalman vertex fitter and activate the refit of the tracks
  KalmanVertexFitter kvf(true);

  unsigned int i, j;
  reco::TrackCollection::const_iterator pmu, qmu;
  for (i = 0, pmu = muons.begin(); pmu != muons.end(); pmu++, i++) {
    reco::TransientTrack ott1 = ttB->build(*pmu);
    if (!ott1.isValid()) continue;
    // Not sure we need to set the beam spot, but do it to be on the safe side
    ott1.setBeamSpot(*beamspotHandle);

    for (j = i+1, qmu = pmu+1; qmu != muons.end(); qmu++, j++) {
      reco::TransientTrack ott2 = ttB->build(*qmu);
      if (!ott2.isValid()) continue;
      ott2.setBeamSpot(*beamspotHandle);

      // fit the secondary vertex
      std::vector<reco::TransientTrack> trackVector = {ott1, ott2};
      TransientVertex tv = kvf.vertex(trackVector);

      // Only store those dimuons for which the common-vertex fit
      // converged.  If the fit failed, all dimuon quantities can be
      // calculated later on from the info available in the
      // single-muon branches.
      if (tv.isValid()) {
	reco::Vertex rv = tv;
	float rv_x = rv.x();
	float rv_y = rv.y();
	float rv_z = rv.z();
	float rv_normChi2 = rv.normalizedChi2();

	// SV-PV vector
	auto diffP = rv.position() - pv.position();
	TVector3 diffV(diffP.X(), diffP.Y(), diffP.Z());

	// Distance between the primary and the dilepton vertices in
	// the transverse plane and its uncertainty
	VertexDistanceXY vdxy;
	Measurement1D vdist2d = vdxy.distance(pv, rv);
	float Lxy_pv    = vdist2d.value();
	float Lxysig_pv = vdist2d.significance();

	// Distance w.r.t. the beam spot and its uncertainty
	VertexState beamSpotState(*beamspotHandle);
	vdist2d = vdxy.distance(beamSpotState, rv);
	float Lxy_bs    = vdist2d.value();
	float Lxysig_bs = vdist2d.significance();

	// Refitted transient tracks
	reco::TransientTrack rtt1 = tv.refittedTrack(ott1);
	reco::TransientTrack rtt2 = tv.refittedTrack(ott2);
	TLorentzVector rt1_p4(rtt1.track().px(), rtt1.track().py(), rtt1.track().pz(), sqrt(pow(rtt1.track().p(),2.)+pow(mass,2.)));
	TLorentzVector rt2_p4(rtt2.track().px(), rtt2.track().py(), rtt2.track().pz(), sqrt(pow(rtt2.track().p(),2.)+pow(mass,2.)));

	// Dimuon 4-vector
	TLorentzVector dimu_p4 = rt1_p4 + rt2_p4;

	// |deltaPhi| needed TVectors
	float deltaPhi = fabs(diffV.DeltaPhi(dimu_p4.Vect()));

	// cosine 3D opening angle: P1 . P2 / |P1| |P2|
	float cosAlpha = rt1_p4.Vect().Dot(rt2_p4.Vect())/rt1_p4.P()/rt2_p4.P();

	// delta R between the tracks
	float deltaR = rt1_p4.DeltaR(rt2_p4);

	// fill tree
	dim_idx1     .push_back(i            );
	dim_idx2     .push_back(j            );
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
	dim_deltaPhi .push_back(deltaPhi     );
	dim_deltaR   .push_back(deltaR       );
	dim_cosAlpha .push_back(cosAlpha     );

	if (debug) {
	  std::cout << "Dimuon info: muon id's = " << i << " " << j
		    << " pt = "  << dimu_p4.Pt()  << " p = "   << dimu_p4.P()
		    << " eta = " << dimu_p4.Eta() << " phi = " << dimu_p4.Phi()
		    << " mass = " << dimu_p4.M() << std::endl;
	  std::cout << "  Common vertex: (x; y; z): ("
		    << rv_x << ";" << rv_y << ";" << rv_z 
		    << ") chi2/ndof = " << rv_normChi2 << std::endl;
	  std::cout << "  Lxy(PV) = "             << Lxy_pv
		    << " Lxy(PV) significance = " << Lxysig_pv
		    << " Lxy(BS) = "              << Lxy_bs
		    << " Lxy(BS) significance = " << Lxysig_bs << std::endl;
	  std::cout << "  dR = "  << deltaR << " dphi = " << deltaPhi
		    << " cos(alpha) = "  << cosAlpha << std::endl;
	}
      }
      else {
	if (debug) {
	  std::cout << "Dimuon info: common-vertex fit failed for muon id's = "
		    << i << " / " << j << std::endl;
	}
      }
    }
  }
}
