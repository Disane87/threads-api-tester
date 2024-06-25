from ctypes.wintypes import SHORT
from re import S
import requests
import html

class ThreadAPI:

    API_BASE_URL: str = "https://graph.threads.net"
    REDIRECT_URI: str = "https://threads-sample.meta:5000/callback"
    AUTH_URL: str = "https://threads.net/oauth/authorize"

    AUTH_CODE: str | None = None
    SHORT_LIVED_TOKEN: str | None = None
    LONG_LIVED_TOKEN: str | None = None

    SCOPES: str = "threads_basic,threads_content_publish"

    USER_ID: int = 0

    def __init__(self, client_id: str, client_secret: str):
        self.CLIENT_ID = client_id
        self.CLIENT_SECRET = client_secret
        self.REDIRECT_URI = html.escape(self.REDIRECT_URI)

        print(f"Client ID: {self.CLIENT_ID}")
        print(f"Client Secret: {self.CLIENT_SECRET}")
        print(f"Redirect URI: {self.REDIRECT_URI}")

    def get_auth_url(self) -> str:
        return (
            f"{self.AUTH_URL}"
            f"?client_id={self.CLIENT_ID}"
            f"&redirect_uri={self.REDIRECT_URI}"
            f"&scope={self.SCOPES}"
            f"&response_type=code"
        )
    
    def set_auth_code(self, code: str):
        print(f"Received auth code: {code}")
        self.AUTH_CODE = code

    def get_user_info(self, user_id: int = 0) -> dict:
        if user_id == 0:
            user_id = self.USER_ID

        fields = "id,username,threads_profile_picture_url,threads_biography"
        url = f"{self.API_BASE_URL}/{user_id}?access_token={self.LONG_LIVED_TOKEN}&fields={fields}"
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

    def get_short_lived_access_token(self) -> str | dict[str, str]:
        if self.SHORT_LIVED_TOKEN:
            return str(self.SHORT_LIVED_TOKEN)

        url = f"{self.API_BASE_URL}/oauth/access_token"
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
            token_response = response.json()
            self.SHORT_LIVED_TOKEN = token_response.get("access_token")
            self.USER_ID = token_response.get("user_id")

            print(f"Short-lived token: {self.SHORT_LIVED_TOKEN}")
            print(f"User ID: {self.USER_ID}")

            return str(self.SHORT_LIVED_TOKEN)
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": f"HTTP request error: {e}\n\n{response.text}"}
        except ValueError:
            print("Response content is not valid JSON")
            return {"error": "Invalid JSON response"}

    def get_long_lived_access_token(self) -> str | dict[str, str]:
        if self.LONG_LIVED_TOKEN:
            return str(self.LONG_LIVED_TOKEN)
        
        url = f"{self.API_BASE_URL}/access_token?access_token={self.SHORT_LIVED_TOKEN}&client_secret={self.CLIENT_SECRET}&grant_type=th_exchange_token"
        try:
            response = requests.get(url)
            response.raise_for_status()
            token_response = response.json()
            self.LONG_LIVED_TOKEN = token_response.get("access_token")
            print(f"Long-lived token: {self.LONG_LIVED_TOKEN}")

            return str(self.LONG_LIVED_TOKEN)
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": f"HTTP request error: {e}\n\n{response.text}"}
        except ValueError:
            print("Response content is not valid JSON")
            return {"error": "Invalid JSON response"}

    def get_recent_posts(self) -> dict:
        if not self.LONG_LIVED_TOKEN:
            return {"error": "No long-lived access token available"}
        
        limit = 6
        fields = "id,media_product_type,media_type,media_url,permalink,owner,username,text,timestamp,shortcode,thumbnail_url,children,is_quote_post"
        url = f"{self.API_BASE_URL}/{self.USER_ID}/threads?access_token={self.LONG_LIVED_TOKEN}&limit={limit}&fields={fields}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": str(e)}

    def upload_image(self, image_url: str, caption: str) -> dict:
        if not self.LONG_LIVED_TOKEN:
            return {"error": "No long-lived access token available"}
        
        create_container_url = f"{self.API_BASE_URL}/{self.USER_ID}/threads?media_type=IMAGE&image_url={image_url}&text={caption}&access_token={self.LONG_LIVED_TOKEN}"
        publish_url = f"{self.API_BASE_URL}/{self.USER_ID}/threads_publish?access_token={self.LONG_LIVED_TOKEN}"

        try:
            response = requests.post(create_container_url)
            response.raise_for_status()
            container_id = response.json().get("id")

            if container_id:
                publish_response = requests.post(f"{publish_url}&creation_id={container_id}")
                publish_response.raise_for_status()
                return publish_response.json()
            else:
                return {"error": "Failed to create media container"}
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error: {e}")
            return {"error": f"HTTP request error: {e}\n\n{response.text}"}
