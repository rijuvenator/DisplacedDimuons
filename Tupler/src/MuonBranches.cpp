#include "DisplacedDimuons/Tupler/interface/MuonBranches.h"

bool MuonBranches::alreadyPrinted_ = false;

void MuonBranches::Fill(const edm::Handle<pat::MuonCollection> &muonsHandle)
{
	Reset();

	// Check if failed to get
	if (FailedToGet(muonsHandle)) return;
	const pat::MuonCollection &muons = *muonsHandle;

	for (const auto &mu : muons)
	{
		mu_pdgID .push_back(mu.pdgId ());
		mu_pt    .push_back(mu.pt    ());
		mu_eta   .push_back(mu.eta   ());
		mu_phi   .push_back(mu.phi   ());
		mu_mass  .push_back(mu.mass  ());
		mu_energy.push_back(mu.energy());
		mu_charge.push_back(mu.charge());
		mu_x     .push_back(mu.vx    ());
		mu_y     .push_back(mu.vy    ());
		mu_z     .push_back(mu.vz    ());

		mu_isSlim.push_back(isSlim(mu));

		const reco::GenParticle * gen = mu.genLepton();
		if (gen != 0)
		{
			mu_gen_pdgID .push_back(gen->pdgId ());
			mu_gen_pt    .push_back(gen->pt    ());
			mu_gen_eta   .push_back(gen->eta   ());
			mu_gen_phi   .push_back(gen->phi   ());
			mu_gen_mass  .push_back(gen->mass  ());
			mu_gen_energy.push_back(gen->energy());
			mu_gen_charge.push_back(gen->charge());
			mu_gen_x     .push_back(gen->vx    ());
			mu_gen_y     .push_back(gen->vy    ());
			mu_gen_z     .push_back(gen->vz    ());
		}
		else
		{
			mu_gen_pdgID .push_back(-999);
			mu_gen_pt    .push_back(-999);
			mu_gen_eta   .push_back(-999);
			mu_gen_phi   .push_back(-999);
			mu_gen_mass  .push_back(-999);
			mu_gen_energy.push_back(-999);
			mu_gen_charge.push_back(-999);
			mu_gen_x     .push_back(-999);
			mu_gen_y     .push_back(-999);
			mu_gen_z     .push_back(-999);
		}

	}
}

bool MuonBranches::isSlim(const pat::Muon &mu)
{
	bool isSlim = false;
	if (
			   (mu.pt() > 5.)
			|| (mu.pt() > 3. && (
								   mu.isPFMuon()
								|| mu.muonID("AllGlobalMuons")
								|| mu.muonID("AllArbitrated")
								|| mu.muonID("AllStandAloneMuons")
								|| mu.muonID("RPCMuLoose")
					)
			   )
			|| (mu.isPFMuon())
	   )
	{
		isSlim = true;
	}

	return isSlim;
}
