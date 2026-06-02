# uwb_processor.py

import numpy as np

class Kalman1D:
    def __init__(self, q=0.001, r=0.04):
        self.q = q
        self.r = r
        self.x = None
        self.p = 1.0

    def filter(self, z):
        if self.x is None:
            self.x = z
            return z

        self.p += self.q
        k = self.p / (self.p + self.r)
        self.x += k * (z - self.x)
        self.p *= (1 - k)
        return self.x


class UWBProcessor:
    def __init__(self):
        self.kf_dict = {}
        self.last_pos = None

    def taylor_ls(self, anchors, distances):
        anchors = np.array(anchors)
        distances = np.array(distances)

        if self.last_pos is None:
            xv = np.mean(anchors, axis=0)
        else:
            xv = self.last_pos.copy()

        for _ in range(10):
            diff = anchors - xv
            r = np.linalg.norm(diff, axis=1)
            r[r == 0] = 1e-6

            residual = distances - r
            H = (xv - anchors) / r[:, None]

            try:
                delta = np.linalg.inv(H.T @ H + np.eye(3)*1e-6) @ H.T @ residual
                xv += delta
                if np.linalg.norm(delta) < 1e-3:
                    break
            except:
                return None

        return xv

    def process(self, anchor_ids, anchors, distances):

        filtered_d = []

        for i, aid in enumerate(anchor_ids):
            if aid not in self.kf_dict:
                self.kf_dict[aid] = Kalman1D()

            f = self.kf_dict[aid].filter(distances[i])
            filtered_d.append(f)

        pos = self.taylor_ls(anchors, filtered_d)

        if pos is None:
            return None

        # reject jump
        if self.last_pos is not None:
            if np.linalg.norm(pos - self.last_pos) > 1.5:
                return None

        self.last_pos = pos
        return pos