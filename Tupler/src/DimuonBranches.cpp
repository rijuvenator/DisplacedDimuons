#include "DisplacedDimuons/Tupler/interface/DimuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

#include "DataFormats/Math/interface/deltaPhi.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "DataFormats/RecoCandidate/interface/IsoDepositDirection.h"
#include "RecoMuon/MuonIsolation/plugins/TrackSelector.h"
//TODO: Figure out how to just include library
#include "RecoMuon/MuonIsolation/plugins/TrackSelector.cc"

bool DimuonBranches::alreadyPrinted_ = false;

void DimuonBranches::Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
			  const edm::ESHandle<TransientTrackBuilder>& ttB,
			  const edm::Handle<reco::VertexCollection> &verticesHandle,
			  const edm::Handle<reco::BeamSpot> &beamspotHandle,
			  const edm::Handle<reco::TrackCollection> &generalTracksHandle)
{
  Reset();
  static bool debug = false;
  static float mass = .105658375;

  // already checked if muons, vertices, and beamspot are valid
  const reco::TrackCollection &muons = *muonsHandle;
  const reco::VertexCollection &vertices = *verticesHandle;
  const reco::BeamSpot &beamspot = *beamspotHandle;
  const reco::TrackCollection &generalTracks = *generalTracksHandle;

  // Primary vertex
  reco::Vertex pv = vertices.front();

  // Setup Kalman vertex fitter and activate the refit of the tracks
  KalmanVertexFitter kvf(true);

  DisplacedMuonFiller muf;

  unsigned int i, j;
  reco::TrackCollection::const_iterator pmu, qmu;
  for (i = 0, pmu = muons.begin(); pmu != muons.end(); pmu++, i++)
  {
    reco::TransientTrack ott1 = ttB->build(*pmu);
    if (!ott1.isValid()) continue;
    // Not sure we need to set the beam spot, but do it to be on the safe side
    ott1.setBeamSpot(beamspot);

    for (j = i+1, qmu = pmu+1; qmu != muons.end(); qmu++, j++)
    {
      reco::TransientTrack ott2 = ttB->build(*qmu);
      if (!ott2.isValid()) continue;
      ott2.setBeamSpot(beamspot);

      // fit the secondary vertex
      std::vector<reco::TransientTrack> trackVector = {ott1, ott2};
      TransientVertex tv;
      try
      {
        tv = kvf.vertex(trackVector);
      }
      catch ( VertexException & e )
      {
        edm::LogWarning("DimuonBranches")
          << "exception in common-vertex fit caught: " << e.what();
      }

      // Only store those dimuons for which the common-vertex fit
      // converged.  If the fit failed, all dimuon quantities can be
      // calculated later on from the info available in the
      // single-muon branches.
      if (tv.isValid())
      {
        reco::Vertex rv = tv;
        float rv_x = rv.x();
        float rv_y = rv.y();
        float rv_z = rv.z();
        float rv_normChi2 = rv.normalizedChi2();

        // SV-PV vector (math::XYZPoint)
        auto diffP = rv.position() - pv.position();

        // Distance between the primary and the dilepton vertices in
        // the transverse plane and its uncertainty
        VertexDistanceXY vdxy;
        Measurement1D vdist2d = vdxy.distance(pv, rv);
        float Lxy_pv    = vdist2d.value();
        float Lxysig_pv = vdist2d.significance();

        // Distance w.r.t. the beam spot and its uncertainty
        VertexState beamSpotState(beamspot);
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

        //Calculate dimuon isolation (using momentum direction to define cone)
        reco::isodeposit::Direction pmumuDir(dimu_p4.Eta(), dimu_p4.Phi());
        float dimuon_iso_pmumu = DimuonIsolation(pmumuDir, rv,dimu_p4, beamspot, generalTracks,debug);

        //Calculate dimuon isolation (using SV-PV to define cone)
        reco::isodeposit::Direction lxyDir(diffP.Eta(), diffP.Phi());
        float dimuon_iso_lxy = DimuonIsolation(lxyDir, rv,dimu_p4, beamspot, generalTracks,debug);

        // delta phi
        float dPhi = fabs(deltaPhi(diffP.Phi(), dimu_p4.Phi()));

        // cosine 3D opening angle: P1 . P2 / |P1| |P2|
        float cosAlpha = rt1_p4.Vect().Dot(rt2_p4.Vect())/rt1_p4.P()/rt2_p4.P();

        // delta R between the tracks
        float dR = rt1_p4.DeltaR(rt2_p4);

        // refitted muon candidates
        DisplacedMuon muon_cand1 = muf.Fill(rtt1.track(), ttB, verticesHandle, beamspotHandle);
        DisplacedMuon muon_cand2 = muf.Fill(rtt2.track(), ttB, verticesHandle, beamspotHandle);
        muon_cand1.idx = i;
        muon_cand2.idx = j;

        // Attempt to refit the primary vertex w/o the candidate muon
        // tracks.  Requires "reco::Tracks generalTracks" collection,
        // so disabled for now.
        // reco::Vertex rpv = RefittedVertex(ttB, pv, beamspot, ott1, ott2, debug);

        // fill tree
        // dimuon variables
        dim_pt       .push_back(dimu_p4.Pt ()    );
        dim_eta      .push_back(dimu_p4.Eta()    );
        dim_phi      .push_back(dimu_p4.Phi()    );
        dim_mass     .push_back(dimu_p4.M  ()    );
        dim_p        .push_back(dimu_p4.P  ()    );
        dim_x        .push_back(rv_x             );
        dim_y        .push_back(rv_y             );
        dim_z        .push_back(rv_z             );
        dim_normChi2 .push_back(rv_normChi2      );
        dim_Lxy_pv   .push_back(Lxy_pv           );
        dim_LxySig_pv.push_back(Lxysig_pv        );
        dim_Lxy_bs   .push_back(Lxy_bs           );
        dim_LxySig_bs.push_back(Lxysig_bs        );
        dim_deltaPhi .push_back(dPhi             );
        dim_deltaR   .push_back(dR               );
        dim_cosAlpha .push_back(cosAlpha         );
        dim_iso_pmumu.push_back(dimuon_iso_pmumu );
        dim_iso_lxy  .push_back(dimuon_iso_lxy   );

        // First muon candidate resulting from the common-vertex fit.
        // The refitted track does not have chi2, ndof, and hitpattern
        // set; the reference point of the track is identical to the
        // position of the refitted vertex.
        dim_mu1_idx         .push_back(     muon_cand1.idx         );
        dim_mu1_px          .push_back(     muon_cand1.px          );
        dim_mu1_py          .push_back(     muon_cand1.py          );
        dim_mu1_pz          .push_back(     muon_cand1.pz          );
        dim_mu1_ptError     .push_back(     muon_cand1.ptError     );
        dim_mu1_eta         .push_back(     muon_cand1.eta         );
        dim_mu1_phi         .push_back(     muon_cand1.phi         );
        dim_mu1_charge      .push_back(     muon_cand1.charge      );
        dim_mu1_d0_pv       .push_back(fabs(muon_cand1.d0_pv      ));
        dim_mu1_d0_bs       .push_back(fabs(muon_cand1.d0_bs      ));
        dim_mu1_d0_pv_lin   .push_back(fabs(muon_cand1.d0_pv_lin  ));
        dim_mu1_d0_bs_lin   .push_back(fabs(muon_cand1.d0_bs_lin  ));
        dim_mu1_d0sig_pv    .push_back(     muon_cand1.d0sig_pv    );
        dim_mu1_d0sig_bs    .push_back(     muon_cand1.d0sig_bs    );
        dim_mu1_d0sig_pv_lin.push_back(     muon_cand1.d0sig_pv_lin);
        dim_mu1_d0sig_bs_lin.push_back(     muon_cand1.d0sig_bs_lin);
        dim_mu1_dz_pv       .push_back(fabs(muon_cand1.dz_pv      ));
        dim_mu1_dz_bs       .push_back(fabs(muon_cand1.dz_bs      ));
        dim_mu1_dz_pv_lin   .push_back(fabs(muon_cand1.dz_pv_lin  ));
        dim_mu1_dz_bs_lin   .push_back(fabs(muon_cand1.dz_bs_lin  ));
        dim_mu1_dzsig_pv    .push_back(     muon_cand1.dzsig_pv    );
        dim_mu1_dzsig_bs    .push_back(     muon_cand1.dzsig_bs    );
        dim_mu1_dzsig_pv_lin.push_back(     muon_cand1.dzsig_pv_lin);
        dim_mu1_dzsig_bs_lin.push_back(     muon_cand1.dzsig_bs_lin);

        // second muon candidate resulting from the common-vertex fit
        dim_mu2_idx         .push_back(     muon_cand2.idx         );
        dim_mu2_px          .push_back(     muon_cand2.px          );
        dim_mu2_py          .push_back(     muon_cand2.py          );
        dim_mu2_pz          .push_back(     muon_cand2.pz          );
        dim_mu2_ptError     .push_back(     muon_cand2.ptError     );
        dim_mu2_eta         .push_back(     muon_cand2.eta         );
        dim_mu2_phi         .push_back(     muon_cand2.phi         );
        dim_mu2_charge      .push_back(     muon_cand2.charge      );
        dim_mu2_d0_pv       .push_back(fabs(muon_cand2.d0_pv      ));
        dim_mu2_d0_bs       .push_back(fabs(muon_cand2.d0_bs      ));
        dim_mu2_d0_pv_lin   .push_back(fabs(muon_cand2.d0_pv_lin  ));
        dim_mu2_d0_bs_lin   .push_back(fabs(muon_cand2.d0_bs_lin  ));
        dim_mu2_d0sig_pv    .push_back(     muon_cand2.d0sig_pv    );
        dim_mu2_d0sig_bs    .push_back(     muon_cand2.d0sig_bs    );
        dim_mu2_d0sig_pv_lin.push_back(     muon_cand2.d0sig_pv_lin);
        dim_mu2_d0sig_bs_lin.push_back(     muon_cand2.d0sig_bs_lin);
        dim_mu2_dz_pv       .push_back(fabs(muon_cand2.dz_pv      ));
        dim_mu2_dz_bs       .push_back(fabs(muon_cand2.dz_bs      ));
        dim_mu2_dz_pv_lin   .push_back(fabs(muon_cand2.dz_pv_lin  ));
        dim_mu2_dz_bs_lin   .push_back(fabs(muon_cand2.dz_bs_lin  ));
        dim_mu2_dzsig_pv    .push_back(     muon_cand2.dzsig_pv    );
        dim_mu2_dzsig_bs    .push_back(     muon_cand2.dzsig_bs    );
        dim_mu2_dzsig_pv_lin.push_back(     muon_cand2.dzsig_pv_lin);
        dim_mu2_dzsig_bs_lin.push_back(     muon_cand2.dzsig_bs_lin);

        if (debug)
        {
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
          std::cout << "  dR = "         << dR       << " dphi = " << dPhi
              << " cos(alpha) = "  << cosAlpha << std::endl;
          std::cout << "Pmumu Isolation: " << dimuon_iso_pmumu << std::endl;
          std::cout << "Lxy   Isolation: " << dimuon_iso_lxy << std::endl;
          std::cout << "Refitted DSA muon info:" << muon_cand1;
          std::cout << "Refitted DSA muon info:" << muon_cand2;
        }
      }
      else
      {
        if (debug)
        {
          std::cout << "Dimuon info: common-vertex fit failed for muon id's = "
              << i << " / " << j << std::endl;
        }
      }
    }
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


using namespace muonisolation;
/* @brief Determines if a dimuon, described with decay vertex rv, and momentum dimuon
 * is isolated with respect to other tracks found within the event.
 *
 * Function modelled from:
 *
 * https://github.com/cms-sw/cmssw/blob/f092629e3aac118bcf206450291a0c042c87769d/RecoMuon/MuonIsolation/plugins/TrackExtractor.cc
 *
 * returns (Sum of other tracks momentum in cone) / (Sum of dimuon momentum)
 */
float DimuonBranches::DimuonIsolation(
		const reco::isodeposit::Direction& isoConeDirection,
		const reco::Vertex& rv,
		const TLorentzVector& dimuon,
		const reco::BeamSpot &beamspot,
		const reco::TrackCollection &generalTracks,
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

	const float vtx_z = rv.z();

	//currently using direction of momentum to define cone
	//reco::isodeposit::Direction muonDir(dimuon.Eta(), dimuon.Phi());

	TrackSelector::Parameters pars(TrackSelector::Range(vtx_z-diffZ, vtx_z+diffZ),
			diffR, isoConeDirection, dRmax,beamspot.position());

	pars.nHitsMin = nHitsMin;
	pars.chi2NdofMax = chi2NdofMax;
	pars.chi2ProbMin = chi2ProbMin;
	pars.ptMin = ptMin;

	TrackSelector selection(pars);
	TrackSelector::result_type sel_tracks = selection(generalTracks);

	if(debug) std::cout << "Isolation - All Tracks: " << generalTracks.size()
			<< " Selected tracks for Dimuon Isolation: " << sel_tracks.size() << std::endl;


	//total Pt from all other tracks within cone
	float sumGeneralPt = 0;
	for(auto it = sel_tracks.begin(); it != sel_tracks.end(); ++it){
		sumGeneralPt += (*it)->pt();
	}

	return sumGeneralPt/dimuon.Perp();
}
