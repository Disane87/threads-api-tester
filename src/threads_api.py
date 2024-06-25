import requests

class ThreadAPI:

    API_BASE_URL = "https://graph.threads.net"
    AUTH_BASE_URL = "https://threads.net"

    REDIRECT_URI = "https://localhost:5000/auth"

    AUTH_CODE = ""
    SHORT_LIVED_TOKEN = ""
    LONG_LIVED_TOKEN = ""

    USER_ID = 0

    def __init__(self, client_id, client_secret):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret

    def get_auth_url(self):
            return (
                f"{self.AUTH_BASE_URL}/oauth/authorize"
                f"?client_id={self.CLIENT_ID}"
                f"&redirect_uri={self.REDIRECT_URI}"
                f"&scope=threads_basic,threads_content_publish"
                f"&response_type=code"
            )

    def get_user_info(self):
        fields = "id,name,picture"
        url = f"{self.API_BASE_URL}/me?fields={fields}&access_token={self.LONG_LIVED_TOKEN}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": str(e)}
        except ValueError:
            print("Response content is not valid JSON")
            return {"error": "Invalid JSON response"}    

    def get_short_lived_access_token(self):
        url = f"{self.AUTH_BASE_URL}/oauth/access_token"
        payload = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'redirect_uri': self.REDIRECT_URI,
            'code': self.AUTH_CODE
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": str(e)}
        except ValueError:
            print("Response content is not valid JSON")
            return {"error": "Invalid JSON response"}


    def get_long_lived_access_token(self):
        url = f"{self.AUTH_BASE_URL}/oauth/access_token"
        payload = {
            'client_id': self.CLIENT_ID,
            'client_secret': self.CLIENT_SECRET,
            'grant_type': 'fb_exchange_token',
            'fb_exchange_token': self.SHORT_LIVED_TOKEN
        }
        try:
            response = requests.post(url, data=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": str(e)}
        except ValueError:
            print("Response content is not valid JSON")
            return {"error": "Invalid JSON response"}


    def get_recent_posts(self):
        limit = 6
        fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
        url = f"{self.API_BASE_URL}/{self.USER_ID}/threads&access_token={self.LONG_LIVED_TOKEN}&limit={limit}&fields={fields}"
        response = requests.get(url)

        if response.status_code != 200:
            return {"error": response.json()}

        return response.json()

    def upload_image(self, image_url, caption):
        create_container_url = f"{self.API_BASE_URL}/{self.USER_ID}/media"
        publish_url = f"{self.API_BASE_URL}/{self.USER_ID}/media_publish"
        params = {
            "access_token": self.LONG_LIVED_TOKEN,
            "image_url": image_url,
            "caption": caption
        }
        response = requests.post(create_container_url, params=params)

        if response.status_code != 200:
            return {"error": response.text}

        container_id = response.json().get("id")

        if container_id:
            publish_response = requests.post(publish_url, params={
                "access_token": self.LONG_LIVED_TOKEN,
                "creation_id": container_id
            })
            return publish_response.json()
        else:
            return {"error": response.json()}
