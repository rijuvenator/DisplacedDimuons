#include "DisplacedDimuons/Tupler/interface/GenBranches.h"

namespace PDGID
{
	const int MUON   = 13;
	const int LLX    = 6000113;
	const int HIGGS  = 35;
	const int PROTON = 2212;
}

void GenBranches::Fill(const reco::GenParticleCollection &gens, const GenEventInfoProduct &GEIP)
{
	Reset();

	// set gen weight
	gen_weight = GEIP.weight();

	// find P -> H -> XX -> 4Mu particles
	// muAll is for all muons
	std::vector<const reco::GenParticle*> muAll;
	const reco::GenParticle *mu11 = nullptr;
	const reco::GenParticle *mu12 = nullptr;
	const reco::GenParticle *mu21 = nullptr;
	const reco::GenParticle *mu22 = nullptr;
	const reco::Candidate   *X1   = nullptr;
	const reco::Candidate   *X2   = nullptr;
	const reco::Candidate   *H    = nullptr;
	const reco::Candidate   *P    = nullptr;

	// loop over the gen particles and look for muons
	for (const auto &gen : gens)
	{
		if (abs(gen.pdgId()) == PDGID::MUON and gen.status() == 1)
		{
			muAll.push_back(&gen);

			// p will be a dummy changeable pointer to a particle
			// first look for the mother X, then based on the pointer addresses,
			// set the appropriate X and mu pointers. then look for Higgs, then proton
			const reco::Candidate *p = &gen;
			while (p->pdgId() != PDGID::LLX && p->numberOfMothers() != 0) { p = p->mother(); }
			if (p->pdgId() == PDGID::LLX)
			{
				if      (X1 == nullptr) { X1 = p; mu11 = &gen; } // X1 == 0                                  --> found mu11
				else if (p  == X1     ) {         mu12 = &gen; } // X1 != 0 && p == X1                       --> found mu12
				else if (X2 == nullptr) { X2 = p; mu21 = &gen; } // X1 != 0 && p != X1 && X2 == 0            --> found mu21
				else if (p  == X2     ) {         mu22 = &gen; } // X2 != 0 && p != X1 && X2 != 0 && p == X2 --> found mu22

				if (H == nullptr && p->numberOfMothers() != 0)
				{
					p = p->mother();
					H = p;
					while (abs(p->pdgId()) != PDGID::PROTON) { p = p->mother(); }
					P = p;
				}
			}
		}
	}

	// make sure all pointers are non-null
	if (mu11 == nullptr || mu12 == nullptr ||
		mu21 == nullptr || mu22 == nullptr ||
		X1   == nullptr || X2   == nullptr ||
		H    == nullptr || P    == nullptr)
	{
		edm::LogWarning("NTupler::GenBranches") << "+++ Warning: At least one pointer is null. Filling nothing. +++";
		return;
	}

	// fill the branches: mu11, mu12, mu21, mu22, X1, X2, H, and P
	// and any additional muons
	std::vector<const reco::Candidate*> particles = {mu11, mu12, mu21, mu22, X1, X2, H, P};
	if (muAll.size() > 4)
	{
		for (const auto &mu : muAll)
		{
			if (std::find(particles.begin(), particles.end(), mu) == particles.end())
			{
				particles.push_back(mu);
			}
		}
	}
	for (const auto &p : particles)
	{
		gen_pdgID .push_back(p->pdgId ());
		gen_pt    .push_back(p->pt    ());
		gen_eta   .push_back(p->eta   ());
		gen_phi   .push_back(p->phi   ());
		gen_mass  .push_back(p->mass  ());
		gen_energy.push_back(p->energy());
		gen_charge.push_back(p->charge());
		gen_x     .push_back(p->vx    ());
		gen_y     .push_back(p->vy    ());
		gen_z     .push_back(p->vz    ());
	}

	// fill d0

	TVector3 disp1(mu11->vx() - X1->vx(), mu11->vy() - X1->vy(), 0.);
	TVector3 disp2(mu21->vx() - X2->vx(), mu21->vy() - X2->vy(), 0.);
	TVector3 zero1(mu11->vx()           , mu11->vy()           , 0.);
	TVector3 zero2(mu21->vx()           , mu21->vy()           , 0.);

	TVector3 p11  (mu11->px()           , mu11->py()           , 0.);
	TVector3 p12  (mu12->px()           , mu12->py()           , 0.);
	TVector3 p21  (mu21->px()           , mu21->py()           , 0.);
	TVector3 p22  (mu22->px()           , mu22->py()           , 0.);

	float d11 = disp1.Cross(p11).Mag()/p11.Mag();
	float d12 = disp1.Cross(p12).Mag()/p12.Mag();
	float d21 = disp2.Cross(p21).Mag()/p21.Mag();
	float d22 = disp2.Cross(p22).Mag()/p22.Mag();

	gen_d0.push_back(d11);
	gen_d0.push_back(d12);
	gen_d0.push_back(d21);
	gen_d0.push_back(d22);

	d11 = zero1.Cross(p11).Mag()/p11.Mag();
	d12 = zero1.Cross(p12).Mag()/p12.Mag();
	d21 = zero2.Cross(p21).Mag()/p21.Mag();
	d22 = zero2.Cross(p22).Mag()/p22.Mag();

	gen_d00.push_back(d11);
	gen_d00.push_back(d12);
	gen_d00.push_back(d21);
	gen_d00.push_back(d22);

	// fill pair delta R
	
	float dR1 = TVector3(mu11->px(), mu11->py(), mu11->pz()).DeltaR(TVector3(mu12->px(), mu12->py(), mu12->pz()));
	float dR2 = TVector3(mu21->px(), mu21->py(), mu21->pz()).DeltaR(TVector3(mu22->px(), mu22->py(), mu22->pz()));
	gen_pairDeltaR.push_back(dR1);
	gen_pairDeltaR.push_back(dR1);
	gen_pairDeltaR.push_back(dR2);
	gen_pairDeltaR.push_back(dR2);
	
}
