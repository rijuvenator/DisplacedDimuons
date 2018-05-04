#include "DisplacedDimuons/Tupler/interface/METBranches.h"

bool METBranches::alreadyPrinted_ = false;

void METBranches::Fill(const edm::Handle<pat::METCollection> &patMETHandle)
{
	static bool debug = false;
	Reset();

	// Check if failed to get
	if (FailedToGet(patMETHandle)) return;

	// Expect only one element
	if (patMETHandle->size() != 1)
		throw cms::Exception("CorruptData", "More than one MET in the pat::METs collection");

	// Expect PF MET; check if this is true
	auto MET = patMETHandle->begin();
	if (!patMETHandle->begin()->isPFMET())
		edm::LogWarning("SimpleNTupler::METBranches")
			<< "+++ Warning: stored MET is not PFMET! +++";

	// Fill MET info
	met_pt  = MET->pt();
	met_phi = MET->phi();
	const reco::GenMET *genMET = MET->genMET();
	if (genMET != NULL)
		met_gen_pt = genMET->pt();

	// Debug info
	if (debug)
		std::cout
			<< "MET info: MET = " << met_pt
			<< " MET phi = "      << met_phi
			<< " gen MET = "      << met_gen_pt
			<< std::endl;
}
