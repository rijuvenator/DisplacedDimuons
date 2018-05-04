// C++ includes
#include <iostream>
#include <vector>
#include <map>
#include <string>

// ROOT includes
#include "TFile.h"
#include "TTree.h"

// CMSSW includes
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/EventBranches.h"
#include "DisplacedDimuons/Tupler/interface/GenBranches.h"

// class declaration
class GenOnlyNTupler : public edm::EDAnalyzer
{
	public:
		GenOnlyNTupler(const edm::ParameterSet&);
		~GenOnlyNTupler() {};

	private:
		virtual void beginJob() {};
		virtual void analyze(const edm::Event&, const edm::EventSetup&);
		virtual void endJob() { tree.Write(); }

		TreeContainer tree;

		EventBranches eventData;
		GenBranches   genData;

		edm::EDGetTokenT<reco::GenParticleCollection> genToken;
		edm::EDGetTokenT<GenEventInfoProduct        > GEIPToken;

};

GenOnlyNTupler::GenOnlyNTupler(const edm::ParameterSet& iConfig):
	tree("DDTree", ""),
	eventData(tree),
	genData  (tree),
	genToken (consumes<reco::GenParticleCollection>(iConfig.getParameter<edm::InputTag>("gens"))),
	GEIPToken(consumes<GenEventInfoProduct        >(iConfig.getParameter<edm::InputTag>("GEIP")))
{};

void GenOnlyNTupler::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	edm::Handle<pat::METCollection> met; // dummy MET collection
	eventData.Fill(iEvent, met);

	edm::Handle<reco::GenParticleCollection> gens;
	edm::Handle<GenEventInfoProduct> GEIP;
	iEvent.getByToken(genToken, gens);
	iEvent.getByToken(GEIPToken, GEIP);
	genData.Fill(*gens, *GEIP);

	tree.Fill();

};

// make plugin
DEFINE_FWK_MODULE(GenOnlyNTupler);
