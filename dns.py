# -*- coding: utf-8 -*-
# vim: tabstop=4 shiftwidth=4 expandtab

"""Lightweight DNS server for whitelisting domains.

This script listens for DNS queries and responds with a configured IP address
for whitelisted domains while resolving other domains normally. It is intended
to emulate the behaviour of services such as Shecan.
"""

import sys
import socket
import argparse
import logging
from dnslib import DNSRecord, DNSHeader, RR, A, QTYPE
from os import environ


def main() -> None:
    """Run the DNS server based on provided CLI arguments."""
    parser = argparse.ArgumentParser(description="Simple DNS proxy")
    parser.add_argument(
        "--ip",
        help="listen IP address; use ENV to read PUB_IP from environment",
        action="store",
        type=str,
        default="0.0.0.0",
    )
    parser.add_argument(
        "--whitelist",
        help="whitelisted domains file; use ALL or DNS_ALLOW_ALL=YES to allow all",
        action="store",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--port", help="listen port", action="store", type=int, default=53
    )
    parser.add_argument("--debug", help="enable debug logging", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(message)s",
    )

    if args.ip.upper() == "ENV":
        env_ip = environ.get("PUB_IP")
        if not env_ip:
            logging.error("PUB_IP environment variable not set")
            sys.exit(1)
        args.ip = env_ip

    udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_sock.bind(("0.0.0.0", args.port))

    allow_all = environ.get("DNS_ALLOW_ALL") == "YES" or (
        args.whitelist and args.whitelist.upper() == "ALL"
    )
    w_list = []
    if not allow_all and args.whitelist:
        try:
            with open(args.whitelist) as f:
                w_list.extend(f.read().splitlines())
        except FileNotFoundError:
            logging.error("Whitelist file %s not found", args.whitelist)
            sys.exit(1)

    logging.debug("IP: %s Port: %s Allow All: %s", args.ip, args.port, allow_all)

    try:
        while True:
            data, addr = udp_sock.recvfrom(1024)
            d = DNSRecord.parse(data)
            for question in d.questions:
                qdom = question.get_qname()
                r = d.reply()
                if not allow_all and w_list and not any(
                    s.lstrip(".") in str(qdom) for s in w_list
                ):
                    try:
                        realip = socket.gethostbyname(qdom.idna())
                    except Exception as e:  # pragma: no cover - debug only
                        logging.debug(e)
                        realip = args.ip
                    r.add_answer(RR(qdom, rdata=A(realip), ttl=60))
                    logging.debug("Request: %s --> %s", qdom.idna(), realip)
                else:
                    r.add_answer(RR(qdom, rdata=A(args.ip), ttl=60))
                    logging.debug("Request: %s --> %s", qdom.idna(), args.ip)
                udp_sock.sendto(r.pack(), addr)
    except KeyboardInterrupt:  # pragma: no cover - interactive use
        logging.debug("done.")
    finally:
        udp_sock.close()


if __name__ == "__main__":
    main()
