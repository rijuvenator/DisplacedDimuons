#include "DisplacedDimuons/Tupler/interface/DSAMuonBranches.h"

void DSAMuonBranches::Fill(const reco::TrackCollection &muons, const reco::VertexCollection &vertices)
{
	Reset();
	float mass = .105658375;
	for (const auto &mu : muons)
	{
		int   pdgID  = -13 * mu.charge()/fabs(mu.charge());
		float energy = pow(pow(mu.p(),2.) + pow(mass,2.), 0.5);

		dsamu_pdgID .push_back(        pdgID    );
		dsamu_pt    .push_back(     mu.pt    () );
		dsamu_eta   .push_back(     mu.eta   () );
		dsamu_phi   .push_back(     mu.phi   () );
		dsamu_mass  .push_back(        mass     );
		dsamu_energy.push_back(        energy   );
		dsamu_charge.push_back(     mu.charge() );
		dsamu_x     .push_back(     mu.vx    () );
		dsamu_y     .push_back(     mu.vy    () );
		dsamu_z     .push_back(     mu.vz    () );

		dsamu_d0    .push_back(fabs(mu.d0    ()));

		auto maxVtx = std::min_element(vertices.begin(), vertices.end(), [] (const auto &v1, const auto &v2) {return v1.p4().Pt() < v2.p4().Pt(); });
		dsamu_d0MV.push_back(fabs(mu.dxy(maxVtx->position())));

		dsamu_normChi2     .push_back(mu.normalizedChi2()                          );
		dsamu_d0Sig        .push_back(fabs(mu.d0())/mu.d0Error()                   );
		dsamu_d0MVSig      .push_back(fabs(mu.dxy(maxVtx->position()))/mu.d0Error());
		dsamu_nMuonHits    .push_back(mu.hitPattern().numberOfValidMuonHits()      );
		dsamu_nDTStations  .push_back(mu.hitPattern().dtStationsWithValidHits()    );
		dsamu_nCSCStations .push_back(mu.hitPattern().cscStationsWithValidHits()   );
	}
}
