# Networking, learned by running it

Small programs that show how TCP, DNS, HTTP, TLS, HTTPS and SNI work. Every lesson is something you
run, break and look inside. There is nothing to install beyond Python: no packages are used.

## The one picture to remember

When you open `https://example.com/cart`, these steps happen **in this order**:

| Step | Layer | Question it answers | Lesson |
|---|---|---|---|
| 1 | **DNS** | What is the IP address of `example.com`? | [02](02-udp-and-dns/) |
| 2 | **TCP** | Can I get a reliable connection to that IP, port 443? | [01](01-tcp/) |
| 3 | **TLS** | Are you really `example.com`? Let us agree on encryption keys. | [04](04-tls/) |
| 3a | **SNI** (part of TLS) | Which site's certificate should you show me? | [06](06-sni/) |
| 4 | **HTTP** | Please give me `/cart`. | [03](03-http/) |

Steps 2 + 4 are plain HTTP. Steps 2 + 3 + 4 are **HTTPS** ([05](05-https/)).

Each step needs the previous one to work. So when something breaks, the first useful question is
always **"which step failed?"** That is what [08](08-troubleshooting/) trains.

## Setup

You need Python 3.10+ and OpenSSL (on Windows it comes with Git). From the root of this repository:

```
python tools/make_certs.py      # creates practice certificates in certs/
python tools/check_setup.py     # tells you if this computer is ready
```

If the second command says **INTERCEPTED**, an antivirus or company proxy is opening TLS connections on
this computer and replacing certificates. Lessons 01 to 03 still work. For 04 to 07, use WSL, where the
traffic stays inside Linux. In PowerShell, from this folder:

```
wsl
alias python=python3            # needed in each new WSL terminal
python tools/check_setup.py
```

Interception is a real situation that you will meet at work, so it is worth understanding.
Lesson [04](04-tls/) explains it.

## How to use each lesson

1. Read the idea in the lesson's README.
2. **Guess** what will happen, then run the example.
3. Read the code. The files are short and commented.
4. Do the "Try it" experiments. Breaking things is where you learn most.
5. Read "Common doubts" at the end.

Many lessons need two terminals: a server in one, a client in the other. Run all commands from the root
of the repository. Stop a server with Ctrl+C. On Windows PowerShell type `curl.exe` instead of `curl`.

## Lessons

| # | Topic | You will see |
|---|---|---|
| [01](01-tcp/) | TCP | Connections, ports, why TCP has no "messages", refused vs. timed out |
| [02](02-udp-and-dns/) | UDP and DNS | A DNS question built byte by byte |
| [03](03-http/) | HTTP | HTTP is only text; methods, status codes, headers, Host |
| [04](04-tls/) | TLS and certificates | The handshake, CAs, and real certificate errors made on purpose |
| [05](05-https/) | HTTPS | The same HTTP code in TLS; what a spy can and cannot read |
| [06](06-sni/) | SNI | Two HTTPS sites on one IP; reading SNI off the wire |
| [07](07-mtls/) | Mutual TLS | The server checks the client's certificate too |
| [08](08-troubleshooting/) | Troubleshooting | Finding the broken layer |

## Doubts from real work

| Doubt | About |
|---|---|
| [Kubernetes ingress, Palo Alto and Infoblox](doubts/kubernetes-ingress-paloalto-infoblox.md) | Which traffic a route table sends to the firewall, and where DNS fits |
| [AKS private endpoints and Infoblox](doubts/aks-private-endpoint-infoblox.md) | Why each private endpoint needs a DNS record, and why its traffic can skip the firewall |
| [IBM MQ queue managers on AKS](doubts/ibm-mq-on-aks.md) | Many queue managers in many namespaces: load balancers, MQ's unusual SNI, idle timeouts |
| [IBM MQ with Envoy](doubts/ibm-mq-with-envoy.md) | The same with Envoy Gateway instead of NGINX, and how to move |

## Tools

| Tool | Purpose |
|---|---|
| [tools/wiretap.py](tools/wiretap.py) | Sits between client and server and prints every byte |
| [tools/netcheck.py](tools/netcheck.py) | Tests DNS, TCP, TLS and HTTP in order and explains the failure |
| [tools/make_certs.py](tools/make_certs.py) | Creates the practice CA and certificates |
| [tools/check_setup.py](tools/check_setup.py) | Checks that this computer is ready |

## Safety

- The servers listen on `127.0.0.1`, so only your own computer can reach them.
- `certs/` holds private keys and is ignored by git. Never commit a private key.
- Do not install the lab CA into your system or browser. The lessons do not need it.
- This code is for learning. Use real libraries and servers in production.

## Words you will meet

| Word | Meaning |
|---|---|
| Port | A number that says which program on a machine the data is for |
| Socket | Your program's end of a connection |
| Handshake | The first messages, which set a connection up |
| Certificate | A public document: "this key belongs to this name", signed by a CA |
| Private key | The secret that proves a certificate is yours |
| CA | Certificate Authority: signs certificates. Your system has a list of trusted ones |
| SAN | The list of names a certificate is valid for |
| SNI | The site name the client sends at the start of the TLS handshake |
| ALPN | The client and server choose HTTP/1.1 or HTTP/2 during the TLS handshake |
| mTLS | Mutual TLS: both sides show a certificate |
