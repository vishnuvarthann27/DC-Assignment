# serverList = ["172.31.11.239:12000"
#               ,"172.31.15.133:12000"
#               ,"172.31.15.193:12000"
#               ]

# clusterEdges = [
#     ["172.31.11.239:12000","172.31.15.133:12000", 4],
#     ["172.31.15.133:12000","172.31.15.193:12000", 2],
#     ["172.31.11.239:12000","172.31.15.193:12000", 4]
# ]


import configparser

CONFIG_FILE = configparser.ConfigParser()
CONFIG_FILE.read("config.properties")

SERVER_IP1 = CONFIG_FILE.get("server1", "ip")
SERVER_PORT1 = CONFIG_FILE.get("server1", "port")

SERVER_IP2 = CONFIG_FILE.get("server2", "ip")
SERVER_PORT2 = CONFIG_FILE.get("server2", "port")

SERVER_IP3 = CONFIG_FILE.get("server3", "ip")
SERVER_PORT3 = CONFIG_FILE.get("server3", "port")

serverList = [SERVER_IP1+":"+SERVER_PORT1
              ,SERVER_IP2+":"+SERVER_PORT2
              ,SERVER_IP3+":"+SERVER_PORT3
              ]

clusterEdges = [
    [SERVER_IP1+":"+SERVER_PORT1,SERVER_IP2+":"+SERVER_PORT2, 4],
    [SERVER_IP2+":"+SERVER_PORT2,SERVER_IP3+":"+SERVER_PORT3, 2],
    [SERVER_IP1+":"+SERVER_PORT1,SERVER_IP3+":"+SERVER_PORT3, 4]
]

class Graph:
    def __init__(self, vertices):
        self.V = vertices
        self.graph = []

    def add_edge(self, u, v, w):
        self.graph.append([u, v, w])


    def find(self, parent, i):
        while parent[i] != i:
            i = parent[i]
        return i

    def apply_union(self, parent, rank, x, y):
        xroot = self.find(parent, x)
        yroot = self.find(parent, y)
        if rank[xroot] < rank[yroot]:
            parent[xroot] = yroot
        elif rank[xroot] > rank[yroot]:
            parent[yroot] = xroot
        else:
            parent[yroot] = xroot
            rank[xroot] += 1


    def kruskal_algo(self):
        result = []
        i, e = 0, 0
        self.graph = sorted(self.graph, key=lambda item: item[2])
        parent, rank = [], []
        for node in range(self.V):
            parent.append(node)
            rank.append(0)
        while e < self.V - 1:
            u, v, w = self.graph[i]
            i += 1
            x = self.find(parent, u)
            y = self.find(parent, v)
            if x != y:
                e += 1
                result.append([u, v, w])
                self.apply_union(parent, rank, x, y)
        for edge in result:
            edge[0] = serverList[edge[0]]
            edge[1] = serverList[edge[1]]
        return result


g = Graph(3)

for edge in clusterEdges:
  g.add_edge(serverList.index(edge[0]), serverList.index(edge[1]), edge[2])

MST = g.kruskal_algo()


