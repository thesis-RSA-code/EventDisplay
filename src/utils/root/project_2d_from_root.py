
import numpy as np
import awkward as ak

# Custom imports

from utils.detector_geometries import DETECTOR_GEOM


def project2d(X, Y, Z, experiment) : # project 3D PMT positions of an event to 2D unfolded cylinder

  cylinder_radius = DETECTOR_GEOM[experiment]['cylinder_radius']
  # zMax = DETECTOR_GEOM[experiment]['height']/2
  # zMin = -DETECTOR_GEOM[experiment]['height']/2

  Xproj = ak.zeros_like(X)
  Yproj = ak.zeros_like(Y)

  if experiment in ['WCTE_r', 'DEMO'] : # WCTE bottom and top cap no symmetrical! top PMTs are further away from the last row of cylinder PMTs than the bottom PMTs, and beware of spherical structure of mPMTs
    # values adjusted by hand so as to correctly identify the top and bottom PMTs, maybe get info from WCSim in PMT id or something
    eps_top = 10
    eps_bottom = 10
    
    # WCTE is rotated in WCSim to have beam on the z axis, rotate it back to have cylinder axis on z axis like SK and HK, then rotate a tiny bit around z axis so as not to cut a column of PMTs in half (but also rotate the top and bottom caps though...)
    print('Rotating WCTE events...')
    thetax = np.pi/2
    thetaz = 0
    
    # rotate around x axis
    X_Rx = X
    Y_Rx = np.cos(thetax)*Y - np.sin(thetax)*Z
    Z_Rx = np.sin(thetax)*Y + np.cos(thetax)*Z

    # rotate around z axis
    X = np.cos(thetaz)*X_Rx + np.sin(thetaz)*Y_Rx
    Y = -np.sin(thetaz)*X_Rx + np.cos(thetaz)*Y_Rx
    Z = Z_Rx

  else :
    if experiment == "WCTE" :
      eps_top = 10
      eps_bottom = 10
    else :
      eps_top = 0.01
      eps_bottom = 0.01

  zMax = np.max(Z)
  zMin = np.min(Z)

  top_cap_mask = Z > zMax - eps_top
  bottom_cap_mask = Z < zMin + eps_bottom
  cylinder_mask = np.logical_not(top_cap_mask | bottom_cap_mask)

  # cylinder 
  azimuth = np.arctan2(Y, X)
  azimuth = ak.where(azimuth < 0, 2*np.pi + azimuth, azimuth)

  Xproj = ak.where(cylinder_mask, cylinder_radius * (azimuth - np.pi), Xproj)
  Yproj = ak.where(cylinder_mask, Z, Yproj)

  # top cap
  Xproj = ak.where(top_cap_mask, - Y, Xproj)
  Yproj = ak.where(top_cap_mask, X + zMax + cylinder_radius, Yproj)

  # bottom cap
  Xproj = ak.where(bottom_cap_mask, - Y, Xproj)
  Yproj = ak.where(bottom_cap_mask, - X + zMin - cylinder_radius, Yproj)

  return Xproj, Yproj
