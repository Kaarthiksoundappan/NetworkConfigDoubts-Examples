# 07 - Mutual TLS (mTLS)

**The idea:** in normal TLS only the server shows a certificate. In mutual TLS the client must show one
too. It is common between services, in banking APIs and for devices.

| | Normal TLS | Mutual TLS |
|---|---|---|
| Server proves who it is | Yes | Yes |
| Client proves who it is | Not in TLS (perhaps later, by password or token) | Yes, by certificate |
| Encryption | Yes | Yes, the same |

## Run it

Use WSL if `tools/check_setup.py` reported INTERCEPTED.

Terminal 1:
```
python 07-mtls/mtls_server.py
```
Terminal 2:
```
python 07-mtls/mtls_client.py
```

The only difference from lesson 04, on the server, is two lines:
```python
context.load_verify_locations(cert("ca.crt"))   # whose client certificates do we accept?
context.verify_mode = ssl.CERT_REQUIRED         # no certificate, no entry
```

## Try it

1. In `mtls_client.py`, load `alpha.test.crt` and `alpha.test.key` in place of the client files. It is
   signed by the same CA, yet the server refuses. Read the server's message, then find
   `extendedKeyUsage` in [make_certs.py](../tools/make_certs.py).
2. On the server, change `CERT_REQUIRED` to `CERT_OPTIONAL`. What happens to case 1, and why must the code
   then handle a client that has no certificate?

## Common doubts

**Why does the client think the handshake succeeded before it is rejected?** In TLS 1.3 the client
finishes first and can start sending before the server has checked its certificate. So the refusal only
appears at the first read.

**Do both sides need the same CA?** No. The server's list says which CAs may sign *clients*. The client's
list says which CAs may sign *servers*. This lab uses one CA to stay simple.

**mTLS proved who the client is. Is it now allowed to do everything?** No. That is authentication (who are
you?). The application must still decide on authorization (what may you do?).

**Why does mTLS break behind a load balancer?** The load balancer ends the TLS connection, so the server
behind it never sees the client's certificate. The balancer must check it and pass the details on
safely, or use TLS passthrough.
