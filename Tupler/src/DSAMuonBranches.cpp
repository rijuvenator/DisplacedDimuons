#include "DisplacedDimuons/Tupler/interface/DSAMuonBranches.h"

bool DSAMuonBranches::alreadyPrinted_ = false;

void DSAMuonBranches::Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
			   const edm::ESHandle<TransientTrackBuilder>& ttB,
			   const edm::Handle<reco::VertexCollection> &verticesHandle,
			   const edm::Handle<reco::BeamSpot> &beamspotHandle)
{
	static bool debug = false;
	Reset();

	// Check if failed to get
	// already checked if vertices are valid
	if (FailedToGet(muonsHandle)) return;
	const reco::TrackCollection &muons = *muonsHandle;
	const reco::VertexCollection &vertices = *verticesHandle;

	// Primary vertex; needed to calculate d0 and dz
	reco::Vertex pv = vertices.front();
	GlobalPoint pv_pos(pv.x(), pv.y(), pv.z());

	for (const auto &mu : muons)
	{
	        double p =
		  sqrt(pow(mu.px(),2.) + pow(mu.py(),2.) + pow(mu.pz(),2.));
		dsamu_pt    .push_back(mu.pt    () );
		dsamu_p     .push_back(p           );
		dsamu_eta   .push_back(mu.eta   () );
		dsamu_phi   .push_back(mu.phi   () );
		dsamu_charge.push_back(mu.charge() );
		dsamu_x     .push_back(mu.vx    () );
		dsamu_y     .push_back(mu.vy    () );
		dsamu_z     .push_back(mu.vz    () );
		dsamu_chi2  .push_back(mu.chi2  () );
		dsamu_ndof  .push_back(mu.ndof  () );

		int n_MuHits   = mu.hitPattern().numberOfValidMuonHits();
		int n_DTHits   = mu.hitPattern().numberOfValidMuonDTHits();
		int n_CSCHits  = mu.hitPattern().numberOfValidMuonCSCHits();
		int n_DTStats  = mu.hitPattern().dtStationsWithValidHits();
		int n_CSCStats = mu.hitPattern().cscStationsWithValidHits();
		dsamu_nMuonHits   .push_back(n_MuHits);
		dsamu_nDTHits     .push_back(n_DTHits);
		dsamu_nCSCHits    .push_back(n_CSCHits);
		dsamu_nDTStations .push_back(n_DTStats);
		dsamu_nCSCStations.push_back(n_CSCStats);

		// Get the transient track for extrapolations below
		reco::TransientTrack ttrack=ttB->build(mu);
		// Not sure we need to set the beam spot, but keep it for safety
		if (!FailedToGet(beamspotHandle))
		  ttrack.setBeamSpot(*beamspotHandle);

		// d0 and dz w.r.t. the primary vertex.  The track is
		// extrapolated to the closest point to the primary
		// vertex in transverse plane.
		double d0_pv = -999., d0err_pv = -999., d0sig_pv = -999.;
		// This gives the same result as the IPTools method below except for the sign
		// d0_pv    = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeParameters().transverseImpactParameter();
		// d0err_pv = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeError().transverseImpactParameterError();
		GlobalVector mu_dir(mu.px(), mu.py(), mu.pz());
		std::pair<bool, Measurement1D> ip2d = IPTools::signedTransverseImpactParameter(ttrack, mu_dir, pv);
                if (ip2d.first) {
		  d0_pv    = ip2d.second.value();
		  d0err_pv = ip2d.second.error();
		  d0sig_pv = fabs(d0_pv)/d0err_pv;
		}
		double dz_pv    = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeParameters().longitudinalImpactParameter();
		double dzerr_pv = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeError().longitudinalImpactParameterError();
		double dzsig_pv = fabs(dz_pv)/dzerr_pv;

		// d0 and dz w.r.t. the beam spot, again using extrapolation
		double d0_bs = -999., d0err_bs = -999., d0sig_bs = -999.;
		double dz_bs = -999., dzerr_bs = -999., dzsig_bs = -999.;
		if (!FailedToGet(beamspotHandle)) {
		  const reco::BeamSpot &beamspot = *beamspotHandle;
		  GlobalPoint bs_pos(beamspot.x0(), beamspot.y0(), beamspot.z0());
		  d0_bs    = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeParameters().transverseImpactParameter();
		  d0err_bs = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeError().transverseImpactParameterError();
		  d0sig_bs = fabs(d0_bs)/d0err_bs;

		  dz_bs    = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeParameters().longitudinalImpactParameter();
		  dzerr_bs = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeError().longitudinalImpactParameterError();
		  dzsig_bs = fabs(dz_bs)/dzerr_bs;
		}

		// d0 w.r.t. (0; 0) assuming that the trajectory is a
		// straight line
		// double d0    = mu.d0();
		// double d0sig = fabs(d0)/mu.d0Error();

		// d0 and dz w.r.t. the primary vertex assuming that
		// the trajectory is a straight line
		//auto maxVtx = std::min_element(vertices.begin(), vertices.end(), [] (const auto &v1, const auto &v2) {return v1.p4().Pt() < v2.p4().Pt(); });
		double d0_pv_lin    = mu.dxy(pv.position());
		double d0sig_pv_lin = fabs(d0_pv_lin)/mu.d0Error();
		double dz_pv_lin    = mu.dz(pv.position());
		double dzsig_pv_lin = fabs(dz_pv_lin)/mu.dzError();

		// d0 and dz w.r.t. the beam spot assuming that the
		// trajectory is a straight line
		double d0_bs_lin = -999., d0sig_bs_lin = -999.;
		double dz_bs_lin = -999., dzsig_bs_lin = -999.;
		if (!FailedToGet(beamspotHandle)) {
		  const reco::BeamSpot &beamspot = *beamspotHandle;
		  d0_bs_lin    = mu.dxy(beamspot);
		  d0sig_bs_lin = fabs(d0_bs_lin)/mu.d0Error();
		  dz_bs_lin    = mu.dz(beamspot.position());
		  dzsig_bs_lin = fabs(dz_bs_lin)/mu.dzError();
		}

		dsamu_d0_pv.push_back(fabs(d0_pv));
		dsamu_d0_bs.push_back(fabs(d0_bs));
		dsamu_d0_pv_lin.push_back(fabs(d0_pv_lin));
		dsamu_d0_bs_lin.push_back(fabs(d0_bs_lin));
		dsamu_d0sig_pv.push_back(d0sig_pv);
		dsamu_d0sig_bs.push_back(d0sig_bs);
		dsamu_d0sig_pv_lin.push_back(d0sig_pv_lin);
		dsamu_d0sig_bs_lin.push_back(d0sig_bs_lin);

		dsamu_dz_pv.push_back(fabs(dz_pv));
		dsamu_dz_bs.push_back(fabs(dz_bs));
		dsamu_dz_pv_lin.push_back(fabs(dz_pv_lin));
		dsamu_dz_bs_lin.push_back(fabs(dz_bs_lin));
		dsamu_dzsig_pv.push_back(dzsig_pv);
		dsamu_dzsig_bs.push_back(dzsig_bs);
		dsamu_dzsig_pv_lin.push_back(dzsig_pv_lin);
		dsamu_dzsig_bs_lin.push_back(dzsig_bs_lin);

		if (debug) {
		  std::cout << "DSA muon info: charge = " << mu.charge()
			    << " pt = "  << mu.pt()  << " p = "   << p
			    << " eta = " << mu.eta() << " phi = " << mu.phi()
			    << std::endl;
		  std::cout << "  (x; y; z): (" << mu.vx() << ";"
			    << mu.vy() << ";" << mu.vz()
			    << ") chi2/ndof = " << mu.chi2() << "/"
			    << mu.ndof() << std::endl;
		  std::cout << "  N(mu hits) = "  << n_MuHits
			    << "; N(DT hits) = "  << n_DTHits
			    << "; N(CSC hits) = " << n_CSCHits
			    << "; N(DTs with valid hits) = "  << n_DTStats
			    << "; N(CSCs with valid hits) = " << n_CSCStats
			    << std::endl;

		  std::cout << "  d0(PV; real extrap.) = "  << d0_pv
			    << " d0(PV) significance = " << d0sig_pv << "\n";
		  std::cout << "  d0(PV; lin extrap.) = "  << d0_pv_lin
			    << " d0(PV) significance = " << d0sig_pv_lin << "\n";
		  std::cout << "  d0(BS; real extrap.) = "  << d0_bs
			    << " d0(BS) significance = " << d0sig_bs << "\n";
		  std::cout << "  d0(BS; lin extrap.) = "  << d0_bs_lin
			    << " d0(BS) significance = " << d0sig_bs_lin << "\n";

		  std::cout << "  dz(PV; real extrap.) = "  << dz_pv
			    << " dz(PV) significance = " << dzsig_pv << "\n";
		  std::cout << "  dz(PV; lin extrap.) = "  << dz_pv_lin
			    << " dz(PV) significance = " << dzsig_pv_lin << "\n";
		  std::cout << "  dz(BS; real extrap.) = "  << dz_bs
			    << " dz(BS) significance = " << dzsig_bs << "\n";
		  std::cout << "  dz(BS; lin extrap.) = "  << dz_bs_lin
			    << " dz(BS) significance = " << dzsig_bs_lin << "\n";
		}
	}
}
