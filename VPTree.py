import statistics

class VPTree:
    def __init__(self, points, dist_fn):
        self.left = None
        self.right = None
        self.left_min = float('inf')
        self.left_max = 0
        self.right_min = float('inf')
        self.right_max = 0
        self.dist_fn = dist_fn

        vp_i = 0
        self.vp = points[vp_i]
        points.pop(0)

        if len(points) == 0:
            return

        distances = [self.dist_fn(self.vp, p) for p in points]
        median = statistics.median(distances)

        left_points = []
        right_points = []
        for point, distance in zip(points, distances):
            if distance >= median:
                self.right_min = min(distance, self.right_min)
                if distance > self.right_max:
                    self.right_max = distance
                    right_points.insert(0, point) # put furthest first
                else:
                    right_points.append(point)
            else:
                self.left_min = min(distance, self.left_min)
                if distance > self.left_max:
                    self.left_max = distance
                    left_points.insert(0, point) # put furthest first
                else:
                    left_points.append(point)

        if len(left_points) > 0:
            self.left = VPTree(left_points, self.dist_fn)

        if len(right_points) > 0:
            self.right = VPTree(right_points, self.dist_fn)

    def get_n_nearest_neighbors(self, query, n_neighbors):
        if not isinstance(n_neighbors, int) or n_neighbors < 1:
            raise ValueError('n_neighbors must be strictly positive integer')
        neighbors = _AutoSortingList(max_size=n_neighbors)
        nodes_to_visit = [(self, 0)]

        furthest_d = float('inf')

        while len(nodes_to_visit) > 0:
            node, d0 = nodes_to_visit.pop(0)
            if node is None or d0 > furthest_d:
                continue

            d = self.dist_fn(query, node.vp)
            if d < furthest_d and node != self:
                neighbors.append((d, node.vp))
                furthest_d, _ = neighbors[-1]

            if self.left is None and self.right is None:
                continue

            if node.left_min <= d <= node.left_max:
                nodes_to_visit.insert(0, (node.left, 0))
            elif node.left_min - furthest_d <= d <= node.left_max + furthest_d:
                nodes_to_visit.append((node.left,
                                       node.left_min - d if d < node.left_min
                                       else d - node.left_max))

            if node.right_min <= d <= node.right_max:
                nodes_to_visit.insert(0, (node.right, 0))
            elif node.right_min - furthest_d <= d <= node.right_max + furthest_d:
                nodes_to_visit.append((node.right,
                                       node.right_min - d if d < node.right_min
                                       else d - node.right_max))
        return [neighbor[1] for neighbor in neighbors]

class _AutoSortingList(list):
    def __init__(self, max_size=None, *args):
        super(_AutoSortingList, self).__init__(*args)
        self.max_size = max_size

    def append(self, item):
        super(_AutoSortingList, self).append(item)
        self.sort(key=lambda x: x[0])
        if self.max_size is not None and len(self) > self.max_size:
            self.pop()