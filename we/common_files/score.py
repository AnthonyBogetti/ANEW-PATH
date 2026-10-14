import numpy as np
import math 

rmsd_ref = np.loadtxt("rmsd_ref.dat", skiprows=1, usecols=(1,2))
rmsd_curr = np.loadtxt("rmsd_curr.dat", skiprows=1, usecols=(1,2))

ref = rmsd_ref.reshape(-1,2)
nref = ref.shape[0]
curr = rmsd_curr.reshape(-1,2)

midpts = np.load("midpoints.npy")

for A in curr:
    min_dist_sq = float('inf')
    best_base = -1
    best_bonus = 0.0

    # 1. Iterate through each line segment to find the closest one to point A.
    for i in range(len(midpts) - 1):
        B = midpts[i]
        C = midpts[i+1]

        vBC = C - B
        vBA = A - B

        # 2. Calculate the scalar projection of A onto the infinite line BC.
        #    Using dot products is efficient.
        sq_mag_vBC = np.dot(vBC, vBC)
        
        # Handle the edge case where the segment has zero length.
        if sq_mag_vBC == 0:
            clamped_proj = 0.0
            dist_sq = np.dot(vBA, vBA) # Squared distance from A to B
        else:
            scalar_proj = np.dot(vBA, vBC) / sq_mag_vBC
            
            # 3. Clamp the projection to the segment [B, C].
            #    This finds the closest point on the segment itself.
            clamped_proj = max(0.0, min(1.0, scalar_proj))
            
            # 4. Find the actual closest point and calculate the squared distance.
            #    (Using squared distance avoids a costly sqrt operation in the loop).
            closest_point = B + clamped_proj * vBC
            dist_sq = np.dot(A - closest_point, A - closest_point)

        # 5. If this segment is the closest one we've found so far,
        #    update our results.
        if dist_sq < min_dist_sq:
            min_dist_sq = dist_sq
            best_base = i
            best_bonus = clamped_proj

    # After checking all segments, we have the correct base and a bonus [0, 1].
    score = best_base + best_bonus

    print(score)
