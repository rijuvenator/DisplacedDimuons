#include "DisplacedDimuons/Tupler/interface/RSAMuonBranches.h"

void RSAMuonBranches::Fill(const reco::TrackCollection &muons, const reco::VertexCollection &vertices)
{
	Reset();
	float mass = .105658375;
	for (const auto &mu : muons)
	{
		int   pdgID  = -13 * mu.charge()/fabs(mu.charge());
		float energy = pow(pow(mu.p(),2.) + pow(mass,2.), 0.5);

		rsamu_pdgID .push_back(        pdgID    );
		rsamu_pt    .push_back(     mu.pt    () );
		rsamu_eta   .push_back(     mu.eta   () );
		rsamu_phi   .push_back(     mu.phi   () );
		rsamu_mass  .push_back(        mass     );
		rsamu_energy.push_back(        energy   );
		rsamu_charge.push_back(     mu.charge() );
		rsamu_x     .push_back(     mu.vx    () );
		rsamu_y     .push_back(     mu.vy    () );
		rsamu_z     .push_back(     mu.vz    () );

		rsamu_d0    .push_back(fabs(mu.d0    ()));

		//auto maxVtx = std::min_element(vertices.begin(), vertices.end(), [] (const auto &v1, const auto &v2) {return v1.p4().Pt() < v2.p4().Pt(); });
		auto maxVtx = vertices.begin();
		rsamu_d0MV.push_back(fabs(mu.dxy(maxVtx->position())));

		rsamu_normChi2     .push_back(mu.normalizedChi2()                          );
		rsamu_d0Sig        .push_back(fabs(mu.d0())/mu.d0Error()                   );
		rsamu_d0MVSig      .push_back(fabs(mu.dxy(maxVtx->position()))/mu.d0Error());
		rsamu_nMuonHits    .push_back(mu.hitPattern().numberOfValidMuonHits()      );
		rsamu_nDTStations  .push_back(mu.hitPattern().dtStationsWithValidHits()    );
		rsamu_nCSCStations .push_back(mu.hitPattern().cscStationsWithValidHits()   );
	}
}
