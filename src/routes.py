from asyncio import threads
from math import e
from re import S
from flask import make_response, request, render_template, redirect, url_for

from src.threads_api import ThreadAPI

def setup_routes(app, config, threadsAPI: ThreadAPI):
    @app.route('/callback')
    def auth():
        config.received_code = request.args.get('code')
        threadsAPI.set_auth_code(config.received_code)

        return render_template('auth.html')

    @app.route('/tokens', methods=['GET', 'POST'])
    def tokens():          

        match request.method:
            case 'GET':
                short_lived_access_token = threadsAPI.get_short_lived_access_token()
                if type(short_lived_access_token) is not str:
                    response = make_response(short_lived_access_token['error'], 200) # type: ignore
                    response.mimetype = "text/plain"
                    return response
            
                long_lived_access_token = threadsAPI.get_long_lived_access_token()
                if type(long_lived_access_token) is not str:
                    response = make_response(long_lived_access_token['error'], 200) # type: ignore
                    response.mimetype = "text/plain"
                    return response

                accounts = {}
                media_data = threadsAPI.get_recent_posts()
                accounts[threadsAPI.USER_ID] = {
                    'media':  media_data.get('data', []),
                    'info': threadsAPI.USER_ID
                }


                return render_template('tokens.html', 
                    accounts=accounts, 
                    short_lived_token_response=threadsAPI.SHORT_LIVED_TOKEN,
                    long_lived_token_response=threadsAPI.LONG_LIVED_TOKEN,
                    code=threadsAPI.AUTH_CODE,
                    user={
                        "id": threadsAPI.USER_ID,
                        "name": "user.get('name', '')", 
                        "picture": "user.get('picture', '')",
                    }
                )
            
            case 'POST':
                if 'image_url' in request.form and 'account_id' in request.form:
                    image_url = request.form['image_url']
                    caption = request.form.get('caption', '')
                    account_id = request.form['account_id']

                    response = threadsAPI.upload_image(image_url, caption)
                    if response.get('error'):
                        print(f"Error uploading image: {response['error']}")
            
        
        

    # @app.route('/renew_tokens', methods=['POST'])
    # def renew_tokens():
    #     config.long_lived_token_response = get_long_lived_access_token(config.long_lived_token_response['access_token'], config.client_secret)
    #     return redirect(url_for('tokens'))