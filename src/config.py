import os

class Config:
    def __init__(self):

        self.cert_file = 'cert.pem'
        self.key_file = 'key.pem'

    def cert_exists(self):
        return os.path.exists(self.cert_file) and os.path.exists(self.key_file)

    
