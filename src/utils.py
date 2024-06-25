import os
import ssl
from attr import field, fields
import requests
from OpenSSL import crypto


def create_self_signed_cert(cert_file, key_file):
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 4096)

    cert = crypto.X509()
    cert.get_subject().C = "DE"
    cert.get_subject().ST = "NRW"
    cert.get_subject().L = "Cologne"
    cert.get_subject().O = "MyCompany"
    cert.get_subject().OU = "MyDivision"
    cert.get_subject().CN = "threads-sample.meta"
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(key)
    cert.sign(key, 'sha256')

    with open(cert_file, "wt") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert).decode("utf-8"))
    with open(key_file, "wt") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key).decode("utf-8"))

def start_flask_server(app, config):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(config.cert_file, config.key_file)
    app.run(port=5000, ssl_context=context)

