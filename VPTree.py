import statistics


class VPTree:
    def __init__(self, points, distance):
        """
        Args:
             points: идентификаторы точек
             distance: функция растояния
        """
        ##левый сосед
        self.left = None
        ##правый сосед
        self.right = None
        ##минимальное растояние до потомков в левом поддереве
        self.left_min = float('inf')
        ##максимальное растояние до потомков в левом поддереве
        self.left_max = 0
        ##минимальное растояние до потомков в правом поддереве
        self.right_min = float('inf')
        ##максимальное растояние до потомков в правом поддереве
        self.right_max = 0
        ##функция растояния
        self.distance = distance
        ##идетификатор точки обзора
        self.vantage_point = points[0]

        if len(points) == 1:
            return

        self._connect_child(points[1:])

    def _connect_child(self, points):
        """
        расчитать потомков текущего узла дерева

        Args:
             points: идентификаторы точек
        """
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

    def get_n_nearest_neighbors(self, id_point, count_neighbors):
        """
        Найти n ближайших соседей

        Args:
             id_point:
             count_neighbors:
        Returns:
            идентивикаторы ближайших точек
        """
        neighbors = []
        nodes_to_visit = [(self, 0)]

        furthest_distance = float('inf')

        while len(nodes_to_visit) > 0:
            node, d0 = nodes_to_visit.pop(0)
            if node is None or d0 > furthest_distance:
                continue

            distance = self.distance(id_point, node.vantage_point)
            if distance < furthest_distance and node != self:
                neighbors.append((distance, node.vantage_point))
                neighbors.sort(key=lambda x: x[0])
                if len(neighbors) > count_neighbors:
                    neighbors.pop()
                furthest_distance = neighbors[-1][0]

            if self.left is None and self.right is None:
                continue

            if node.left_min <= distance <= node.left_max:
                nodes_to_visit.insert(0, (node.left, 0))
            elif node.left_min - furthest_distance <= distance <= node.left_max + furthest_distance:
                nodes_to_visit.append(
                    (node.left, node.left_min - distance if distance < node.left_min else distance - node.left_max))

            if node.right_min <= distance <= node.right_max:
                nodes_to_visit.insert(0, (node.right, 0))
            elif node.right_min - furthest_distance <= distance <= node.right_max + furthest_distance:
                nodes_to_visit.append(
                    (node.right, node.right_min - distance if distance < node.right_min else distance - node.right_max))
        return [neighbor[1] for neighbor in neighbors]
