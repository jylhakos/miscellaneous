
def DFS(graph, stack, node):

	if node not in stack:

		stack.append(node)

		for neighbour in graph[node]:

			DFS(graph, stack, neighbour)

		return stack

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

	print("DEPTH FIRST SEARCH")

	stack = DFS(graph, [], 'A')

	print('STACK: ', stack)
