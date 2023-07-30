import requests

# Enter a proxy IP address and port.

proxy = 'http://129.226.33.104:3218'

# Initialize a URL.

url = 'https://ipecho.net/plain'

# Send a GET request to the url and pass the proxy as a parameter.

page = requests.get(url,
proxies={"http": proxy, "https": proxy})

# Prints the content of the requested url.

print(page.text)