# Threads API tester 🎉

Python script to extract your threads api access tokens to automate stuff 🔥

## Installation

Just clone the repo and install deps

```bash
pip install -r requirements.txt
```

## Usage/Examples

Just simply execute the script. Create an `.env` file with the content of `.env.example` and your Threads `CLIENT_ID` and `CLIENT_SECRET`. If you donÄt know how to get these values, head over to my blog:

[Threads API is here ☝️](https://blog.disane.dev/en/threads-api-is-here/)

Please add `https://localhost:5000/auth` to your Threads OAuth callback url to get the sample working. If you encounnter an insecure SSL warning of your browser, it's just normal, because this script generates a self signed certificate for you.

```bash
python main.py --client-id [instagram-client-id] --client-secret [instagram-client-secret]

```
