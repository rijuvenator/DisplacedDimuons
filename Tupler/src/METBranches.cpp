#include "DisplacedDimuons/Tupler/interface/METBranches.h"

bool METBranches::alreadyPrinted_ = false;

void METBranches::Fill(const edm::Handle<pat::METCollection> &patMETHandle,
		       const edm::TriggerResults &filterResults,
		       const edm::TriggerNames   &filterNames)
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

  // Event flags and MET filters
  for (unsigned int i = 0; i < filterResults.size(); i++) {
    /* std::cout << i << " " << filterNames.triggerName(i)
       << " accept " << filterResults.accept(i)<< std::endl; */
    const std::string filterName = filterNames.triggerName(i);
    if (filterName == "goodDataHLTPhysicsDeclared")
      flag_PhysicsDeclared = filterResults.accept(i);
    else if (filterName == "goodDataPrimaryVertexFilter")
      flag_PrimaryVertexFilter = filterResults.accept(i);
    else if (filterName == "goodDataMETFilter")
      flag_AllMETFilters = filterResults.accept(i);
    else if (filterName == "goodDataHBHENoiseFilter") 
      flag_HBHENoiseFilter    = filterResults.accept(i);
    else if (filterName == "goodDataHBHEIsoNoiseFilter")
      flag_HBHEIsoNoiseFilter = filterResults.accept(i);
    else if (filterName == "goodDataCSCTightHaloFilter")
      flag_CSCTightHaloFilter = filterResults.accept(i);
    else if (filterName == "goodDataEcalTPFilter")
      flag_EcalTPFilter = filterResults.accept(i);
    else if (filterName == "goodDataEeBadScFilter")
      flag_EeBadScFilter = filterResults.accept(i);
    else if (filterName == "goodDataBadPFMuonFilter")
      flag_BadPFMuonFilter = filterResults.accept(i);
    else if (filterName == "goodDataBadChargedCandidateFilter")
      flag_BadChargedCandidateFilter = filterResults.accept(i);
  }

  // Debug info
  if (debug) {
    std::cout << "MET info: MET = " << met_pt     << " MET phi = " << met_phi
	      << " gen MET = "      << met_gen_pt << std::endl;
    std::cout << " PhysicsDeclaredFlag = " << flag_PhysicsDeclared
	      << " PrimaryVertexFilter = " << flag_PrimaryVertexFilter
	      << " METFilters = "          << flag_AllMETFilters
	      << " HBHENoiseFilter = "     << flag_HBHENoiseFilter
	      << " HBHEIsoNoiseFilter = "  << flag_HBHEIsoNoiseFilter << "\n"
	      << " CSCTightHaloFilter = "  << flag_CSCTightHaloFilter
	      << " EcalTPFilter = "        << flag_EcalTPFilter
	      << " EeBadScFilter = "       << flag_EeBadScFilter
	      << " BadPFMuonFilter = "     << flag_BadPFMuonFilter
	      << " BadChargedCandidateFilter = "
	      << flag_BadChargedCandidateFilter << std::endl;
  }
}
