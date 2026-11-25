# 08 - Troubleshooting: which layer is broken?

**The idea:** check the layers in order, DNS, TCP, TLS, HTTP. The first one that fails is where to look.

```
python tools/netcheck.py https://example.com
```

## Exercises

Predict the layer that fails **before** you run each one:

```
python tools/netcheck.py https://no-such-host.invalid
python tools/netcheck.py http://127.0.0.1:9555
python tools/netcheck.py http://192.0.2.1
python tools/netcheck.py https://expired.badssl.com
python tools/netcheck.py https://self-signed.badssl.com
python tools/netcheck.py https://wrong.host.badssl.com
python tools/netcheck.py https://example.com/no-such-page
```

[badssl.com](https://badssl.com) is a public site made for testing TLS errors.

With the servers of lessons 03 and 05 running:

```
python tools/netcheck.py https://127.0.0.1:9003
python tools/netcheck.py http://127.0.0.1:9005
python tools/netcheck.py https://localhost:9005
python tools/netcheck.py https://localhost:9005 --ca certs/ca.crt
```

## Cheat sheet

| Message | Layer | Look at |
|---|---|---|
| Could not resolve host / getaddrinfo failed / NXDOMAIN | DNS | Spelling, DNS record, which DNS server, hosts file |
| Connection refused | TCP | Is the service running? Right port? Listening only on 127.0.0.1? |
| Connection timed out | TCP | Firewall, security group, wrong IP, routing, VPN |
| Connection reset | TCP or above | Proxy or firewall cut it, server crashed, TLS/HTTP mix-up |
| wrong version number | TLS | HTTPS sent to a plain HTTP port |
| unable to get local issuer certificate | TLS | Private CA, missing intermediate, TLS interception |
| self-signed certificate | TLS | Same, and check that you reached the right server |
| Hostname mismatch | TLS | SAN list, SNI, connecting by IP |
| certificate has expired | TLS | Renew; was the server reloaded? Is the clock right? |
| handshake failure / protocol version | TLS | TLS versions and ciphers, missing client certificate |
| certificate required | TLS | The server wants mTLS |
| 4xx | HTTP | Path, method, headers, login |
| 421 | HTTP | SNI and Host do not match |
| 500 | HTTP | The application's logs |
| 502 / 503 / 504 | HTTP | The server behind the proxy |

## Doing it by hand

| Layer | Windows (PowerShell) | Linux / WSL |
|---|---|---|
| DNS | `nslookup example.com` | `dig example.com` |
| TCP | `Test-NetConnection example.com -Port 443` | `nc -vz example.com 443` |
| TLS | `curl.exe -v https://example.com` | `openssl s_client -connect example.com:443 -servername example.com` |
| HTTP | `curl.exe -v https://example.com` | `curl -v https://example.com` |

`ping` uses another protocol (ICMP), which many servers block. A failed ping does not prove that a site is
down, and a working ping does not prove that port 443 is open.

## Going deeper

[Wireshark](https://www.wireshark.org) shows every packet. Capture on the loopback adapter while you
run lesson 01, with the filter `tcp.port == 9001`, and find SYN, SYN-ACK, ACK. Then look at lesson 06 with
the filter `tls.handshake.extensions_server_name`.
