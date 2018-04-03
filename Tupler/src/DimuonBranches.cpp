#include "DisplacedDimuons/Tupler/interface/DimuonBranches.h"

void DimuonBranches::Fill(const edm::EventSetup& iSetup, const reco::TrackCollection &muons, const reco::VertexCollection &vertices)
{
	Reset();
	float mass = .105658375;

	edm::ESHandle<TransientTrackBuilder> ttB;
	iSetup.get<TransientTrackRecord>().get("TransientTrackBuilder", ttB);

	std::vector<reco::TransientTrack> ttV;
	std::vector<TLorentzVector> p4V;
	for (const auto &mu : muons)
	{
		TLorentzVector v(mu.px(), mu.py(), mu.pz(), pow(pow(mu.p(),2.)+pow(mass,2.),0.5));
		p4V.push_back(v);

		reco::TransientTrack tt = ttB->build(mu);
		ttV.push_back(tt);
	}

	for (unsigned int i=0; i<ttV.size(); i++)
	{
		for (unsigned int j=i+1; j<ttV.size(); j++)
		{
			// fit the secondary vertex
			KalmanVertexFitter kvf(true);
			std::vector<reco::TransientTrack> trackVector = { ttV[i], ttV[j] };
			TransientVertex tv = kvf.vertex(trackVector);
			reco::Vertex rv = tv;

			// cosine 3D opening angle: P1 . P2 / |P1| |P2|
			float cosAlpha = p4V[i].Vect().Dot(p4V[j].Vect())/p4V[i].P()/p4V[j].P();

			// SV-PV vector
			auto diffP = rv.position() - vertices.begin()->position();
			TVector3 diffV(diffP.X(), diffP.Y(), diffP.Z());

			// Lxy is just the magnitude in the XY plane
			float Lxy = diffV.Perp();

			// dimuon LorentzVector
			TLorentzVector p4 = p4V[i] + p4V[j];

			// |deltaPhi| needed TVectors
			float deltaPhi = fabs(diffV.DeltaPhi(p4.Vect()));

			// fill tree
			dim_idx1    .push_back(i                    );
			dim_idx2    .push_back(j                    );
			dim_pdgID   .push_back(6000113              );
			dim_pt      .push_back(p4.Pt              ());
			dim_eta     .push_back(p4.Eta             ());
			dim_phi     .push_back(p4.Phi             ());
			dim_mass    .push_back(p4.M               ());
			dim_energy  .push_back(p4.E               ());
			dim_charge  .push_back(0                    );
			dim_x       .push_back(rv.x               ());
			dim_y       .push_back(rv.y               ());
			dim_z       .push_back(rv.z               ());
			dim_Lxy     .push_back(Lxy                  );
			dim_deltaR  .push_back(p4V[i].DeltaR(p4V[j]));
			dim_normChi2.push_back(rv.normalizedChi2  ());
			dim_cosAlpha.push_back(cosAlpha             );
			dim_deltaPhi.push_back(deltaPhi             );
		}
	}
}
