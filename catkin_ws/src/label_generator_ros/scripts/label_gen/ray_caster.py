import numpy as np
import trimesh
from trimesh.ray.ray_pyembree import RayMeshIntersector
import trimesh
from .helper import get_rays, transform_points


class RayCaster:
  def __init__(self, mesh_path, k_image, size, r_sub=4):
    H, W = size

    mesh = trimesh.load(mesh_path)
    self._rmi = RayMeshIntersector(mesh)
    self._start, stop, self._dir = get_rays(
      k_image, size, extrinsic=None, d_min=0.3, d_max=1.4
    )

    self.r_sub = r_sub
    self._start = self._start[:: self.r_sub, :: self.r_sub]
    self._dir = self._dir[:: self.r_sub, :: self.r_sub]
    
  def raycast(self, H_cam):
    # Move Camera Rays
    ray_origins = transform_points(self._start.reshape((-1, 3)), H_cam)
    H_turn = np.eye(4)
    H_turn[:3, :3] = H_cam[:3, :3]
    ray_directions = transform_points(self._dir.reshape((-1, 3)), H_turn)

    # Perform Raytracing
    locations, index_ray, index_tri = self._rmi.intersects_location(
      ray_origins=ray_origins, ray_directions=ray_directions, multiple_hits=False
    )
    return locations, index_ray, index_tri, ray_origins
