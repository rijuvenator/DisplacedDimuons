#ifndef ISOLATIONBRANCHES_H
#define ISOLATIONBRANCHES_H


// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// isolation branch collection
class IsolationBranches : public BranchCollection
{
	public:
		// constructor
		IsolationBranches(TreeContainer &tree, const bool DECLARE=true) :
			BranchCollection(tree, "TODO", "TODO")
		{
			Reset();
			if (DECLARE) Declarations();
		}

		// members
		static bool alreadyPrinted_;

		/*
		float bs_x ;
		float bs_y ;
		float bs_z ;
		float bs_dx;
		float bs_dy;
		float bs_dz;
		*/

		// methods
		void Declarations()
		{
			/*
			Declare("bs_x" , bs_x , "F");
			Declare("bs_y" , bs_y , "F");
			Declare("bs_z" , bs_z , "F");
			Declare("bs_dx", bs_dx, "F");
			Declare("bs_dy", bs_dy, "F");
			Declare("bs_dz", bs_dz, "F");
			*/
		}

		void Reset()
		{
			/*
			bs_x  = -999.;
			bs_y  = -999.;
			bs_z  = -999.;
			bs_dx = -999.;
			bs_dy = -999.;
			bs_dz = -999.;
			*/
		}

		//void Fill(const edm::Handle<reco::BeamSpot> &beamspotHandle);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
