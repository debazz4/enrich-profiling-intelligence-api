import webbrowser

auth_url = "http://127.0.0.1:8000/api/v1/auth/github/login"

print("Opening browser for login...")
webbrowser.open(auth_url)