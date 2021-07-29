import statistics

class VPTreeNode:
    def __init__(self, points, dist):
        self.left = None
        self.right = None
        self.left_min = float('inf')
        self.left_max = 0
        self.right_min = float('inf')
        self.right_max = 0
        self.dist = dist


        self.vantage_point = points[0]
        points.pop(0)


        distances = [self.dist(self.vantage_point, point) for point in points]
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
            self.left = VPTreeNode(left_points, self.dist)

        if len(right_points) > 0:
            self.right = VPTreeNode(right_points, self.dist)


    def get_n_nearest_neighbors(self, query, count_neighbors):

        neighbors = []
        nodes_to_visit = [(self, 0)]

        max_distance = float('inf')

        while len(nodes_to_visit) > 0:
            node, d0 = nodes_to_visit.pop(0)
            if node is None or d0 > max_distance:
                continue

            distance = self.dist(query, node.vp)
            if distance < max_distance:
                neighbors.append((distance, node.vp))
                max_distance, _ = neighbors[-1]

            if self.left is None and self.right is None:
                continue

            if node.left_min <= distance <= node.left_max:
                nodes_to_visit.insert(0, (node.left, 0))
            elif node.left_min - max_distance <= distance <= node.left_max + max_distance:
                nodes_to_visit.append((node.left,
                                       node.left_min - distance if distance < node.left_min
                                       else distance - node.left_max))

            if node.right_min <= distance <= node.right_max:
                nodes_to_visit.insert(0, (node.right, 0))
            elif node.right_min - max_distance <= distance <= node.right_max + max_distance:
                nodes_to_visit.append((node.right,
                                       node.right_min - distance if distance < node.right_min
                                       else distance - node.right_max))

        return sorted(neighbors)[0:count_neighbors]