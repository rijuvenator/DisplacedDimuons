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
  float eta    ;
  float phi    ;
  int   charge ;
  float x      ;
  float y      ;
  float z      ;

  float chi2 ;
  int   ndof ;

  int n_MuonHits    ;
  int n_DTHits      ;
  int n_CSCHits     ;
  int n_DTStations  ;
  int n_CSCStations ;

  float d0_pv        ;
  float d0_bs        ;
  float d0_pv_lin    ;
  float d0_bs_lin    ;
  float d0sig_pv     ;
  float d0sig_bs     ;
  float d0sig_pv_lin ;
  float d0sig_bs_lin ;

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
    eta    = -999.;
    phi    = -999.;
    charge = -999 ; 
    x      = -999.;
    y      = -999.;
    z      = -999.;

    chi2   = -999.;
    ndof   = -999 ;

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
	   << " pt = "  << pt      << " p = "      << p
	   << " eta = " << rhs.eta << " phi = "    << rhs.phi << std::endl;
    output << "  (x; y; z): (" << rhs.x << ";" << rhs.y << ";" << rhs.z
	   << ") chi2/ndof = " << rhs.chi2 << "/" << rhs.ndof << std::endl;
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
