class Hypercube4D:
    @staticmethod
    def generate_tesseract(size=1.0):
        vertices = []
        edges = []

        for i in range(16):
            x = size * (1 if (i & 1) else -1)
            y = size * (1 if (i & 2) else -1)
            z = size * (1 if (i & 4) else -1)
            w = size * (1 if (i & 8) else -1)
            vertices.append([x, y, z, w])

        for i in range(16):
            for j in range(i + 1, 16):
                diff = i ^ j
                if diff & (diff - 1) == 0:
                    edges.append((i, j))

        return vertices, edges
