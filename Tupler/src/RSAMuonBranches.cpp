#include "DisplacedDimuons/Tupler/interface/RSAMuonBranches.h"

bool RSAMuonBranches::alreadyPrinted_ = false;

void RSAMuonBranches::Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
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

	unsigned int idx = 0;
	DisplacedMuonFiller muf;
	for (const auto &mu : muons)
  {
    DisplacedMuon muon_cand = muf.Fill(mu, ttB, verticesHandle, beamspotHandle, false);
    muon_cand.idx = idx++;
    if (debug)
      std::cout << "RSA muon info:" << muon_cand;

    rsamu_idx         .push_back(muon_cand.idx              );
    rsamu_px          .push_back(muon_cand.px               );
    rsamu_py          .push_back(muon_cand.py               );
    rsamu_pz          .push_back(muon_cand.pz               );
    rsamu_ptError     .push_back(muon_cand.ptError          );
    rsamu_eta         .push_back(muon_cand.eta              );
    rsamu_phi         .push_back(muon_cand.phi              );
    rsamu_charge      .push_back(muon_cand.charge           );
    rsamu_chi2        .push_back(muon_cand.chi2             );
    rsamu_ndof        .push_back(muon_cand.ndof             );

    rsamu_x           .push_back(muon_cand.x                );
    rsamu_y           .push_back(muon_cand.y                );
    rsamu_z           .push_back(muon_cand.z                );
    rsamu_x_fhit      .push_back(muon_cand.x_fhit           );
    rsamu_y_fhit      .push_back(muon_cand.y_fhit           );
    rsamu_z_fhit      .push_back(muon_cand.z_fhit           );

    rsamu_nMuonHits   .push_back(muon_cand.n_MuonHits       );
    rsamu_nDTHits     .push_back(muon_cand.n_DTHits         );
    rsamu_nCSCHits    .push_back(muon_cand.n_CSCHits        );
    rsamu_nDTStations .push_back(muon_cand.n_DTStations     );
    rsamu_nCSCStations.push_back(muon_cand.n_CSCStations    );

    rsamu_d0_pv       .push_back(fabs(muon_cand.d0_pv      ));
    rsamu_d0_bs       .push_back(fabs(muon_cand.d0_bs      ));
    rsamu_d0_pv_lin   .push_back(fabs(muon_cand.d0_pv_lin  ));
    rsamu_d0_bs_lin   .push_back(fabs(muon_cand.d0_bs_lin  ));
    rsamu_d0sig_pv    .push_back(     muon_cand.d0sig_pv    );
    rsamu_d0sig_bs    .push_back(     muon_cand.d0sig_bs    );
    rsamu_d0sig_pv_lin.push_back(     muon_cand.d0sig_pv_lin);
    rsamu_d0sig_bs_lin.push_back(     muon_cand.d0sig_bs_lin);

    rsamu_dz_pv       .push_back(fabs(muon_cand.dz_pv      ));
    rsamu_dz_bs       .push_back(fabs(muon_cand.dz_bs      ));
    rsamu_dz_pv_lin   .push_back(fabs(muon_cand.dz_pv_lin  ));
    rsamu_dz_bs_lin   .push_back(fabs(muon_cand.dz_bs_lin  ));
    rsamu_dzsig_pv    .push_back(     muon_cand.dzsig_pv    );
    rsamu_dzsig_bs    .push_back(     muon_cand.dzsig_bs    );
    rsamu_dzsig_pv_lin.push_back(     muon_cand.dzsig_pv_lin);
    rsamu_dzsig_bs_lin.push_back(     muon_cand.dzsig_bs_lin);
  }
}
