import statistics

class VPTree:
    def __init__(self, points, distance):
        self.left = None
        self.right = None
        self.left_min = float('inf')
        self.left_max = 0
        self.right_min = float('inf')
        self.right_max = 0
        self.distance = distance

        self.vantage_point = points[0]

        if len(points) == 1:
            return

        self._connect_child(points[1:])

    def _connect_child(self, points):
        distances = [self.distance(self.vantage_point, point) for point in points]
        median = statistics.median(distances)

        left_points = []
        right_points = []

        for point, distance in zip(points, distances):
            if distance >= median:
                self.right_min = min(distance, self.right_min)
                if distance > self.right_max:
                    self.right_max = distance
                    right_points.insert(0, point)
                else:
                    right_points.append(point)
            else:
                self.left_min = min(distance, self.left_min)
                if distance > self.left_max:
                    self.left_max = distance
                    left_points.insert(0, point)
                else:
                    left_points.append(point)

        if len(left_points) > 0:
            self.left = VPTree(left_points, self.distance)

        if len(right_points) > 0:
            self.right = VPTree(right_points, self.distance)

    def get_n_nearest_neighbors(self, query, n_neighbors):

        neighbors = []
        nodes_to_visit = [(self, 0)]

        furthest_d = float('inf')

        while len(nodes_to_visit) > 0:
            node, d0 = nodes_to_visit.pop(0)
            if node is None or d0 > furthest_d:
                continue

            d = self.distance(query, node.vantage_point)
            if d < furthest_d and node != self:
                neighbors.append((d, node.vantage_point))
                neighbors.sort(key=lambda x: x[0])
                if len(neighbors) > n_neighbors:
                    neighbors.pop()
                furthest_d = neighbors[-1][0]

            if self.left is None and self.right is None:
                continue

            if node.left_min <= d <= node.left_max:
                nodes_to_visit.insert(0, (node.left, 0))
            elif node.left_min - furthest_d <= d <= node.left_max + furthest_d:
                nodes_to_visit.append((node.left, node.left_min - d if d < node.left_min else d - node.left_max))

            if node.right_min <= d <= node.right_max:
                nodes_to_visit.insert(0, (node.right, 0))
            elif node.right_min - furthest_d <= d <= node.right_max + furthest_d:
                nodes_to_visit.append((node.right, node.right_min - d if d < node.right_min else d - node.right_max))
        return [neighbor[1] for neighbor in neighbors]