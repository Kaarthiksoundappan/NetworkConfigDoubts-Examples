# 05 - HTTPS

**The idea:** HTTPS is not a new protocol. It is the HTTP of lesson 03 sent through the TLS of lesson 04.

```
  HTTP           HTTPS
+------+       +------+
| HTTP |       | HTTP |   the same text
+------+       +------+
| TCP  |       | TLS  |   the extra layer
+------+       +------+
               | TCP  |
               +------+
 port 80       port 443
```

Open [https_server.py](https_server.py) beside [http_server.py](../03-http/http_server.py): both call the
same `handle_http` function.

## Run it

Terminal 1:
```
python 05-https/https_server.py
```
Terminal 2:
```
python 05-https/https_client.py
curl --cacert certs/ca.crt https://localhost:9005/
```

Without `--cacert certs/ca.crt`, curl refuses, because it does not know our lab CA.

## See the difference

Keep the HTTPS server running, and start the spy:
```
python tools/wiretap.py 9100 9005
```
In a third terminal:
```
python 05-https/https_client.py 127.0.0.1 9100
```

The client sends `Cookie: secret=12345`, just as in lesson 03. This time the wiretap shows only
scrambled bytes. Note that the connection still **works** through the spy. TLS does not stop anyone from
carrying your data; it stops them from reading or changing it.

## What can somebody on the network see?

| | HTTP | HTTPS |
|---|---|---|
| IP addresses and ports | visible | visible |
| Site name | visible | usually visible, through SNI (lesson 06) |
| Path and query (`/cart?id=7`) | visible | hidden |
| Headers, cookies, passwords | visible | hidden |
| Page content | visible | hidden |
| Roughly how much data, and when | visible | visible |

## Try it: mix them up

With both the HTTP (9003) and the HTTPS (9005) server running:

| Command | Result | Why |
|---|---|---|
| `curl https://127.0.0.1:9003/` | `wrong version number` | TLS sent to a plain HTTP port |
| `curl http://localhost:9005/` | Connection reset or empty reply | Plain HTTP sent to a TLS port |

(On Windows, curl words these errors differently.) The HTTP server prints `first bytes: 16 03 01`: that
is how a TLS handshake begins. Remember it, because you will meet it in real server logs.

## Common doubts

**Does the lock icon mean a site is safe?** It means that the connection is private and the name is
correct. A scam site can have a valid certificate for its own name.

**What is TLS termination?** A load balancer or proxy does the TLS work, then talks to the real server
behind it, often by plain HTTP. There, "HTTPS" ends at the proxy. Options:

| Style | Client to proxy | Proxy to server | Can the proxy read HTTP? |
|---|---|---|---|
| Termination | HTTPS | HTTP | Yes |
| Re-encryption | HTTPS | HTTPS (new connection) | Yes |
| Passthrough | HTTPS, passed on untouched | same connection | No, only SNI |

**My app behind a proxy redirects forever. Why?** Often the proxy talks HTTP to the app, the app thinks
the user used HTTP and redirects to HTTPS, again and again. Proxies send `X-Forwarded-Proto: https` so
that the app can know.

**Can HTTPS use another port?** Yes, 443 is only the default. This lesson uses 9005.
