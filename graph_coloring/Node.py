class Node:
    def __init__(self, index, neighbors, available_colors):
        self.index = index
        self.neighbors = set(neighbors)
        self.available_colors = set(available_colors)
        self.saturation = 0
        self.degree = len(neighbors)

    def remove_color(self, color):
        self.available_colors.discard(color)
        return not self.available_colors

    def add_color(self, color):
        self.available_colors.add(color)

    def __lt__(self, other):
        return (self.saturation, self.degree) > (other.saturation, other.degree)