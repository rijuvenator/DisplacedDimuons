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
	//const reco::VertexCollection &vertices = *verticesHandle;

	// Primary vertex; needed to calculate d0 and dz
	//reco::Vertex pv = vertices.front();

	unsigned int idx = 0;
	DisplacedMuonFiller muf;
	for (const auto &mu : muons)
	  {
	    DisplacedMuon muon_cand = muf.Fill(mu, ttB, verticesHandle, beamspotHandle);
	    muon_cand.idx = idx++;
	    if (debug)
	      std::cout << "DSA muon info:" << muon_cand;

	    dsamu_idx    .push_back(muon_cand.idx    );
	    dsamu_px     .push_back(muon_cand.px     );
	    dsamu_py     .push_back(muon_cand.py     );
	    dsamu_pz     .push_back(muon_cand.pz     );
	    dsamu_ptError.push_back(muon_cand.ptError);
	    dsamu_eta    .push_back(muon_cand.eta    );
	    dsamu_phi    .push_back(muon_cand.phi    );
	    dsamu_charge .push_back(muon_cand.charge );
	    dsamu_chi2   .push_back(muon_cand.chi2   );
	    dsamu_ndof   .push_back(muon_cand.ndof   );

	    dsamu_x      .push_back(muon_cand.x      );
	    dsamu_y      .push_back(muon_cand.y      );
	    dsamu_z      .push_back(muon_cand.z      );
	    dsamu_x_fhit .push_back(muon_cand.x_fhit );
	    dsamu_y_fhit .push_back(muon_cand.y_fhit );
	    dsamu_z_fhit .push_back(muon_cand.z_fhit );

	    dsamu_nMuonHits   .push_back(muon_cand.n_MuonHits);
	    dsamu_nDTHits     .push_back(muon_cand.n_DTHits);
	    dsamu_nCSCHits    .push_back(muon_cand.n_CSCHits);
	    dsamu_nDTStations .push_back(muon_cand.n_DTStations);
	    dsamu_nCSCStations.push_back(muon_cand.n_CSCStations);

	    dsamu_d0_pv.push_back(fabs(muon_cand.d0_pv));
	    dsamu_d0_bs.push_back(fabs(muon_cand.d0_bs));
	    dsamu_d0_pv_lin.push_back(fabs(muon_cand.d0_pv_lin));
	    dsamu_d0_bs_lin.push_back(fabs(muon_cand.d0_bs_lin));
	    dsamu_d0sig_pv.push_back(muon_cand.d0sig_pv);
	    dsamu_d0sig_bs.push_back(muon_cand.d0sig_bs);
	    dsamu_d0sig_pv_lin.push_back(muon_cand.d0sig_pv_lin);
	    dsamu_d0sig_bs_lin.push_back(muon_cand.d0sig_bs_lin);

	    dsamu_dz_pv.push_back(fabs(muon_cand.dz_pv));
	    dsamu_dz_bs.push_back(fabs(muon_cand.dz_bs));
	    dsamu_dz_pv_lin.push_back(fabs(muon_cand.dz_pv_lin));
	    dsamu_dz_bs_lin.push_back(fabs(muon_cand.dz_bs_lin));
	    dsamu_dzsig_pv.push_back(muon_cand.dzsig_pv);
	    dsamu_dzsig_bs.push_back(muon_cand.dzsig_bs);
	    dsamu_dzsig_pv_lin.push_back(muon_cand.dzsig_pv_lin);
	    dsamu_dzsig_bs_lin.push_back(muon_cand.dzsig_bs_lin);
	  }
}
