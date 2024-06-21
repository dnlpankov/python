# %%
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

import requests
from requests_oauthlib import OAuth2Session
import json
# Replace these with your own client ID and secret

client_id = 'jIjODSTBXb7DtLQDLNQGx76lee0nerMT'
client_secret = 'hn9kvUApp6bQ1kTFjTWkx5Fit1JmaIHf'
redirect_uri = 'http://localhost:5000/oauth/callback'

# OAuth2 endpoints
authorization_base_url = 'https://auth.aweber.com/oauth2/authorize'
token_url = 'https://auth.aweber.com/oauth2/token'

# Define the scopes you need
scopes = ['account.read', 'list.read', 'subscriber.read']



# Create an OAuth2 session with the required scopes
aweber = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=scopes)





# %%
# # Create an OAuth2 session
# aweber = OAuth2Session(client_id, redirect_uri=redirect_uri)


# %%
# Redirect user to AWeber for authorization
authorization_url, state = aweber.authorization_url(authorization_base_url)
print('Please go to this URL and authorize access:', authorization_url)


# %%
redirect_response='http://localhost:5000/oauth/callback?code=1VSBpGB78TOo2CRiT9nXuQZ56gPKpp2k&state=GTaNLztiXMMB6ST2SD0wU8h6wJSaaP'
token = aweber.fetch_token(token_url, client_secret=client_secret, authorization_response=redirect_response)
#token

# %%
import json
# File to store tokens
token_file = 'aweber_tokens.json'

# Save tokens to file
with open(token_file, 'w') as f:
    json.dump(token, f)

print("Initial token obtained and saved to file.")

# %%

# Now you can make authenticated requests
account_response = aweber.get('https://api.aweber.com/1.0/accounts')
print(account_response.json())

# %%
try:
    account_response = aweber.get('https://api.aweber.com/1.0/accounts')
    account_response.raise_for_status()  # Raise an error for bad status codes
    accounts = account_response.json()
    print("Account details fetched successfully!")
    print(accounts)
except requests.exceptions.RequestException as e:
    print("Error fetching account details:", e)

# Example: Fetch subscriber statistics for a specific list
account_id = accounts['entries'][0]['id']
list_id = 'YOUR_LIST_ID'  # Replace with your actual list ID

# %%
account_id

# %%

# Now you can make authenticated requests
account_response = aweber.get('https://api.aweber.com/1.0/accounts')
print(account_response.json())

# %%
import os
import json
import requests
from requests_oauthlib import OAuth2Session
from datetime import datetime, timedelta

# Replace these with your own client ID and secret

client_id = 'jIjODSTBXb7DtLQDLNQGx76lee0nerMT'
client_secret = 'hn9kvUApp6bQ1kTFjTWkx5Fit1JmaIHf'
redirect_uri = 'http://localhost:5000/oauth/callback'

# OAuth2 endpoints
authorization_base_url = 'https://auth.aweber.com/oauth2/authorize'
token_url = 'https://auth.aweber.com/oauth2/token'

# OAuth2 endpoints
token_url = 'https://auth.aweber.com/oauth2/token'

# File to store tokens
token_file = 'aweber_tokens.json'

def save_tokens(tokens):
    with open(token_file, 'w') as f:
        json.dump(tokens, f)

def load_tokens():
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            return json.load(f)
    return None

def refresh_tokens(refresh_token):
    extra = {'client_id': client_id, 'client_secret': client_secret}
    aweber = OAuth2Session(client_id, token={'refresh_token': refresh_token}, auto_refresh_kwargs=extra, auto_refresh_url=token_url, token_updater=save_tokens)
    tokens = aweber.refresh_token(token_url, refresh_token=refresh_token)
    save_tokens(tokens)
    return tokens

def get_aweber_session():
    tokens = load_tokens()
    
    if tokens is None:
        raise Exception("No tokens found. Please run the initial setup script first.")
    
    # Check if token has expired
    expiration_time = datetime.fromtimestamp(tokens['expires_at'])
    if datetime.now() >= expiration_time:
        tokens = refresh_tokens(tokens['refresh_token'])
    
    return OAuth2Session(client_id, token=tokens)

def fetch_campaign_data():
    aweber = get_aweber_session()
    
    # Fetch account details
    try:
        account_response = aweber.get('https://api.aweber.com/1.0/accounts')
        account_response.raise_for_status()  # Raise an error for bad status codes
        accounts = account_response.json()
        print("Account details fetched successfully!")
        print(accounts)
    except requests.exceptions.RequestException as e:
        print("Error fetching account details:", e)
        return
    
    # Fetch campaign reports for each list in the account
    account_id = accounts['entries'][0]['id']
    print(account_id)
    # try:
    #     lists_response = aweber.get(f'https://api.aweber.com/1.0/accounts/{account_id}/lists')
    #     lists_response.raise_for_status()
    #     lists = lists_response.json()
        
    #     for list_entry in lists['entries']:
    #         list_id = list_entry['id']
    #         stats_response = aweber.get(f'https://api.aweber.com/1.0/accounts/{account_id}/lists/{list_id}/stats')
    #         stats_response.raise_for_status()
    #         stats = stats_response.json()
    #         print(f"Statistics for list {list_id} fetched successfully!")
    #         print(stats)
            
    # except requests.exceptions.RequestException as e:
    #     print("Error fetching list or campaign statistics:", e)

# Fetch campaign data daily
fetch_campaign_data()


# %%
account_id

# %%



