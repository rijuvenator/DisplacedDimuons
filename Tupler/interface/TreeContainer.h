#ifndef TREECONTAINER_H
#define TREECONTAINER_H

// C++ includes
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <algorithm>

//ROOT includes
#include "TString.h"
#include "TTree.h"

// CMSSW includes
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

// simple tree container class with TFileService
// Write and Fill provided for convenience
class TreeContainer
{
	public:
		// constructor
		TreeContainer(TString name, TString title) { tree = fs->make<TTree>(name, title); }

		// members
		edm::Service<TFileService> fs;
		TTree *tree;

		// methods
		void Write() { fs->cd(); tree->Write(); }
		void Fill () { tree->Fill() ; }

};

#endif
