#include "DisplacedDimuons/Tupler/interface/DisplacedMuonFiller.h"

#include "TrackingTools/IPTools/interface/IPTools.h"

DisplacedMuon DisplacedMuonFiller::Fill(const reco::Track& track,
					const edm::ESHandle<TransientTrackBuilder>& ttB,
					const edm::Handle<reco::VertexCollection> &verticesHandle,
					const edm::Handle<reco::BeamSpot> &beamspotHandle,
					const bool patmuon)
{
  DisplacedMuon cand;

  // TBD: move this part upstream?
  // Primary vertex; needed to calculate d0 and dz
  // Check if failed to get
  // already checked if vertices are valid
  const reco::VertexCollection &vertices = *verticesHandle;
  reco::Vertex pv = vertices.front();

  cand.px      = track.px     ();
  cand.py      = track.py     ();
  cand.pz      = track.pz     ();
  cand.ptError = track.ptError();
  cand.eta     = track.eta    ();
  cand.phi     = track.phi    ();
  cand.charge  = track.charge ();
  cand.chi2    = track.chi2   ();
  cand.ndof    = track.ndof   ();

  // Position of the reference point.
  cand.x       = track.vx     ();
  cand.y       = track.vy     ();
  cand.z       = track.vz     ();

  // Position of the innermost hit.  As it is stored in TrackExtra, we
  // need to make sure that TrackExtra exists.
  if (!patmuon) {
    if (!track.extra().isNull() && track.innerOk())
      {
	cand.x_fhit = track.innerPosition().x();
	cand.y_fhit = track.innerPosition().y();
	cand.z_fhit = track.innerPosition().z();
      }
  }

  cand.n_PxlHits   = track.hitPattern().numberOfValidPixelHits();
  cand.n_TrkHits   = track.hitPattern().numberOfValidTrackerHits();
  cand.n_TrkLayers = track.hitPattern().trackerLayersWithMeasurement();

  cand.n_MuonHits    = track.hitPattern().numberOfValidMuonHits()   ;
  cand.n_DTHits      = track.hitPattern().numberOfValidMuonDTHits() ;
  cand.n_CSCHits     = track.hitPattern().numberOfValidMuonCSCHits();
  cand.n_DTStations  = track.hitPattern().dtStationsWithValidHits() ;
  cand.n_CSCStations = track.hitPattern().cscStationsWithValidHits();

  // Get the transient track for extrapolations below
  reco::TransientTrack ttrack=ttB->build(track);
  // Not sure we need to set the beam spot, but keep it for safety
  if (!beamspotHandle.failedToGet())
    ttrack.setBeamSpot(*beamspotHandle);

  // d0 and dz w.r.t. the primary vertex.  The track is extrapolated
  // to the closest point to the primary vertex in transverse plane.
  GlobalPoint pv_pos(pv.x(), pv.y(), pv.z());
  // This gives the same result as the IPTools method below except for the sign
  // cand.d0_pv      = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeParameters().transverseImpactParameter();
  // double d0err_pv = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeError().transverseImpactParameterError();
  GlobalVector track_dir(track.px(), track.py(), track.pz());
  std::pair<bool, Measurement1D> ip2d = IPTools::signedTransverseImpactParameter(ttrack, track_dir, pv);
  if (ip2d.first)
  {
    cand.d0_pv      = ip2d.second.value();
    double d0err_pv = ip2d.second.error();
    cand.d0sig_pv   = fabs(cand.d0_pv)/d0err_pv;
  }
  cand.dz_pv      = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeParameters().longitudinalImpactParameter();
  double dzerr_pv = ttrack.trajectoryStateClosestToPoint(pv_pos).perigeeError().longitudinalImpactParameterError();
  cand.dzsig_pv   = fabs(cand.dz_pv)/dzerr_pv;

  // d0 and dz w.r.t. the beam spot, again using extrapolation
  if (!beamspotHandle.failedToGet())
  {
    const reco::BeamSpot &beamspot = *beamspotHandle;
    GlobalPoint bs_pos(beamspot.x0(), beamspot.y0(), beamspot.z0());
    cand.d0_bs      = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeParameters().transverseImpactParameter();
    double d0err_bs = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeError().transverseImpactParameterError();
    cand.d0sig_bs   = fabs(cand.d0_bs)/d0err_bs;

    cand.dz_bs      = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeParameters().longitudinalImpactParameter();
    double dzerr_bs = ttrack.trajectoryStateClosestToPoint(bs_pos).perigeeError().longitudinalImpactParameterError();
    cand.dzsig_bs   = fabs(cand.dz_bs)/dzerr_bs;
  }

  // d0 w.r.t. (0; 0) assuming that the trajectory is a straight line
  // double d0    = track.d0();
  // double d0sig = fabs(d0)/track.d0Error();

  // d0 and dz w.r.t. the primary vertex assuming that the trajectory
  // is a straight line
  //auto maxVtx = std::min_element(vertices.begin(), vertices.end(), [] (const auto &v1, const auto &v2) {return v1.p4().Pt() < v2.p4().Pt(); });
  cand.d0_pv_lin    = track.dxy(pv.position());
  cand.d0sig_pv_lin = fabs(cand.d0_pv_lin)/track.d0Error();
  cand.dz_pv_lin    = track.dz(pv.position());
  cand.dzsig_pv_lin = fabs(cand.dz_pv_lin)/track.dzError();

  // d0 and dz w.r.t. the beam spot assuming that the trajectory is a
  // straight line
  if (!beamspotHandle.failedToGet())
  {
    const reco::BeamSpot &beamspot = *beamspotHandle;
    cand.d0_bs_lin    = track.dxy(beamspot);
    cand.d0sig_bs_lin = fabs(cand.d0_bs_lin)/track.d0Error();
    cand.dz_bs_lin    = track.dz(beamspot.position());
    cand.dzsig_bs_lin = fabs(cand.dz_bs_lin)/track.dzError();
  }

  return cand;
}

// Extrapolate the trajectory of a track to various points -- point of
// closest approach (PCA) to the beam spot, PCA to the CMS origin, PCA
// to the main primary vertex -- and compare the parameters to those
// stored in the reco::Track class (obtained at the PCA to the
// "reference point").  The results indicate that the reference point
// is in fact the beam spot.
void DisplacedMuonFiller::CompareTrackParams(
             const reco::Track& track,
	     const edm::Handle<reco::VertexCollection> &verticesHandle,
	     const edm::Handle<reco::BeamSpot> &beamspotHandle,
	     const edm::ESHandle<Propagator>& propagator,
	     const edm::ESHandle<MagneticField>& magfield)
{
  static bool debug = true;

  // Create the free trajectory state using the track parameters.
  // B field does not seem to matter: replacing magfield.product() by 0
  // yields identical results.
  FreeTrajectoryState fts(GlobalPoint( track.vx(), track.vy(), track.vz()),
			  GlobalVector(track.px(), track.py(), track.pz()),
			  track.charge(), magfield.product());

  // Propagation to the point of closest approach to the beam spot.
  if (beamspotHandle.failedToGet()) return;
  const reco::BeamSpot &beamspot = *beamspotHandle;
  FreeTrajectoryState ftsPCABS(propagator->propagate(fts, beamspot));

  // Propagation to PCA to the CMS origin.
  GlobalPoint orig(0., 0., 0.);
  FreeTrajectoryState ftsPCAOrig(propagator->propagate(fts, orig));

  // Propagation to PCA to the main primary vertex.
  const reco::VertexCollection &vertices = *verticesHandle;
  reco::Vertex pv = vertices.front();
  GlobalPoint pv_pos(pv.x(), pv.y(), pv.z());
  FreeTrajectoryState ftsPCAPV(propagator->propagate(fts, pv_pos));

  // Check that the track parameters at the RefPoint and at the PCA
  // to the beam spot are indeed the same.
  if (fabs(track.pt()-ftsPCABS.momentum().perp()) > 1e-3)
    std::cout << "+++ DisplacedMuonFiller::CompareTrackParams warning: "
	      << " track pT = " << track.pt()
	      << " differs from pT at the PCA to the beam spot = "
	      << ftsPCABS.momentum().perp() << std::endl;

  if (fabs(track.eta()-ftsPCABS.momentum().eta()) > 1e-3)
    std::cout << "+++ DisplacedMuonFiller::CompareTrackParams warning: "
	      << " track eta = " << track.eta()
	      << " differs from eta at the PCA to the beam spot = "
	      << ftsPCABS.momentum().eta() << std::endl;

  if (fabs(track.phi()-ftsPCABS.momentum().phi()) > 1e-3)
    std::cout << "+++ DisplacedMuonFiller::CompareTrackParams warning: "
	      << " track phi = " << track.phi()
	      << " differs from phi at the PCA to the beam spot = "
	      << ftsPCABS.momentum().phi() << std::endl;

  if (debug)
  {
    std::cout << "parameters at the reference point: " << std::setprecision(6)
	      << "(x; y; z) = " << "(" << track.vx()
	      << "; " << track.vy() << "; " << track.vz() << ")"
	      << ", pT = "  << track.pt()
	      << ", eta = " << track.eta()
	      << ", phi = " << track.phi() << std::endl;

    std::cout << "propagation to the beam spot: "
	      << "(x; y; z) = " << "(" << ftsPCABS.position().x()
	      << "; " << ftsPCABS.position().y()
	      << "; " << ftsPCABS.position().z() << ")"
	      << ", pT = "  << ftsPCABS.momentum().perp()
	      << ", eta = " << ftsPCABS.momentum().eta()
	      << ", phi = " << ftsPCABS.momentum().phi() << std::endl;

    std::cout << "propagation to the primary vertex: "
	      << "(x; y; z) = " << "(" << ftsPCAPV.position().x()
	      << "; " << ftsPCAPV.position().y()
	      << "; " << ftsPCAPV.position().z() << ")"
	      << ", pT = "  << ftsPCAPV.momentum().perp()
	      << ", eta = " << ftsPCAPV.momentum().eta()
	      << ", phi = " << ftsPCAPV.momentum().phi() << std::endl;

    std::cout << "propagation to the origin: "
	      << "(x; y; z) = " << "(" << ftsPCAOrig.position().x()
	      << "; " << ftsPCAOrig.position().y()
	      << "; " << ftsPCAOrig.position().z() << ")"
	      << ", pT = "  << ftsPCAOrig.momentum().perp()
	      << ", eta = " << ftsPCAOrig.momentum().eta()
	      << ", phi = " << ftsPCAOrig.momentum().phi()
	      << std::setprecision(4) << std::endl;
    std::setprecision(4);
  }
}
