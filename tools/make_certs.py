"""Create a private lab CA and the certificates used in lessons 04 to 07.

    python tools/make_certs.py

Everything goes into certs/ (ignored by git). Nothing is installed on your computer,
so your browser will NOT trust these certificates. That is intentional.
"""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CERTS = Path(__file__).resolve().parent.parent / "certs"


def find_openssl():
    found = shutil.which("openssl")
    if found:
        return found
    for base in (os.environ.get("ProgramFiles"), os.environ.get("LOCALAPPDATA")):
        if base:
            for git in (Path(base) / "Git", Path(base) / "Programs" / "Git"):
                for sub in ("mingw64", "usr"):
                    exe = git / sub / "bin" / "openssl.exe"
                    if exe.exists():
                        return str(exe)
    sys.exit("openssl not found. Install Git for Windows (it includes openssl).")


def openssl(*args):
    result = subprocess.run([find_openssl(), *args], cwd=CERTS, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"openssl {' '.join(args)}\nfailed:\n{result.stderr}")


def new_key(name):
    openssl("genpkey", "-algorithm", "EC", "-pkeyopt", "ec_paramgen_curve:P-256",
            "-out", f"{name}.key")


def write_config(name, common_name, extensions):
    text = "\n".join(["[req]", "prompt = no", "distinguished_name = dn", "[dn]",
                      f"CN = {common_name}", "[ext]", *extensions, ""])
    (CERTS / f"{name}.cnf").write_text(text)


def make_ca():
    """A root CA certificate signs itself. Trust in it must be granted by hand."""
    new_key("ca")
    write_config("ca", "Lab Root CA", ["basicConstraints = critical, CA:TRUE",
                                       "keyUsage = critical, keyCertSign, cRLSign",
                                       "subjectKeyIdentifier = hash"])
    openssl("req", "-x509", "-new", "-key", "ca.key", "-config", "ca.cnf",
            "-extensions", "ext", "-days", "365", "-out", "ca.crt")
    print("  ca.crt          the certificate authority")


def make_leaf(name, note, san=None, usage="serverAuth", days="365"):
    """key -> signing request (CSR) -> the CA signs it -> certificate"""
    extensions = ["basicConstraints = critical, CA:FALSE",
                  "keyUsage = critical, digitalSignature",
                  f"extendedKeyUsage = {usage}",
                  "subjectKeyIdentifier = hash",
                  "authorityKeyIdentifier = keyid"]
    if san:
        # The SAN list holds the names a certificate is valid for. Modern clients ignore CN.
        extensions.append(f"subjectAltName = {san}")
    new_key(name)
    write_config(name, name, extensions)
    openssl("req", "-new", "-key", f"{name}.key", "-config", f"{name}.cnf",
            "-out", f"{name}.csr")
    openssl("x509", "-req", "-in", f"{name}.csr", "-CA", "ca.crt", "-CAkey", "ca.key",
            "-CAcreateserial", "-days", days, "-extfile", f"{name}.cnf",
            "-extensions", "ext", "-out", f"{name}.crt")
    print(f"  {name + '.crt':<15} {note}")


def main():
    CERTS.mkdir(exist_ok=True)
    print(f"Using {find_openssl()}\nWriting to {CERTS}")
    make_ca()
    make_leaf("localhost", "for localhost and 127.0.0.1", "DNS:localhost, IP:127.0.0.1")
    make_leaf("alpha.test", "for alpha.test", "DNS:alpha.test")
    make_leaf("beta.test", "for beta.test", "DNS:beta.test")
    make_leaf("expired", "expired on purpose", "DNS:localhost, IP:127.0.0.1", days="0")
    make_leaf("client", "identifies a client (lesson 07)", usage="clientAuth")
    time.sleep(1.1)  # let the zero-day certificate actually expire
    print("Done.")


if __name__ == "__main__":
    main()
