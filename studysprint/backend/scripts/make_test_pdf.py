"""Write a Computer Networks test lecture to sample_data/: `python scripts/make_test_pdf.py`."""

import sys
import textwrap
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from app.demo import make_pdf  # noqa: E402

PAGES = [
    (
        "The OSI Model",
        "The OSI model is a seven layer framework that describes how data moves across a "
        "network. The physical layer sends raw bits over a cable or radio link. The network "
        "layer chooses a path for packets between different networks. The transport layer "
        "provides end to end delivery between applications on two hosts. Encapsulation means "
        "each layer wraps the data from the layer above with its own header.",
    ),
    (
        "TCP and UDP",
        "TCP is a connection oriented protocol that guarantees reliable, ordered delivery of "
        "data. Before sending data, TCP performs a three way handshake using SYN, SYN-ACK and "
        "ACK segments. UDP is a connectionless protocol that sends datagrams without "
        "guaranteeing delivery or order. Video calls and online games often use UDP because "
        "low latency matters more than retransmitting lost packets.",
    ),
    (
        "IP Addressing and Subnets",
        "An IP address is a numeric label that identifies a device on a network. IPv4 "
        "addresses are 32 bits long, while IPv6 addresses are 128 bits long. A subnet mask "
        "separates the network portion of an address from the host portion. NAT lets many "
        "devices on a private network share a single public IP address.",
    ),
    (
        "DNS Resolution",
        "DNS is a distributed system that translates domain names into IP addresses. A "
        "recursive resolver queries root servers, then top level domain servers, then the "
        "authoritative name server for the domain. Resolvers cache answers for the time set "
        "by the TTL value, which reduces lookup latency and load on name servers.",
    ),
    (
        "Routing",
        "A router is a device that forwards packets between networks using a routing table. "
        "Distance vector protocols share routing tables with neighbours, while link state "
        "protocols flood information about links so every router can compute shortest paths. "
        "Dijkstra's algorithm computes the shortest path from one router to every other router "
        "in a link state network.",
    ),
]

target = BACKEND.parent / "sample_data" / "networks-lecture.pdf"
target.parent.mkdir(exist_ok=True)
target.write_bytes(make_pdf([[title, ""] + textwrap.wrap(body, 88) for title, body in PAGES]))
print(f"wrote {target}")
