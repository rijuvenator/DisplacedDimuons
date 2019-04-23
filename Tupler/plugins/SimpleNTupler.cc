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
#include "DataFormats/PatCandidates/interface/TriggerEvent.h"
#include "DataFormats/PatCandidates/interface/PackedTriggerPrescales.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/PatCandidates/interface/MET.h"
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
#include "DisplacedDimuons/Tupler/interface/METBranches.h"
#include "DisplacedDimuons/Tupler/interface/BeamspotBranches.h"
#include "DisplacedDimuons/Tupler/interface/VertexBranches.h"
#include "DisplacedDimuons/Tupler/interface/GenBranches.h"
#include "DisplacedDimuons/Tupler/interface/PATMuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DSAMuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/RSAMuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DGBMuonBranches.h"
#include "DisplacedDimuons/Tupler/interface/DimuonBranches.h"

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

    template<class Type>
    bool FailedToGet(Type&, const std::string&);

    // the tree
    TreeContainer tree;

    // parameters from the cmsRun cfg file
    std::vector<std::string> ddmHLTPaths;
    bool                     isMC;
    bool                     isSignal;
    std::string              finalState;
    std::string              source;

    // the branch collection classes
    EventBranches    eventData;
    TriggerBranches  triggerData;
    METBranches      metData;
    BeamspotBranches beamspotData;
    VertexBranches   vertexData;
    GenBranches      genData;
    PATMuonBranches  patMuonData;
    DSAMuonBranches  dsaMuonData;
    RSAMuonBranches  rsaMuonData;
    DGBMuonBranches  dgbMuonData;
    DimuonBranches   dimData;

    // the tokens
    edm::EDGetTokenT<pat::TriggerEvent             > triggerEventToken;
    edm::EDGetTokenT<pat::PackedTriggerPrescales   > prescalesToken;
    edm::EDGetTokenT<edm::TriggerResults           > triggerToken;
    edm::EDGetTokenT<pat::METCollection            > patMetToken;
    edm::EDGetTokenT<edm::TriggerResults           > filtersToken;
    edm::EDGetTokenT<reco::BeamSpot                > beamspotToken;
    edm::EDGetTokenT<reco::VertexCollection        > vertexToken;
    edm::EDGetTokenT<reco::GenParticleCollection   > genToken;
    edm::EDGetTokenT<GenEventInfoProduct           > GEIPToken;
    edm::EDGetTokenT<std::vector<PileupSummaryInfo>> pileupToken;
    edm::EDGetTokenT<pat::MuonCollection           > muonToken;
    edm::EDGetTokenT<reco::TrackCollection         > dsaMuonToken;
    edm::EDGetTokenT<reco::TrackCollection         > rsaMuonToken;
    edm::EDGetTokenT<reco::TrackCollection         > dgbMuonToken;

};

// class constructor
SimpleNTupler::SimpleNTupler(const edm::ParameterSet& iConfig):
  tree("DDTree", ""),

  ddmHLTPaths(iConfig.getParameter<std::vector<std::string>>("ddmHLTPaths")),
  isMC       (iConfig.getParameter<bool                    >("isMC"       )),
  isSignal   (iConfig.getParameter<bool                    >("isSignal"   )),
  finalState (iConfig.getParameter<std::string             >("finalState" )),
  source     (iConfig.getParameter<std::string             >("source"     )),

  eventData   (tree),
  triggerData (tree, source == "PAT"),
  metData     (tree, source == "PAT"),
  beamspotData(tree, source != "GEN"),
  vertexData  (tree, source != "GEN"),
  genData     (tree, isMC           ),
  patMuonData (tree, source == "PAT"),
  dsaMuonData (tree, source != "GEN"),
  rsaMuonData (tree, source != "GEN"),
  dgbMuonData (tree, source != "GEN"),
  dimData     (tree, source != "GEN"),

  triggerEventToken(consumes<pat::TriggerEvent             >(iConfig.getParameter<edm::InputTag>("triggerEvent"  ))),
  prescalesToken   (consumes<pat::PackedTriggerPrescales   >(iConfig.getParameter<edm::InputTag>("prescales"     ))),
  triggerToken     (consumes<edm::TriggerResults           >(iConfig.getParameter<edm::InputTag>("triggerResults"))),
  patMetToken      (consumes<pat::METCollection            >(iConfig.getParameter<edm::InputTag>("patMet"        ))),
  filtersToken     (consumes<edm::TriggerResults           >(iConfig.getParameter<edm::InputTag>("filters"       ))),
  beamspotToken    (consumes<reco::BeamSpot                >(iConfig.getParameter<edm::InputTag>("beamspot"      ))),
  vertexToken      (consumes<reco::VertexCollection        >(iConfig.getParameter<edm::InputTag>("vertices"      ))),
  genToken         (consumes<reco::GenParticleCollection   >(iConfig.getParameter<edm::InputTag>("gens"          ))),
  GEIPToken        (consumes<GenEventInfoProduct           >(iConfig.getParameter<edm::InputTag>("GEIP"          ))),
  pileupToken      (consumes<std::vector<PileupSummaryInfo>>(iConfig.getParameter<edm::InputTag>("pileupInfo"    ))),
  muonToken        (consumes<pat::MuonCollection           >(iConfig.getParameter<edm::InputTag>("muons"         ))),
  dsaMuonToken     (consumes<reco::TrackCollection         >(iConfig.getParameter<edm::InputTag>("dsaMuons"      ))),
  rsaMuonToken     (consumes<reco::TrackCollection         >(iConfig.getParameter<edm::InputTag>("rsaMuons"      ))),
  dgbMuonToken     (consumes<reco::TrackCollection         >(iConfig.getParameter<edm::InputTag>("dgbMuons"      )))
{};

// wrapper for failedToGet
template<class Type>
bool SimpleNTupler::FailedToGet(Type& Handle, const std::string& name)
{
  if (Handle.failedToGet())
  {
    edm::LogWarning("SimpleNTupler")
      << "+++ Warning: "
      << name
      << " is not found +++";
    return true;
  }
  return false;
}

// analyze method
void SimpleNTupler::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  // ******************
  // *** EVENT DATA ***
  // ******************
  eventData.Fill(iEvent);


  // ********************
  // *** TRIGGER DATA ***
  // ********************
  // Check whether the DDM paths(s) fired or not
  // If fired, save the Level-1/HLT muons
  if (source == "PAT")
  {
    bool ddm_paths_fired = false;
    edm::Handle<pat::TriggerEvent> triggerEvent;
    iEvent.getByToken(triggerEventToken, triggerEvent);
    if (!FailedToGet(triggerEvent, "pat::TriggerEvent collection"))
    {
      edm::Handle<edm::TriggerResults> triggerResults;
      iEvent.getByToken(triggerToken, triggerResults);
      if (!FailedToGet(triggerResults, "edm::TriggerResults collection"))
      {
        edm::Handle<pat::PackedTriggerPrescales> prescales;
        iEvent.getByToken(prescalesToken, prescales);
        const edm::TriggerNames& triggerNames = iEvent.triggerNames(*triggerResults);
        ddm_paths_fired = triggerData.Fill(*triggerEvent, prescales, triggerNames, ddmHLTPaths);
      }
    }
    // Do nothing else if the path(s) we are interested in have not fired
    // and if this is not a signal sample
    if (!ddm_paths_fired && !isSignal) return;
  }


  // ****************
  // *** MET DATA ***
  // ****************
  if (source == "PAT")
  {
    edm::Handle<pat::METCollection> met;
    iEvent.getByToken(patMetToken, met);

    edm::Handle<edm::TriggerResults> filterResults;
    iEvent.getByToken(filtersToken, filterResults);
    if (!FailedToGet(filterResults, "edm::TriggerResults collection"))
    {
      const edm::TriggerNames& filterNames = iEvent.triggerNames(*filterResults);
      metData.Fill(met, *filterResults, filterNames);
    }
  }


  // *********************
  // *** BEAMSPOT DATA ***
  // *********************
  edm::Handle<reco::BeamSpot> beamspot;
  if (source != "GEN")
  {
    iEvent.getByToken(beamspotToken, beamspot);
    beamspotData.Fill(beamspot);
  }


  // ******************
  // *** VERTEX DATA **
  // ******************
  edm::Handle<reco::VertexCollection> vertices;
  if (source != "GEN")
  {
    iEvent.getByToken(vertexToken, vertices);
    vertexData.Fill(vertices);
  }

  // Stepping helix propagator
  edm::ESHandle<Propagator> propagator;
  iSetup.get<TrackingComponentsRecord>().get("SteppingHelixPropagatorAny", propagator);

  // B field
  edm::ESHandle<MagneticField> magfield;
  iSetup.get<IdealMagneticFieldRecord>().get(magfield);

  // ****************
  // *** GEN DATA ***
  // ****************
  if (isMC)
  {
    edm::Handle<reco::GenParticleCollection> gens;
    edm::Handle<GenEventInfoProduct> GEIP;
    edm::Handle<std::vector<PileupSummaryInfo> > pileupInfo;
    iEvent.getByToken(genToken, gens);
    iEvent.getByToken(GEIPToken, GEIP);
    iEvent.getByToken(pileupToken, pileupInfo);
    genData.Fill(gens, GEIP, pileupInfo, isSignal, finalState, beamspot, propagator, magfield);
  }

  // ***** GET TRANSIENT TRACK BUILDER *****
  edm::ESHandle<TransientTrackBuilder> ttB;
  iSetup.get<TransientTrackRecord>().get("TransientTrackBuilder", ttB);

  // *********************
  // *** PAT MUON DATA ***
  // *********************
  if (source == "PAT")
  {
    edm::Handle<pat::MuonCollection> patMuons;
    iEvent.getByToken(muonToken, patMuons);
    if (vertexData.isValid())
      patMuonData.Fill(patMuons, ttB, vertices, beamspot, propagator, magfield);
  }

  // *********************
  // *** DSA MUON DATA ***
  // *********************
  edm::Handle<reco::TrackCollection> dsaMuons;
  edm::Handle<pat::MuonCollection>   patMuons;
  if (source != "GEN")
  {
    iEvent.getByToken(dsaMuonToken, dsaMuons);
    iEvent.getByToken(muonToken,    patMuons);

    if (vertexData.isValid())
      dsaMuonData.Fill(dsaMuons, ttB, vertices, beamspot, propagator, magfield, patMuons);
  }

  // *********************
  // *** RSA MUON DATA ***
  // *********************
  if (source != "GEN")
  {
    edm::Handle<reco::TrackCollection> rsaMuons;
    iEvent.getByToken(rsaMuonToken, rsaMuons);
    if (vertexData.isValid())
      rsaMuonData.Fill(rsaMuons, ttB, vertices, beamspot);
  }

  // *********************
  // *** DGB MUON DATA ***
  // *********************
  if (source != "GEN")
  {
    // Skip for now. -SV.
    //edm::Handle<reco::TrackCollection> dgbMuons;
    //iEvent.getByToken(rsaMuonToken, dgbMuons);
    //if (vertexData.isValid())
    //  dgbMuonData.Fill(dgbMuons, ttB, vertices, beamspot);
  }

  // *******************
  // *** DIMUON DATA ***
  // *******************
  if (source != "GEN")
  {
    if (dsaMuonData.isValid() && vertexData.isValid())
      dimData.Fill(iSetup, dsaMuons, ttB, vertices, beamspot, patMuons);
  }

  // Final tree fill
  tree.Fill();
};

// make plugin
DEFINE_FWK_MODULE(SimpleNTupler);
