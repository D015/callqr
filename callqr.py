from app import app
# from app import db
# import ssl
#
# ctx = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) # use TLS to avoid POODLE
# ctx.load_cert_chain('certificate.crt', 'private.key')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005)