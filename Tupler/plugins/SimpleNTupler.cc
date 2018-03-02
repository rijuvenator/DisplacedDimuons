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

#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "DataFormats/HepMCCandidate/interface/GenParticleFwd.h"
#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/TrackReco/interface/TrackFwd.h"

// local includes
#include "DisplacedDimuons/Tupler/interface/EventBranches.h"
#include "DisplacedDimuons/Tupler/interface/TriggerBranches.h"
#include "DisplacedDimuons/Tupler/interface/BeamspotBranches.h"
#include "DisplacedDimuons/Tupler/interface/VertexBranches.h"
#include "DisplacedDimuons/Tupler/interface/GenBranches.h"
#include "DisplacedDimuons/Tupler/interface/MuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DSAMuonBranches.h"

// class declaration
class SimpleNTupler : public edm::EDAnalyzer
{
	public:
		SimpleNTupler(const edm::ParameterSet&);
		~SimpleNTupler() {};

	private:
		virtual void beginJob() {};
		virtual void analyze(const edm::Event&, const edm::EventSetup&);
		virtual void endJob() { tree.Write(); }

		TreeContainer tree;

		EventBranches eventData;
		TriggerBranches triggerData;
		BeamspotBranches beamspotData;
		VertexBranches vertexData;
		GenBranches genData;
		MuonBranches muonData;
		DSAMuonBranches dsaMuonData;

		edm::EDGetTokenT<edm::TriggerResults> triggerToken;
		edm::EDGetTokenT<reco::BeamSpot> beamspotToken;
		edm::EDGetTokenT<reco::VertexCollection> vertexToken;
		edm::EDGetTokenT<reco::GenParticleCollection> genToken;
		edm::EDGetTokenT<GenEventInfoProduct> GEIPToken;
		edm::EDGetTokenT<pat::MuonCollection> muonToken;
		edm::EDGetTokenT<reco::TrackCollection> dsaMuonToken;

};

SimpleNTupler::SimpleNTupler(const edm::ParameterSet& iConfig):
	tree("DDTree", ""),
	eventData(tree),
	triggerData(tree),
	beamspotData(tree),
	vertexData(tree),
	genData(tree),
	muonData(tree),
	dsaMuonData(tree),
	triggerToken(consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerResults"))),
	beamspotToken(consumes<reco::BeamSpot>(iConfig.getParameter<edm::InputTag>("beamspot"))),
	vertexToken(consumes<reco::VertexCollection>(iConfig.getParameter<edm::InputTag>("vertices"))),
	genToken(consumes<reco::GenParticleCollection>(iConfig.getParameter<edm::InputTag>("gens"))),
	GEIPToken(consumes<GenEventInfoProduct>(iConfig.getParameter<edm::InputTag>("GEIP"))),
	muonToken(consumes<pat::MuonCollection>(iConfig.getParameter<edm::InputTag>("muons"))),
	dsaMuonToken(consumes<reco::TrackCollection>(iConfig.getParameter<edm::InputTag>("dsaMuons")))
{};

void SimpleNTupler::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
	eventData.Fill(iEvent);

	edm::Handle<edm::TriggerResults> triggerResults;
	iEvent.getByToken(triggerToken, triggerResults);
	const edm::TriggerNames& triggerNames = iEvent.triggerNames(*triggerResults);
	triggerData.Fill(*triggerResults, triggerNames);

	edm::Handle<reco::BeamSpot> beamspot;
	iEvent.getByToken(beamspotToken, beamspot);
	beamspotData.Fill(*beamspot);

	edm::Handle<reco::VertexCollection> vertices;
	iEvent.getByToken(vertexToken, vertices);
	vertexData.Fill(*vertices);

	edm::Handle<reco::GenParticleCollection> gens;
	edm::Handle<GenEventInfoProduct> GEIP;
	iEvent.getByToken(genToken, gens);
	iEvent.getByToken(GEIPToken, GEIP);
	genData.Fill(*gens, *GEIP);

	edm::Handle<pat::MuonCollection> muons;
	iEvent.getByToken(muonToken, muons);
	muonData.Fill(*muons);

	edm::Handle<reco::TrackCollection> dsaMuons;
	iEvent.getByToken(dsaMuonToken, dsaMuons);
	dsaMuonData.Fill(*dsaMuons);

	tree.Fill();

};

// make plugin
DEFINE_FWK_MODULE(SimpleNTupler);
