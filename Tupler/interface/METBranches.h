#ifndef METBRANCHES_H
#define METBRANCHES_H

// CMSSW includes
#include "DataFormats/PatCandidates/interface/MET.h"

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

		float met_pt    ;
		float met_phi   ;
		float met_gen_pt;

		// methods
		void Declarations()
		{
			Declare("met_pt"    , met_pt    , "F");
			Declare("met_phi"   , met_phi   , "F");
			Declare("met_gen_pt", met_gen_pt, "F");
		}

		void Reset()
		{
			met_pt     = -999.;
			met_phi    = -999.;
			met_gen_pt = -999.;
		}

		void Fill(const edm::Handle<pat::METCollection> &patMETHandle);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
