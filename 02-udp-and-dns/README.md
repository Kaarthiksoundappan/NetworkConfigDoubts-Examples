# 02 - UDP and DNS

## UDP

**The idea:** UDP sends single messages with no connection, no confirmation and no resending. It is
simple and fast.

| | TCP | UDP |
|---|---|---|
| Handshake first | Yes | No |
| Lost data is resent | Yes | No |
| Keeps order | Yes | No |
| Keeps message boundaries | No | Yes |
| Used by | HTTP/1.1, HTTP/2, SSH | DNS, video calls, games, HTTP/3 (through QUIC) |

```
python 02-udp-and-dns/udp_demo.py
```

## DNS

**The idea:** DNS turns a name (`example.com`) into an IP address. Usually it is one small UDP question
and one small UDP answer, on port 53.

```
python 02-udp-and-dns/dns_query.py example.com
python 02-udp-and-dns/dns_query.py www.github.com
python 02-udp-and-dns/dns_query.py no-such-host.invalid
```

| Record | Holds |
|---|---|
| A | An IPv4 address |
| AAAA | An IPv6 address |
| CNAME | An alias: "look up this other name instead" |
| MX | Where to deliver email |
| TXT | Free text, often used to prove that you own a domain |
| NS | Which servers are in charge of this domain |

**TTL** is how many seconds an answer may be cached. Run the same query twice and watch it count down.

## Try it

1. Ask two different servers about the same name: add `8.8.8.8` or `1.1.1.1` at the end. Big sites often
   give different addresses, to send you to a nearby server.
2. Compare with the standard tools: `nslookup www.github.com` or, on Linux, `dig www.github.com`.
3. See other record types: `nslookup -type=MX gmail.com`.

## Common doubts

**I changed a DNS record. Why do I still get the old address?** The old answer is cached until its TTL
ends: in your app, your system, your router or your DNS server. Clear the Windows cache with
`ipconfig /flushdns`.

**Why does one computer find the name and another does not?** They may use different DNS servers.
Company names often exist only on the company's internal DNS server. Also check the hosts file
(`C:\Windows\System32\drivers\etc\hosts` or `/etc/hosts`), which is normally checked before DNS.

**Is DNS encrypted?** Classic DNS is not, so people on the network path can see which names you look up.
DNS over HTTPS (DoH) and DNS over TLS (DoT) encrypt it.

**Does DNS know about ports or paths?** An A record knows neither. It only maps a name to an address.
`example.com/a` and `example.com/b` always use the same lookup.

**What is NXDOMAIN?** "This name does not exist." It differs from "the name exists but has no record of
this type", where the status is fine but there are 0 answers.
