#ifndef DISPLACEDMUON_H
#define DISPLACEDMUON_H

#include <iosfwd>
#include <iostream>
#include <math.h>

// muon branch collection
struct DisplacedMuon
{
  // constructor
  DisplacedMuon()
  {
    Reset();
  }

  // members
  int   idx    ;
  float px     ;
  float py     ;
  float pz     ;
  float ptError;
  float eta    ;
  float phi    ;
  int   charge ;

  // Position of the "reference point" on track.  Reference point is
  // "the point of closest approach to the centre of CMS" (see
  // DataFormats/TrackReco/interface/TrackBase.h).
  float x      ;
  float y      ;
  float z      ;

  // Position of the innermost hit on track (stored in reco::TrackExtra)
  float x_fhit ;
  float y_fhit ;
  float z_fhit ;

  float chi2 ;
  int   ndof ;

  // Information from HitPattern: tracker (N/A for DSA and RSA)
  int n_PxlHits;
  int n_TrkHits;
  int n_TrkLayers;

  // Information from HitPattern: muon system
  int n_MuonHits    ;
  int n_DTHits      ;
  int n_CSCHits     ;
  int n_DTStations  ;
  int n_CSCStations ;

  // d0 w.r.t. the primary vertex and the beam spot, and its
  // significance.  For now store two types of values for each, 1)
  // obtained by propagating the trajectory in the magnetic field, and
  // 2) (with "lin" in the variable name) calculated analytically
  // assuming that the trajectory is a straight line.
  float d0_pv        ;
  float d0_bs        ;
  float d0_pv_lin    ;
  float d0_bs_lin    ;
  float d0sig_pv     ;
  float d0sig_bs     ;
  float d0sig_pv_lin ;
  float d0sig_bs_lin ;

  // Ditto for dz
  float dz_pv        ;
  float dz_bs        ;
  float dz_pv_lin    ;
  float dz_bs_lin    ;
  float dzsig_pv     ;
  float dzsig_bs     ;
  float dzsig_pv_lin ;
  float dzsig_bs_lin ;

  // methods
  void Reset()
  {
    idx    = -999 ;
    px     = -999.;
    py     = -999.;
    pz     = -999.;
    ptError= -999.;
    eta    = -999.;
    phi    = -999.;
    charge = -999 ; 

    x      = -999.;
    y      = -999.;
    z      = -999.;
    x_fhit = -999.;
    y_fhit = -999.;
    z_fhit = -999.;

    chi2   = -999.;
    ndof   = -999 ;

    n_PxlHits     = -999;
    n_TrkHits     = -999;
    n_TrkLayers   = -999;

    n_MuonHits    = -999;
    n_DTHits      = -999;
    n_CSCHits     = -999;
    n_DTStations  = -999;
    n_CSCStations = -999;

    d0_pv        = -999.;
    d0_bs        = -999.;
    d0_pv_lin    = -999.;
    d0_bs_lin    = -999.;
    d0sig_pv     = -999.;
    d0sig_bs     = -999.;
    d0sig_pv_lin = -999.;
    d0sig_bs_lin = -999.;

    dz_pv        = -999.;
    dz_bs        = -999.;
    dz_pv_lin    = -999.;
    dz_bs_lin    = -999.;
    dzsig_pv     = -999.;
    dzsig_bs     = -999.;
    dzsig_pv_lin = -999.;
    dzsig_bs_lin = -999.;
  }

  friend std::ostream& operator << (std::ostream& output, const DisplacedMuon& rhs) {
    double pt = sqrt(pow(rhs.px,2) + pow(rhs.py,2));
    double p  = sqrt(pow(pt,2)     + pow(rhs.pz,2));
    output << " idx = " << rhs.idx << " charge = " << rhs.charge
	   << " pt = "  << pt << " +/- " << rhs.ptError << " p = " << p
	   << " eta = " << rhs.eta << " phi = " << rhs.phi
	   << " chi2/ndof = " << rhs.chi2 << "/" << rhs.ndof << std::endl;
    output << "  (px; py; pz) at the reference point: (" << rhs.px
	   << ";" << rhs.py        << ";" << rhs.pz     << ")" << std::endl;
    output << "  (x; y; z) of the reference point: (" << rhs.x
	   << ";" << rhs.y         << ";" << rhs.z      << ")" << std::endl;
    output << "  (x; y; z) of the innermost hit:   (" << rhs.x_fhit
    	      << ";" << rhs.y_fhit << ";" << rhs.z_fhit << ")" << std::endl;

    output << "  N(pixel hits) = "     << rhs.n_PxlHits
	   << "; N(tracker hits) = "   << rhs.n_TrkHits
	   << "; N(tracker layers) = " << rhs.n_TrkLayers << std::endl;

    output << "  N(mu hits) = "  << rhs.n_MuonHits
	   << "; N(DT hits) = "  << rhs.n_DTHits
	   << "; N(CSC hits) = " << rhs.n_CSCHits
	   << "; N(DTs with valid hits) = "  << rhs.n_DTStations
	   << "; N(CSCs with valid hits) = " << rhs.n_CSCStations << std::endl;

    output << "  d0(PV; real extrap.) = " << rhs.d0_pv
	   << " d0(PV) significance = "   << rhs.d0sig_pv << std::endl;
    output << "  d0(PV; lin extrap.) = "  << rhs.d0_pv_lin
	   << " d0(PV) significance = "   << rhs.d0sig_pv_lin << std::endl;
    output << "  d0(BS; real extrap.) = " << rhs.d0_bs
	   << " d0(BS) significance = "   << rhs.d0sig_bs << std::endl;
    output << "  d0(BS; lin extrap.) = "  << rhs.d0_bs_lin
	   << " d0(BS) significance = "   << rhs.d0sig_bs_lin << std::endl;

    output << "  dz(PV; real extrap.) = " << rhs.dz_pv
	   << " dz(PV) significance = "   << rhs.dzsig_pv << std::endl;
    output << "  dz(PV; lin extrap.) = "  << rhs.dz_pv_lin
	   << " dz(PV) significance = "   << rhs.dzsig_pv_lin << std::endl;
    output << "  dz(BS; real extrap.) = " << rhs.dz_bs
	   << " dz(BS) significance = "   << rhs.dzsig_bs << std::endl;
    output << "  dz(BS; lin extrap.) = "  << rhs.dz_bs_lin
	   << " dz(BS) significance = "   << rhs.dzsig_bs_lin << std::endl;

    return output;
  }
};

#endif
