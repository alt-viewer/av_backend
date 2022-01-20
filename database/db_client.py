import pydgraph as dgraph

client_stub = dgraph.DgraphClientStub("localhost:9080")
client = dgraph.DgraphClient(client_stub)
