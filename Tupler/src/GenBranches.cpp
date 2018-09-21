#include "DisplacedDimuons/Tupler/interface/GenBranches.h"

bool GenBranches::alreadyPrinted_ = false;
bool GenBranches::alreadyPrinted_GEIP = false;

namespace PDGID
{
  const int MUON   = 13;
  const int LLXP   = 6000111;
  const int LLX    = 6000113;
  const int HIGGS  = 35;
  const int PROTON = 2212;
}

bool GenBranches::FailedToGet(const edm::Handle<reco::GenParticleCollection> &gensHandle,
    const edm::Handle<GenEventInfoProduct> &GEIPHandle)
{
  if (gensHandle.failedToGet())
  {
    if (!alreadyPrinted_)
    {
      edm::LogWarning("SimpleNTupler")
        << "+++ Warning: "
        << primaryHandleName
        << " is not found; "
        << primaryExtraText
        << "+++";
      alreadyPrinted_ = true;
    }
    return true;
  }
  if (GEIPHandle.failedToGet())
  {
    if (!alreadyPrinted_GEIP)
    {
      edm::LogWarning("SimpleNTupler")
        << "+++ Warning: GenEventInfoProduct is not found +++";
      alreadyPrinted_GEIP = true;
    }
    return true;
  }
  return false;
}

void GenBranches::Fill(
    const edm::Handle<reco::GenParticleCollection> &gensHandle,
    const edm::Handle<GenEventInfoProduct> &GEIPHandle,
    const edm::Handle<std::vector<PileupSummaryInfo> > &pileupInfo,
    const bool isSignal, const std::string finalState,
    const edm::Handle<reco::BeamSpot> &beamspotHandle,
    const edm::ESHandle<Propagator>& propagator,
    const edm::ESHandle<MagneticField>& magfield)
{
  static bool alreadyPrinted_pileup = false;
  static bool debug = false;
  Reset();

  // Check if failed to get
  if (FailedToGet(gensHandle, GEIPHandle)) return;
  const reco::GenParticleCollection &gens = *gensHandle;
  const GenEventInfoProduct &GEIP = *GEIPHandle;

  // set gen weight
  gen_weight = GEIP.weight();

  // Extract the true number of primary vertices in the event for
  // pileup reweighting if PileupSummaryInfo collection exists.  See
  // https://hypernews.cern.ch/HyperNews/CMS/get/physTools/3592/1/2/1/1/1/1.html
  // for more details.
  if (pileupInfo.failedToGet())
  {
    if (!alreadyPrinted_pileup)
    {
      edm::LogWarning("SimpleNTupler")
        << "+++ Warning: PileupSummaryInfo is not found +++";
      alreadyPrinted_pileup = true;
    }
  }
  else
  {
    std::vector<PileupSummaryInfo>::const_iterator pi;
    for (pi = pileupInfo->begin(); pi != pileupInfo->end(); pi++)
    {
      int bx = pi->getBunchCrossing();
      if (bx == 0)
      {
	      gen_tnpv = pi->getTrueNumInteractions();
	      continue;
      }
    }
  }

  // find appropriate gen particles and fill branches
  if      (isSignal && finalState == "4Mu"  ) Fill4Mu  (gens);
  else if (isSignal && finalState == "2Mu2J") Fill2Mu2J(gens);
  else                                        FillOther(gens);

  // Calculate/save some more info for final-state muons:
  //  - d0 and dz w.r.t. the point of closest approach (PCA) to the
  //    beam spot (assuming a line)
  //  - a bunch of parameters of gen muons extrapolated to the PCA
  //    to the beam spot, for comparison with reco muons
  for (unsigned int ipart = 0; ipart < gen_status.size(); ipart++)
  {
    float d0_lin = -999., dz_lin = -999.;
    float px = -999., py = -999., pz = -999., pt = -999., ene = -999.;
    float vx = -999., vy = -999., vz = -999., eta = -999., phi = -999.;
    float d0 = -999., dz = -999.;
    if (gen_status[ipart] == 1)
    {
      if (gen_charge[ipart] != 0)
      {
	      if (!beamspotHandle.failedToGet())
        {
          const reco::BeamSpot &beamspot = *beamspotHandle;
          float x_bs = beamspot.x0();
          float y_bs = beamspot.y0();
          float z_bs = beamspot.z0();

          // d0/dz w.r.t. the PCA to the beam spot; linear extrapolation.
          // Use |(Point-RefPoint) x Momentum| / |Momentum| convention
          // to get the sign of d0 consistent with that in the rest of
          // CMSSW (see TrackBase.h)
          TVector3 zero(x_bs-gen_x[ipart], y_bs-gen_y[ipart], 0.);
          TVector3 p3zz(gen_px[ipart], gen_py[ipart], 0.);
          d0_lin = zero.Cross(p3zz).Z()/p3zz.Mag();
          dz_lin = (gen_z[ipart]-z_bs) +
            zero.Dot(p3zz)/gen_pt[ipart]*gen_pz[ipart]/gen_pt[ipart];

          // Propagate parameters to the point of closest approach to
          // the beam spot and store the propagated parameters in the
          // tree for comparison with parameters of the reconstructed
          // tracks.
          FreeTrajectoryState fts =
            PropagateToBeamSpot(ipart, beamspot, propagator, magfield);

          px  = fts.momentum().x();
          py  = fts.momentum().y();
          pz  = fts.momentum().z();
          pt  = fts.momentum().perp();
          eta = fts.momentum().eta();
          phi = fts.momentum().phi();
          ene = sqrt(pow(fts.momentum().mag(),2) + pow(gen_mass[ipart],2));
          vx  = fts.position().x();
          vy  = fts.position().y();
          vz  = fts.position().z();

          d0  = ((x_bs-vx)*py - (y_bs-vy)*px)/pt;
          dz  = (vz-z_bs) - ((vx-x_bs)*px + (vy-y_bs)*py) / pt * pz / pt;
        }
      }
    }

    gen_d0       .push_back(d0_lin);
    gen_dz       .push_back(dz_lin);

    gen_bs_px    .push_back(px );
    gen_bs_py    .push_back(py );
    gen_bs_pz    .push_back(pz );
    gen_bs_pt    .push_back(pt );
    gen_bs_eta   .push_back(eta);
    gen_bs_phi   .push_back(phi);
    gen_bs_energy.push_back(ene);
    gen_bs_x     .push_back(vx );
    gen_bs_y     .push_back(vy );
    gen_bs_z     .push_back(vz );
    gen_bs_d0    .push_back(d0 );
    gen_bs_dz    .push_back(dz );
  }
 
  if (debug)
  {
    std::cout << "Gen info: weight = " << gen_weight
	      << " true number of primary vertices = " << gen_tnpv
	      << "; gen particles: \n";
    std::cout << " idx |   id  | stat| moth|   pt  |    eta   |   phi  |    M    |    E   | q |        (x;y;z)        |   d0  |   dz  |";
    std:: cout << " pt@bs | eta@bs | phi@bs |       (x;y;z)@bs      | d0@bs | dz@bs |\n";
    unsigned int nparts = gen_status.size();
    for (unsigned int i = 0; i < nparts; i++)
    {
      std::cout << std::setw(5) << i << "|" << std::setw(7) << gen_pdgID[i]
		<< "|" << std::setw(5)  << gen_status[i]
		<< "|" << std::setw(5)  << gen_mother[i] << std::setprecision(4)
		<< "|" << std::setw(7)  << gen_pt[i] 
		<< "|" << std::setw(10) << gen_eta[i]
		<< "|" << std::setw(8)  << gen_phi[i]
		<< "|" << std::setw(9)  << gen_mass[i]
		<< "|" << std::setw(8)  << gen_energy[i]
		<< "|" << std::setw(3)  << gen_charge[i]
		<< "|" << std::setw(7)  << gen_x[i]
		<< " " << std::setw(7)  << gen_y[i]
		<< " " << std::setw(7)  << gen_z[i];
      if (gen_bs_pt[i] > 0.) 
	std::cout      << "|" << std::setw(7) << gen_d0[i]
		       << "|" << std::setw(7) << gen_dz[i]
		       << "|" << std::setw(7) << gen_bs_pt[i]
		       << "|" << std::setw(8) << gen_bs_eta[i]
		       << "|" << std::setw(8) << gen_bs_phi[i]
		       << "|" << std::setw(7) << gen_bs_x[i]
		       << " " << std::setw(7) << gen_bs_y[i]
		       << " " << std::setw(7) << gen_bs_z[i]
		       << "|" << std::setw(7) << gen_bs_d0[i]
		       << "|" << std::setw(7) << gen_bs_dz[i];
      std::cout << "|" << std::endl;
    }
    unsigned int npairs = gen_Lxy.size();
    if (npairs > 0)
    {
      std::cout << " idi |   Lxy   |   cosA  |    dR   | \n";
      for (unsigned int i = 0; i < npairs; i++)
      {
	std::cout << std::setw(5) << i << std::setprecision(4)
		  << "|" << std::setw(9) << gen_Lxy[i] 
		  << "|" << std::setw(9) << gen_cosAlpha[i]
		  << "|" << std::setw(9) << gen_deltaR[i] << "|" << std::endl;
      }
    }
  }
}

// fill gen branches for P -> H -> XX -> 4Mu
void GenBranches::Fill4Mu(const reco::GenParticleCollection &gens)
{
  // muAll is for all muons
  std::vector<const reco::GenParticle*> muAll;
  const reco::GenParticle *mu11 = nullptr;
  const reco::GenParticle *mu12 = nullptr;
  const reco::GenParticle *mu21 = nullptr;
  const reco::GenParticle *mu22 = nullptr;
  const reco::Candidate   *X1   = nullptr;
  const reco::Candidate   *X2   = nullptr;
  const reco::Candidate   *H    = nullptr;
  const reco::Candidate   *P    = nullptr;

  // loop over the gen particles and look for muons
  bool allSet = false;
  for (const auto &gen : gens)
  {
    if (abs(gen.pdgId()) == PDGID::MUON and gen.status() == 1)
    {
      muAll.push_back(&gen);
      if (allSet) continue;

      // p will be a dummy changeable pointer to a particle
      // first look for the mother X, then based on the pointer addresses,
      // set the appropriate X and mu pointers. then look for Higgs, then proton
      const reco::Candidate *p = &gen;
      while (p->pdgId() != PDGID::LLX && p->numberOfMothers() != 0) { p = p->mother(); }
      if (p->pdgId() == PDGID::LLX)
      {
        if      (X1 == nullptr) { X1 = p; mu11 = &gen; } // X1 == 0                                  --> found mu11
        else if (p  == X1     ) {         mu12 = &gen; } // X1 != 0 && p == X1                       --> found mu12
        else if (X2 == nullptr) { X2 = p; mu21 = &gen; } // X1 != 0 && p != X1 && X2 == 0            --> found mu21
        else if (p  == X2     ) {         mu22 = &gen; } // X2 != 0 && p != X1 && X2 != 0 && p == X2 --> found mu22

        // once mu22 is found, no need to keep looping over the gen particles
        // X1, X2, mu11, mu12, mu21, and mu22 should be set
        //if (mu22 != nullptr) break;
        if (mu22 != nullptr) {allSet=true;}
      }
    }
  }
  // make sure X1 and X2 are non-null
  if (X1 == nullptr || X2 == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: X1 or X2 is null. Filling nothing. +++";
    return;
  }
  // set H and P starting from X1
  const reco::Candidate *p = X1;
  p = p->mother();
  H = p;
  while (abs(p->pdgId()) != PDGID::PROTON) { p = p->mother(); }
  P = p;

  // make sure all pointers are non-null
  if (mu11 == nullptr || mu12 == nullptr ||
      mu21 == nullptr || mu22 == nullptr ||
      X1   == nullptr || X2   == nullptr ||
      H    == nullptr || P    == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: At least one pointer is null. Filling nothing. +++";
    return;
  }

  // fill the branches: mu11, mu12, mu21, mu22, X1, X2, H, and P
  // and any additional muons
  std::vector<const reco::Candidate*> particles = {mu11, mu12, mu21, mu22, X1, X2, H, P};
  if (muAll.size() > 4)
  {
    for (const auto &mu : muAll)
    {
      if (std::find(particles.begin(), particles.end(), mu) == particles.end())
      {
        particles.push_back(mu);
      }
    }
  }
  for (const auto &p : particles)
  {
    gen_status.push_back(p->status());
    gen_pdgID .push_back(p->pdgId ());
    gen_px    .push_back(p->px    ());
    gen_py    .push_back(p->py    ());
    gen_pz    .push_back(p->pz    ());
    gen_pt    .push_back(p->pt    ());
    gen_eta   .push_back(p->eta   ());
    gen_phi   .push_back(p->phi   ());
    gen_mass  .push_back(p->mass  ());
    gen_energy.push_back(p->energy());
    gen_charge.push_back(p->charge());
    gen_x     .push_back(p->vx    ());
    gen_y     .push_back(p->vy    ());
    gen_z     .push_back(p->vz    ());
    gen_mother.push_back(-1         ); // not yet implemented
  }

  // fill Lxy, cosAlpha, and deltaR
  std::vector<std::vector<const reco::GenParticle*>> muonPairs = {{mu11, mu12}, {mu21, mu22}};
  for (size_t i=0; i<2; ++i)
  {
    const auto &muonPair = muonPairs[i];
    const auto &mu1      = muonPair [0];
    const auto &mu2      = muonPair [1];

    TVector3 p1(mu1->px(), mu1->py(), mu1->pz());
    TVector3 p2(mu2->px(), mu2->py(), mu2->pz());

    float Lxy      = mu1->vertex().Rho();
    float cosAlpha = p1.Dot(p2)/p1.Mag()/p2.Mag();
    float dR       = p1.DeltaR(p2);

    // this loop no longer uses muon information
    // therefore it no longer needs to be over muonPairs
    // replacing it with a loop over 0, 1
    // this suppresses the unused variable/error 
    for (int j=0; j<2; ++j)
    {
      gen_Lxy     .push_back(Lxy     );
      gen_cosAlpha.push_back(cosAlpha);
      gen_deltaR  .push_back(dR      );
    }
  }
}

// fill gen branches for P -> H -> XX -> 2Mu 2Jet
void GenBranches::Fill2Mu2J(const reco::GenParticleCollection &gens)
{
  // muAll is for all muons
  std::vector<const reco::GenParticle*> muAll;
  const reco::GenParticle *mup  = nullptr;
  const reco::GenParticle *mum  = nullptr;
  const reco::Candidate   *q1   = nullptr;
  const reco::Candidate   *q2   = nullptr;
  const reco::Candidate   *X    = nullptr;
  const reco::Candidate   *XP   = nullptr;
  const reco::Candidate   *H    = nullptr;
  const reco::Candidate   *P    = nullptr;

  bool allSet = false;
  for (const auto &gen : gens)
  {
    // look for X -> mu1 mu2
    if (abs(gen.pdgId()) == PDGID::MUON && gen.status() == 1)
    {
      muAll.push_back(&gen);
      if (allSet) continue;

      // p will be a dummy changeable pointer to a particle
      // first look for the mother X, then based on the pointer addresses,
      // set the appropriate X and mu pointers. then look for Higgs, then proton
      const reco::Candidate *p = &gen;
      while (p->pdgId() != PDGID::LLX && p->numberOfMothers() != 0) { p = p->mother(); }
      if (p->pdgId() == PDGID::LLX)
      {
        if   (X == nullptr)     { X = p;      }
        if   (gen.charge() > 0) { mup = &gen; }
        else                    { mum = &gen; }
      }
    }
    // look for X' -> q1 q2
    if (gen.pdgId() == PDGID::LLXP)
    {
      XP = &gen;
      if (!(XP->numberOfDaughters() == 2))
      {
        edm::LogWarning("NTupler::GenBranches") << "+++ Warning: X' does not have 2 daughters. Filling nothing. +++";
        return;
      }
      if (XP->daughter(0)->pdgId() > 0)
      {
        q1 = XP->daughter(0);
        q2 = XP->daughter(1);
      }
      else
      {
        q1 = XP->daughter(1);
        q2 = XP->daughter(0);
      }
    }
    // if both mu's and X' are set, no need to keep looping over gen particles
    //if (mup != nullptr && mum != nullptr && XP != nullptr) break;
    if (mup != nullptr && mum != nullptr && XP != nullptr) {allSet=true;}
  }
  // make sure X and X' are non-null
  if (X == nullptr || XP == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: X or X' is null. Filling nothing. +++";
    return;
  }
  // set H and P starting from X
  const reco::Candidate *p = X;
  p = p->mother();
  H = p;
  while (abs(p->pdgId()) != PDGID::PROTON) { p = p->mother(); }
  P = p;

  // make sure all pointers are non-null
  if (mup == nullptr || q1  == nullptr ||
      mum == nullptr || q2  == nullptr ||
      X   == nullptr || XP  == nullptr ||
      H   == nullptr || P   == nullptr)
  {
    edm::LogWarning("NTupler::GenBranches") << "+++ Warning: At least one pointer is null. Filling nothing. +++";
    return;
  }

  // fill the branches: mu+, mu-, q, qbar, X, X', H, and P
  std::vector<const reco::Candidate*> particles = {mup, mum, q1, q2, X, XP, H, P};
  if (muAll.size() > 2)
  {
    for (const auto &mu : muAll)
    {
      if (std::find(particles.begin(), particles.end(), mu) == particles.end())
      {
        particles.push_back(mu);
      }
    }
  }
  for (const auto &p : particles)
  {
    gen_status.push_back(p->status());
    gen_pdgID .push_back(p->pdgId ());
    gen_px    .push_back(p->px    ());
    gen_py    .push_back(p->py    ());
    gen_pz    .push_back(p->pz    ());
    gen_pt    .push_back(p->pt    ());
    gen_eta   .push_back(p->eta   ());
    gen_phi   .push_back(p->phi   ());
    gen_mass  .push_back(p->mass  ());
    gen_energy.push_back(p->energy());
    gen_charge.push_back(p->charge());
    gen_x     .push_back(p->vx    ());
    gen_y     .push_back(p->vy    ());
    gen_z     .push_back(p->vz    ());
    gen_mother.push_back(-1         ); // not yet implemented
  }

  // fill Lxy, cosAlpha, and deltaR
  std::vector<std::vector<const reco::Candidate*>> PPairs = {{mup, mum}, {q1, q2}};
  for (size_t i=0; i<2; ++i)
  {
    const auto &PPair = PPairs[i];
    const auto part1  = PPair [0];
    const auto part2  = PPair [1];

    TVector3 p1(part1->px(), part1->py(), part1->pz());
    TVector3 p2(part2->px(), part2->py(), part2->pz());

    float Lxy      = part1->vertex().Rho();
    float cosAlpha = p1.Dot(p2)/p1.Mag()/p2.Mag();
    float dR       = p1.DeltaR(p2);

    // this loop no longer uses muon information
    // therefore it no longer needs to be over muonPairs
    // replacing it with a loop over 0, 1;
    // this suppresses the unused variable/error 
    for (int j=0; j<2; ++j)
    {
      gen_Lxy     .push_back(Lxy     );
      gen_cosAlpha.push_back(cosAlpha);
      gen_deltaR  .push_back(dR      );
    }
  }
}

// fill gen branches for some other MC type, simply filling everything
void GenBranches::FillOther(const reco::GenParticleCollection &gens)
{
  for (const auto &p : gens)
  {
    gen_status.push_back(p.status());
    gen_pdgID .push_back(p.pdgId ());
    gen_px    .push_back(p.px    ());
    gen_py    .push_back(p.py    ());
    gen_pz    .push_back(p.pz    ());
    gen_pt    .push_back(p.pt    ());
    gen_eta   .push_back(p.eta   ());
    gen_phi   .push_back(p.phi   ());
    gen_mass  .push_back(p.mass  ());
    gen_energy.push_back(p.energy());
    gen_charge.push_back(p.charge());
    gen_x     .push_back(p.vx    ());
    gen_y     .push_back(p.vy    ());
    gen_z     .push_back(p.vz    ());

    int mIndex = -1;
    if (p.numberOfMothers() > 0) { mIndex = p.motherRef(0).key(); }

    gen_mother.push_back(mIndex    );
  }
}

// Propagate parameters of gen particle with index idx to the point of
// closest approach to the beam spot
FreeTrajectoryState GenBranches::PropagateToBeamSpot(
		      unsigned int idx,
		      const reco::BeamSpot& beamspot,
		      const edm::ESHandle<Propagator>& propagator,
		      const edm::ESHandle<MagneticField>& magfield)
{
  // Create the free trajectory state
  FreeTrajectoryState fts(GlobalPoint( gen_x[idx],  gen_y[idx],  gen_z[idx]),
			  GlobalVector(gen_px[idx], gen_py[idx], gen_pz[idx]),
			  gen_charge[idx], magfield.product());

  // Propagate fts to the point of closest approach to the beam spot
  FreeTrajectoryState ftsPCABS(propagator->propagate(fts, beamspot));

  return ftsPCABS;
}
