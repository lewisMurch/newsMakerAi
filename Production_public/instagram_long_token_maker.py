import requests

def get_instagram_long_lived_token(short_lived_tokens, client_secret):
    url = "https://graph.instagram.com/access_token"
    responses = []

    for token in short_lived_tokens:
        params = {
            'grant_type': 'ig_exchange_token',
            'client_secret': client_secret,
            'access_token': token
        }

        # Print the parameters for debugging
        print(f"Requesting with parameters: {params}")

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()  # Check if the request was successful
            responses.append(response.json())
        except requests.exceptions.HTTPError as http_err:
            responses.append({'error': f'HTTP error occurred: {http_err}', 'status_code': response.status_code, 'response_text': response.text})
        except Exception as err:
            responses.append({'error': f'Other error occurred: {err}'})

    return responses

# List of short-lived tokens
tokens = [
    "yourshort-livedtokens",
    "yourshort-livedtokens",
    "yourshort-livedtokens",
    "yourshort-livedtokens"
]

client_secret = "yourclientsecretkey"

responses = get_instagram_long_lived_token(tokens, client_secret)
for response in responses:
    print(response)
