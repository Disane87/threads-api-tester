import os
from flask import request, render_template, redirect, url_for

from src.threads_api import ThreadAPI

def setup_routes(app, config, threadsAPI: ThreadAPI):
    @app.route('/auth')
    def auth():
        config.received_code = request.args.get('code')
        return render_template('auth.html')

    @app.route('/tokens', methods=['GET', 'POST'])
    def tokens():
        if request.method == 'POST':
            if 'image_url' in request.form and 'account_id' in request.form:
                image_url = request.form['image_url']
                caption = request.form.get('caption', '')
                account_id = request.form['account_id']

                response = threadsAPI.upload_image(image_url, caption)
                if response.get('error'):
                    print(f"Error uploading image: {response['error']}")


        user = threadsAPI.get_user_info()
        
        accounts = {}
        media_data = threadsAPI.get_recent_posts()
        accounts[threadsAPI.USER_ID] = {
            'media':  media_data.get('data', []),
            'info': threadsAPI.USER_ID
        }


        return render_template('tokens.html', accounts=accounts, 
                               short_lived_token_response=threadsAPI.SHORT_LIVED_TOKEN,
                               long_lived_token_response=threadsAPI.LONG_LIVED_TOKEN,
                               code=threadsAPI.AUTH_CODE,
                               user={
                                "id": threadsAPI.USER_ID,
                                "name": user.get('name', ''), 
                                "picture": user.get('picture', ''),
                            }
                        )

    # @app.route('/renew_tokens', methods=['POST'])
    # def renew_tokens():
    #     config.long_lived_token_response = get_long_lived_access_token(config.long_lived_token_response['access_token'], config.client_secret)
    #     return redirect(url_for('tokens'))
