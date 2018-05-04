#ifndef VERTEXBRANCHES_H
#define VERTEXBRANCHES_H

// CMSSW includes
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/TreeContainer.h"
#include "DisplacedDimuons/Tupler/interface/BranchCollection.h"

// vertex branch collection
class VertexBranches : public BranchCollection
{
	public:
		// constructor
		VertexBranches(TreeContainer &tree, const bool DECLARE=true) :
			BranchCollection(tree, "reco::Vertex collection", "Vertex info will not be filled")
		{
			Reset();
			if (DECLARE) Declarations();
		}

		// members
		static bool alreadyPrinted_;

		int   vtx_nvtx;
		float vtx_pv_x;
		float vtx_pv_y;
		float vtx_pv_z;
		float vtx_pv_dx;
		float vtx_pv_dy;
		float vtx_pv_dz;
		float vtx_pv_chi2;
		float vtx_pv_ndof; // ndof is not int because tracks contribute to the vertex with fractional weights
		int   vtx_pv_ntrk;

		// methods
		void Declarations()
		{
			Declare("vtx_nvtx"   , vtx_nvtx,    "I");
			Declare("vtx_pv_x"   , vtx_pv_x,    "F");
			Declare("vtx_pv_y"   , vtx_pv_y,    "F");
			Declare("vtx_pv_z"   , vtx_pv_z,    "F");
			Declare("vtx_pv_dx"  , vtx_pv_dx,   "F");
			Declare("vtx_pv_dy"  , vtx_pv_dy,   "F");
			Declare("vtx_pv_dz"  , vtx_pv_dz,   "F");
			Declare("vtx_pv_chi2", vtx_pv_chi2, "F");
			Declare("vtx_pv_ndof", vtx_pv_ndof, "F");
			Declare("vtx_pv_ntrk", vtx_pv_ntrk, "I");
		}

		void Reset()
		{
			vtx_nvtx    = -999;
			vtx_pv_x    = -999.;
			vtx_pv_y    = -999.;
			vtx_pv_z    = -999.;
			vtx_pv_dx   = -999.;
			vtx_pv_dy   = -999.;
			vtx_pv_dz   = -999.;
			vtx_pv_chi2 = -999.;
			vtx_pv_ndof = -999.;
			vtx_pv_ntrk = -999;
		}

		void Fill(const edm::Handle<reco::VertexCollection> &verticesHandle);

		virtual bool alreadyPrinted() { return alreadyPrinted_; }
		virtual void setAlreadyPrinted() { alreadyPrinted_ = true; }
};

#endif
