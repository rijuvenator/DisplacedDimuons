#include "DisplacedDimuons/Tupler/interface/DGBMuonBranches.h"

bool DGBMuonBranches::alreadyPrinted_ = false;

void DGBMuonBranches::Fill(const edm::Handle<reco::TrackCollection> &muonsHandle,
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
	std::cout << "DGB muon info:" << muon_cand;

      dgbmu_idx         .push_back(muon_cand.idx              );
      dgbmu_px          .push_back(muon_cand.px               );
      dgbmu_py          .push_back(muon_cand.py               );
      dgbmu_pz          .push_back(muon_cand.pz               );
      dgbmu_ptError     .push_back(muon_cand.ptError          );
      dgbmu_eta         .push_back(muon_cand.eta              );
      dgbmu_phi         .push_back(muon_cand.phi              );
      dgbmu_charge      .push_back(muon_cand.charge           );
      dgbmu_chi2        .push_back(muon_cand.chi2             );
      dgbmu_ndof        .push_back(muon_cand.ndof             );

      dgbmu_x           .push_back(muon_cand.x                );
      dgbmu_y           .push_back(muon_cand.y                );
      dgbmu_z           .push_back(muon_cand.z                );
      dgbmu_x_fhit      .push_back(muon_cand.x_fhit           );
      dgbmu_y_fhit      .push_back(muon_cand.y_fhit           );
      dgbmu_z_fhit      .push_back(muon_cand.z_fhit           );

      dgbmu_nMuonHits   .push_back(muon_cand.n_MuonHits       );
      dgbmu_nDTHits     .push_back(muon_cand.n_DTHits         );
      dgbmu_nCSCHits    .push_back(muon_cand.n_CSCHits        );
      dgbmu_nDTStations .push_back(muon_cand.n_DTStations     );
      dgbmu_nCSCStations.push_back(muon_cand.n_CSCStations    );

      dgbmu_d0_pv       .push_back(fabs(muon_cand.d0_pv      ));
      dgbmu_d0_bs       .push_back(fabs(muon_cand.d0_bs      ));
      dgbmu_d0_pv_lin   .push_back(fabs(muon_cand.d0_pv_lin  ));
      dgbmu_d0_bs_lin   .push_back(fabs(muon_cand.d0_bs_lin  ));
      dgbmu_d0sig_pv    .push_back(     muon_cand.d0sig_pv    );
      dgbmu_d0sig_bs    .push_back(     muon_cand.d0sig_bs    );
      dgbmu_d0sig_pv_lin.push_back(     muon_cand.d0sig_pv_lin);
      dgbmu_d0sig_bs_lin.push_back(     muon_cand.d0sig_bs_lin);

      dgbmu_dz_pv       .push_back(fabs(muon_cand.dz_pv      ));
      dgbmu_dz_bs       .push_back(fabs(muon_cand.dz_bs      ));
      dgbmu_dz_pv_lin   .push_back(fabs(muon_cand.dz_pv_lin  ));
      dgbmu_dz_bs_lin   .push_back(fabs(muon_cand.dz_bs_lin  ));
      dgbmu_dzsig_pv    .push_back(     muon_cand.dzsig_pv    );
      dgbmu_dzsig_bs    .push_back(     muon_cand.dzsig_bs    );
      dgbmu_dzsig_pv_lin.push_back(     muon_cand.dzsig_pv_lin);
      dgbmu_dzsig_bs_lin.push_back(     muon_cand.dzsig_bs_lin);
  }
}
