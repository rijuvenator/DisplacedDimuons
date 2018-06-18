#ifndef METBRANCHES_H
#define METBRANCHES_H

// CMSSW includes
#include "DataFormats/PatCandidates/interface/MET.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// MET branch collection
class METBranches : public BranchCollection
{
 public:
  // constructor
 METBranches(TreeContainer &tree, const bool DECLARE=true) :
  BranchCollection(tree, "pat::METs collection", "MET info will not be filled")
    {
      Reset();
      if (DECLARE) Declarations();
    }

  // members
  static bool alreadyPrinted_;

  // MET, MET phi, and true MET
  float met_pt     ;
  float met_phi    ;
  float met_gen_pt ;

  // Event flags and MET filters
  int flag_PhysicsDeclared           ;
  int flag_PrimaryVertexFilter       ;
  int flag_AllMETFilters             ; // "AND" of the filters below
  int flag_HBHENoiseFilter           ;
  int flag_HBHEIsoNoiseFilter        ;
  int flag_CSCTightHaloFilter        ;
  int flag_EcalTPFilter              ;
  int flag_EeBadScFilter             ;
  int flag_BadPFMuonFilter           ;
  int flag_BadChargedCandidateFilter ;

  // methods
  void Declarations()
  {
    Declare("met_pt"    , met_pt    , "F");
    Declare("met_phi"   , met_phi   , "F");
    Declare("met_gen_pt", met_gen_pt, "F");

    Declare("flag_PhysicsDeclared"    , flag_PhysicsDeclared    , "I");
    Declare("flag_PrimaryVertexFilter", flag_PrimaryVertexFilter, "I");
    Declare("flag_AllMETFilters"      , flag_AllMETFilters      , "I");
    Declare("flag_HBHENoiseFilter"    , flag_HBHENoiseFilter    , "I");
    Declare("flag_HBHEIsoNoiseFilter" , flag_HBHEIsoNoiseFilter , "I");
    Declare("flag_CSCTightHaloFilter" , flag_CSCTightHaloFilter , "I");
    Declare("flag_EcalTPFilter"       , flag_EcalTPFilter       , "I");
    Declare("flag_EeBadScFilter"      , flag_EeBadScFilter      , "I");
    Declare("flag_BadPFMuonFilter"    , flag_BadPFMuonFilter    , "I");
    Declare("flag_BadChargedCandidateFilter", flag_BadChargedCandidateFilter, "I");
  }

  void Reset()
  {
    met_pt     = -999.;
    met_phi    = -999.;
    met_gen_pt = -999.;

    flag_PhysicsDeclared           = -999;
    flag_PrimaryVertexFilter       = -999;
    flag_AllMETFilters             = -999;
    flag_HBHENoiseFilter           = -999;
    flag_HBHEIsoNoiseFilter        = -999;
    flag_CSCTightHaloFilter        = -999;
    flag_EcalTPFilter              = -999;
    flag_EeBadScFilter             = -999;
    flag_BadPFMuonFilter           = -999;
    flag_BadChargedCandidateFilter = -999;
  }

  void Fill(const edm::Handle<pat::METCollection> &patMETHandle,
	    const edm::TriggerResults &filterResults,
	    const edm::TriggerNames   &filterNames);

  virtual bool alreadyPrinted() { return alreadyPrinted_; }
  virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
