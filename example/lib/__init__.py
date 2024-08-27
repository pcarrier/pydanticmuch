from __future__ import annotations

from collections import defaultdict

from cbor2 import dumps
from cbor2 import loads
from pydantic import BaseModel

class Node[N: BaseModel, E: BaseModel, M: BaseModel](BaseModel):
    graph: Graph[N, E, M]
    position: int
    payload: N

    @property
    def head_of(self) -> list[Edge[N, E, M]]:
        return self.graph.heads[self.position]
    @property
    def tail_of(self) -> list[Edge[N, E, M]]:
        return self.graph.tails[self.position]


class Edge[N: BaseModel, E: BaseModel, M: BaseModel](BaseModel):
    payload: E
    head: Node[N, E, M]
    tail: Node[N, E, M]


class Graph[N: BaseModel, E: BaseModel, M: BaseModel](BaseModel):
    nodes: list[Node[N, E, M]] = []
    heads: dict[int, list[Edge[N, E, M]]] = defaultdict(list)
    tails: dict[int, list[Edge[N, E, M]]] = defaultdict(list)
    metadata: M

    def add_node(self, payload: N) -> Node[N, E, M]:
        n = Node[N, E, M](graph=self, position=len(self.nodes), payload=payload)
        self.nodes.append(n)
        return n

    def add_edge(self, payload: E, head: Node[N, E, M], tail: Node[N, E, M]) -> Edge[N, E, M]:
        if self != head.graph:
            raise ValueError("Head node is not in this graph")
        if self != tail.graph:
            raise ValueError("Tail node is not in this graph")
        e = Edge[N, E, M](head=head, tail=tail, payload=payload)
        self.heads[head.position].append(e)
        self.tails[tail.position].append(e)
        return e


class BinaryGraphCodec[N: BaseModel, E: BaseModel, M: BaseModel]:
    @staticmethod
    def encode(graph: Graph[N, E, M]) -> bytes:
        return dumps(
            (
                [
                    (
                        node.payload.model_dump(),
                        [
                            (
                                edge.payload.model_dump(),
                                edge.tail.position,
                            )
                            for edge in node.head_of
                        ],
                    )
                    for node in graph.nodes
                ],
                graph.metadata.model_dump(),
            ),
            canonical=True,
        )

    @staticmethod
    def decode(
            data: bytes, n: type[N], e: type[E], m: type[M]
    ) -> Graph[N, E, M]:
        (nodes, metadata) = loads(data)
        graph = Graph[N, E, M](nodes=[], metadata=m.model_validate(metadata))
        for position, node in enumerate(nodes):
            n = Node[N, E, M](
                graph=graph,
                position=position,
                payload=n.model_validate(node[0]),
            )
            graph.nodes.append(n)
        for position, node in enumerate(nodes):
            for edge in node[1]:
                graph.add_edge(
                    e.model_validate(edge[0]),
                    graph.nodes[position],
                    graph.nodes[edge[1]]
                )
        return graph
