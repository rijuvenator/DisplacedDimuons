#ifndef BEAMSPOTBRANCHES_H
#define BEAMSPOTBRANCHES_H

// CMSSW includes
#include "DataFormats/BeamSpot/interface/BeamSpot.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// beamspot branch collection
class BeamspotBranches : BranchCollection
{
	public:
		// constructor
		BeamspotBranches(TreeContainer &tree, const bool DECLARE=true) : BranchCollection(tree, DECLARE) {}

		// members
		float bs_x    ;
		float bs_y    ;
		float bs_z    ;
		float bs_x_err;
		float bs_y_err;
		float bs_z_err;

		// methods
		virtual void Declarations()
		{
			Declare("bs_x"    , bs_x    , "F");
			Declare("bs_y"    , bs_y    , "F");
			Declare("bs_z"    , bs_z    , "F");
			Declare("bs_x_err", bs_x_err, "F");
			Declare("bs_y_err", bs_y_err, "F");
			Declare("bs_z_err", bs_z_err, "F");
		}

		virtual void Reset()
		{
			bs_x     = -999.;
			bs_y     = -999.;
			bs_z     = -999.;
			bs_x_err = -999.;
			bs_y_err = -999.;
			bs_z_err = -999.;
		}

		void Fill(const reco::BeamSpot &beamspot);
};

#endif
