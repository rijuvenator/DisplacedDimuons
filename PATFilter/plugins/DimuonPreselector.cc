// -*- C++ -*-
//
// Package:    DisplacedDimuons
// Class:      DimuonPreselector
// 
/**\class DimuonPreselector DimuonPreselector.cc DisplacedDimuons/DimuonPreselector.cc

 Description: This filter selects events with two or more muons.

 Implementation:
     <Notes on implementation>
*/

// system include files

// user include files
#include "FWCore/Framework/interface/EDFilter.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/TrackReco/interface/Track.h"
#include "DataFormats/PatCandidates/interface/Muon.h"

//
// class declaration
//
class DimuonPreselector : public edm::EDFilter {
public:
  explicit DimuonPreselector(const edm::ParameterSet&);
  ~DimuonPreselector();

private:
  virtual bool filter(edm::Event&, const edm::EventSetup&);
  void sort_by_pt(const double & pt, double & pt1, double & pt2);

  // ----------member data ---------------------------
  edm::InputTag dsa_src;
  double min_pt1_dsa, min_pt2_dsa;
  edm::InputTag dgl_src;
  double min_pt1_dgl, min_pt2_dgl;
  bool filter_on_DSAMuons, filter_on_DGLMuons;
};

//
// constructors and destructor
//
DimuonPreselector::DimuonPreselector(const edm::ParameterSet& iConfig) :
  dsa_src(iConfig.getParameter<edm::InputTag>("dsa_src")),
  min_pt1_dsa(iConfig.getParameter<double>("min_pt1_dsa")),
  min_pt2_dsa(iConfig.getParameter<double>("min_pt2_dsa")),
  dgl_src(iConfig.getParameter<edm::InputTag>("dgl_src")),
  min_pt1_dgl(iConfig.getParameter<double>("min_pt1_dgl")),
  min_pt2_dgl(iConfig.getParameter<double>("min_pt2_dgl")),
  filter_on_DSAMuons(iConfig.getParameter<bool>("filter_on_DSAMuons")),
  filter_on_DGLMuons(iConfig.getParameter<bool>("filter_on_DGLMuons"))
{
  consumes<reco::TrackCollection>(dsa_src);
  consumes<reco::TrackCollection>(dgl_src);
}

DimuonPreselector::~DimuonPreselector()
{
}

//
// member functions
//

// ------------ method called on each new Event ------------
bool DimuonPreselector::filter(edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  bool debug = true;

  // If no filter is required, all events pass
  if (filter_on_DSAMuons == false && filter_on_DGLMuons == false)
    return true;

  // Filter on displaced standalone muons: require at least two muons,
  // each with pT above a certain threshold
  if (filter_on_DSAMuons) {
    int idsa = 0;
    double pt1_dsa = 0., pt2_dsa = 0.; // pT's of leading and subleading muons
    edm::Handle<reco::TrackCollection> dsas;
    iEvent.getByLabel(dsa_src, dsas);
    if (dsas.failedToGet()) {
      edm::LogWarning("DimuonPreselector")
	<< "+++ Warning: DSA collection is not found +++";
      return false;
    }
    for (reco::TrackCollection::const_iterator dsa = dsas->begin(); dsa != dsas->end(); dsa++) {
      sort_by_pt(dsa->pt(), pt1_dsa, pt2_dsa);
      if (debug) 
	std::cout << "DSA # " << idsa++ << " pt = " << dsa->pt()
		  << " eta = " << dsa->eta() << std::endl;
    }
    if (pt1_dsa > min_pt1_dsa && pt2_dsa > min_pt2_dsa) {
      if (debug) std::cout << " -- Keep event; DSA pt1 = " << pt1_dsa
			   << " pt2 = " << pt2_dsa << std::endl;
      return true;
    }
  }

  // Similar filter on displaced global muons
  if (filter_on_DGLMuons) {
    int idgl = 0;
    double pt1_dgl = 0., pt2_dgl = 0.;
    edm::Handle<reco::TrackCollection> dgls;
    iEvent.getByLabel(dgl_src, dgls);
    if (dgls.failedToGet()) {
      edm::LogWarning("DimuonPreselector")
	<< "+++ Warning: DGL collection is not found +++";
      return false;
    }
    for (reco::TrackCollection::const_iterator dgl = dgls->begin(); dgl != dgls->end(); dgl++) {
      sort_by_pt(dgl->pt(), pt1_dgl, pt2_dgl);
      if (debug)
	std::cout << "DGL # " << idgl++ << " pt = " << dgl->pt()
		  << " eta = " << dgl->eta() << std::endl;
    }
    if (pt1_dgl > min_pt1_dgl && pt2_dgl > min_pt2_dgl) {
      if (debug) std::cout << " -- Keep event; DGL pt1_dgl = " << pt1_dgl
			   << " pt2 = " << pt2_dgl << std::endl;
      return true;
    }
  }

  // Neither of the filters passed
  return false;
}

void DimuonPreselector::sort_by_pt(const double & pt, double & pt1, double & pt2) {
  if (pt > pt1) {
    pt2 = pt1;
    pt1 = pt;
  }
  else if (pt > pt2) {
    pt2 = pt;
  }
}

// define this as a plugin
DEFINE_FWK_MODULE(DimuonPreselector);
