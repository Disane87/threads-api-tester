import argparse
import ssl
import threading
import time
import webbrowser
import os
from flask import Flask
from dotenv import load_dotenv
from src.config import Config
from src.routes import setup_routes
from src.utils import create_self_signed_cert, start_flask_server
from src.threads_api import ThreadAPI
# from pyngrok import ngrok

def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description='Get Threads long-lived access token.')
    parser.add_argument('--client-id', type=int, default=os.getenv('CLIENT_ID'), help='Your Threads app client ID')
    parser.add_argument('--client-secret', type=str, default=os.getenv('CLIENT_SECRET'), help='Your Threads app client secret')
    parser.add_argument('--ngrok-auth-token', type=str, default=os.getenv('NGROK_AUTH_TOKEN'), help='Your ngrok auth token')
    
    args = parser.parse_args()
    print("Args: ", args)
    threadsAPI = ThreadAPI(args.client_id, args.client_secret)
    config = Config()

    if not threadsAPI.CLIENT_ID or not threadsAPI.CLIENT_SECRET or not threadsAPI.REDIRECT_URI or not args.ngrok_auth_token:
        print("Error: Missing required parameters. Ensure they are set in the .env file or passed as arguments.")
        return

    if not config.cert_exists():
        create_self_signed_cert(config.cert_file, config.key_file)


    app = Flask(__name__, template_folder='../public', static_folder='../static')

    setup_routes(app, config, threadsAPI)

    # # Setze deinen Authentifizierungstoken
    # ngrok.set_auth_token(args.ngrok_auth_token)

    # # Starte einen HTTP-Tunnel auf dem gewünschten Port 5000
    # nrgok = ngrok.connect("5000", bind_tls=True)
    # print(f"Ngrok-Tunnel aktiv unter der URL: {nrgok.public_url}")

    # threadsAPI.REDIRECT_URI = f"{nrgok.public_url}/auth"

    server_thread = threading.Thread(target=start_flask_server, args=(app, config))
    server_thread.daemon = True
    server_thread.start()
    auth_url = threadsAPI.get_auth_url()
    print(f"Opening the authorization URL in your browser: {auth_url}")

    webbrowser.open(auth_url, new=2, autoraise=True)

    while not threadsAPI.AUTH_CODE:
        print("Waiting for the authorization code...")
        time.sleep(1)

    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()
