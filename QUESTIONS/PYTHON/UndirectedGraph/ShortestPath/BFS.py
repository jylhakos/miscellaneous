
def BFS(graph, start, end):

    explored = []

    queue = [[start]]

    if start == end:

        print("START EQUALS END.")

        return

    while queue:

        path = queue.pop(0)

        node = path[-1]

        if node not in explored:

            neighbours = graph[node]

            for neighbour in neighbours:

                new_path = list(path)

                new_path.append(neighbour)

                queue.append(new_path)

                if neighbour == end:

                    print("SHORTEST PATH: ", *new_path)

                    return

            explored.append(node)

    print("PATH DOESN'T EXIST.")

    return

if __name__ == "__main__":

    graph = {'A': ['B', 'D', 'H'],
             'B': ['A', 'C', 'D'],
             'C': ['B', 'D', 'F'],
             'D': ['A', 'B', 'C', 'E'],
             'E': ['D', 'F', 'H'],
             'F': ['C', 'E', 'G'],
             'G': ['F', 'H'],
             'H': ['A', 'E', 'G']
            }

    print("BREADTH FIRST SEARCH", 'A', 'TO', 'H')

    BFS(graph, 'A', 'H')