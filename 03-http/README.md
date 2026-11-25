# 03 - HTTP

**The idea:** HTTP/1.1 is text sent through a TCP connection. The client sends a request and the server
sends a response. That is all.

```
GET /new HTTP/1.1            <- method, path, version
Host: shop.test              <- headers
User-Agent: my-first-client
                             <- blank line: headers are finished
```
```
HTTP/1.1 200 OK              <- version, status code, reason
Content-Type: text/plain
Content-Length: 24           <- how many bytes the body has

You found the new page.      <- body
```

## Run it

Terminal 1:
```
python 03-http/http_server.py
```
Terminal 2:
```
python 03-http/raw_http_client.py
python 03-http/raw_http_client.py example.com 80 /
```

Then open <http://127.0.0.1:9003/> in a browser and look at the server's terminal. Your browser sends
the same kind of text, only with more headers.

Next, read [shared/tiny_http.py](../shared/tiny_http.py). It is a whole HTTP server in about 100 lines.

## Try it

In PowerShell type `curl.exe`. `-v` shows the conversation.

| Command | What it shows |
|---|---|
| `curl -v http://127.0.0.1:9003/` | Request (`>`) and response (`<`) |
| `curl -v http://127.0.0.1:9003/nope` | 404: the server works, the path does not exist |
| `curl -v http://127.0.0.1:9003/old` | 302 and a `Location` header. curl stops here |
| `curl -v -L http://127.0.0.1:9003/old` | `-L` follows the redirect: **two** requests |
| `curl -v -d "hello" http://127.0.0.1:9003/echo` | POST with a body |
| `curl -I http://127.0.0.1:9003/` | HEAD: only headers |
| `curl -H "Host: shop.test" http://127.0.0.1:9003/` | Same IP and port, a different site! |
| `curl -v --cookie "visited=yes" http://127.0.0.1:9003/cookie` | Cookies are just headers |

**Now spy on it.** Keep the server running and start:
```
python tools/wiretap.py 9100 9003
```
and in a third terminal:
```
curl -H "Cookie: secret=12345" http://127.0.0.1:9100/
```
The wiretap prints your secret cookie. Anyone on the path of plain HTTP can do this. Lesson 05 fixes it.

## Status codes

| Code | Meaning |
|---|---|
| 200 | OK |
| 301 / 302 | Moved: go to the address in `Location` |
| 400 | The server did not understand the request |
| 401 | Not logged in |
| 403 | You are not allowed |
| 404 | The path does not exist |
| 500 | The server's code failed |
| 502 | A proxy got a bad answer, or none, from the server behind it |
| 503 | Temporarily unavailable |
| 504 | A proxy waited too long for the server behind it |

4xx means "the request has a problem". 5xx means "the server has a problem".

## Common doubts

**Is a 404 a network problem?** No. Any HTTP status code proves that DNS, TCP (and TLS, for HTTPS)
worked: something received your request and answered it.

**Why is the `Host` header needed?** TCP only carries the IP and port. Many sites share one IP, so the
name must be sent inside the request. Lesson 06 shows why HTTPS needs the name even earlier.

**HTTP is stateless. How do logins work?** The server sends a cookie, and the browser returns it with
every later request. Or the client sends a token in an `Authorization` header.

**HTTP/1.1, HTTP/2, HTTP/3?** Same methods, headers and status codes, sent differently: 1.1 is text over
TCP, 2 is binary with many requests sharing one TCP connection, 3 runs over QUIC, which uses UDP.
