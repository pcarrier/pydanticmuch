from pydantic import BaseModel

from lib import Graph, BinaryGraphCodec

class N(BaseModel):
    pass

class E(BaseModel):
    pass

class M(BaseModel):
    pass

if __name__ == '__main__':
    g = Graph[N, E, M](metadata=M())
    g.add_node(N())
    blob = BinaryGraphCodec[N, E, M].encode(g)
    g2 = BinaryGraphCodec[N, E, M].decode(blob, N, E, M)
