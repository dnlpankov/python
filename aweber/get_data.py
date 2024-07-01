# %%
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from datetime import datetime
import pytz

import os
import json
import requests
from requests_oauthlib import OAuth2Session
from datetime import datetime
from urllib.parse import urlencode
import pandas as pd
import re
import time

# %%


# %%
creds_path="./"
test=0
#test=1
if test==1:
    limit_per_request=1
    sleep_time_for_one_campaign=0
    creds_path="./"
else:
    limit_per_request=30
    sleep_time_for_one_campaign=0.6
    creds_path="/home/deploy/python/aweber/"

# %%


# %%

# Path to Aweber credentials file
aweber_creds = creds_path+ 'aweber_credentials.json'

# Load the credentials
with open(aweber_creds, 'r') as file:
    credentials = json.load(file)


# Assign creds to variables
client_id = credentials['client_id']
client_secret = credentials['client_secret']
redirect_uri = 'http://localhost:5000/oauth/callback'

# OAuth2 endpoints
authorization_base_url = 'https://auth.aweber.com/oauth2/authorize'
token_url = 'https://auth.aweber.com/oauth2/token'

# Scopes
scopes = ['email.read', 'account.read', 'list.read', 'subscriber.read']

# File to store tokens
token_file = creds_path+'aweber_tokens.json'

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
    
    return OAuth2Session(client_id, token=tokens, scope=scopes), tokens['access_token']

def get_campaigns(list_id, account_id, campaign_type, start=0, limit=1000):
    aweber, access_token = get_aweber_session()
    try:
        params = {'ws.op': 'find', 'campaign_type': campaign_type, 'ws.start': start, 'ws.size': limit}
        campaigns_url = f'https://api.aweber.com/1.0/accounts/{account_id}/lists/{list_id}/campaigns?{urlencode(params)}'
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AWeber-Python-code-sample/1.0',
            'Authorization': f'Bearer {access_token}'
        }
        print(f"Fetching campaigns with URL: {campaigns_url}")
        response = aweber.get(campaigns_url, headers=headers)
        response.raise_for_status()
        campaigns = response.json()
        print("Campaigns fetched successfully!")
        return campaigns
    except requests.exceptions.RequestException as e:
        print(f"Error fetching campaigns for list {list_id}:", e)
        return {'entries': []}
# Function to convert iso format time to CET
def convert_to_cet(time_str):
    #print(time_str)
    time_str_cet=None
    if time_str is not None:
        input_time = datetime.fromisoformat(time_str)
        cet_tz = pytz.timezone("Europe/Berlin")
        cet_time = input_time.astimezone(cet_tz)
        time_str_cet=cet_time.strftime('%Y-%m-%d %H:%M:%S')
    return time_str_cet

def get_all_lists_for_account(account_id):
    # response = requests.get(f'https://api.aweber.com/1.0/accounts/{account_id}/lists', headers=headers)
    # lists = response.json()
    try:
        aweber, access_token = get_aweber_session()
        #print(access_token)
        lists_url = f'https://api.aweber.com/1.0/accounts/{account_id}/lists'
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AWeber-Python-code-sample/1.0',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(lists_url, headers=headers)
        response.raise_for_status()
        campaign_details = response.json()


        print(f"Details for campaign {account_id} fetched successfully!")
        lists=[]
        for entry in campaign_details['entries']:
            lists+=[entry['id']]

        return lists
    except requests.exceptions.RequestException as e:
        print(f"Error fetching lists for account {account_id}:", e)
        return {}

def get_campaign_details(account_id, list_id, campaign_id, campaign_type, access_token):
    try:
        
        campaign_details_url = f'https://api.aweber.com/1.0/accounts/{account_id}/lists/{list_id}/campaigns/{campaign_type}{campaign_id}'
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AWeber-Python-code-sample/1.0',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(campaign_details_url, headers=headers)
        response.raise_for_status()
        campaign_details = response.json()
        campaign_details['sent_at_cet'] = convert_to_cet(campaign_details['sent_at'])
        campaign_details['list_id'] = list_id
        print(f"Details for campaign {campaign_id} fetched successfully!")
        time.sleep(sleep_time_for_one_campaign)
        return campaign_details
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for campaign {campaign_id}:", e)
        return {}



def fetch_all_campaigns_of_list_and_type(account_id, list_id, campaign_type, data_nature):
    aweber, access_token = get_aweber_session()
    

    campaigns_response = get_campaigns(list_id, account_id, campaign_type, limit=limit_per_request)
    campaigns = campaigns_response['entries']
    all_campaigns_of_list_and_type_details = []
    for campaign in campaigns:
        campaign_id = campaign['id']
        print(f"campaign is {campaign_id} and list is {list_id}")
        if data_nature=='campaigns_stats':
            campaign_details = get_campaign_details(account_id, list_id, campaign_id, campaign_type, access_token)
        elif data_nature=='campaigns_characteristics':
            campaign_details = get_campaign_characteristics(account_id, list_id, campaign_id, campaign_type, access_token)
        #print(type(campaign_details['sent_at_cet']))
        all_campaigns_of_list_and_type_details.append(campaign_details)
    return all_campaigns_of_list_and_type_details

def fetch_all_campaigns(account_id, campaign_type_set, data_nature):
    all_campaigns_details = []
    lists=get_all_lists_for_account(account_id)
    #print(entries)
    for list_id in lists:
        for campaign_type in campaign_type_set:
            all_campaigns_details = all_campaigns_details+fetch_all_campaigns_of_list_and_type(account_id, list_id, campaign_type, data_nature)
    return all_campaigns_details, lists







# %%
# Example usage:
account_id = 2007954  # Replace with actual account ID
list_id = 6405738  # Replace with actual list ID
campaign_type = 'b'  # Replace with actual campaign type (e.g., 'broadcast', 'followup', etc.)

all_campaigns_details_final, lists = fetch_all_campaigns(account_id, campaign_type_set=['b', 'f'], data_nature='campaigns_stats')

# Print or process all campaign details
#print(json.dumps(all_campaigns_details_final, indent=2))

# %%



# %%


# %% [markdown]
# ## Uploading Data to postgres

# %%
# with open(sql_creds, 'r') as file:
#     sql_credentials = json.load(file)

# sql_credentials['string']

# %%
from sqlalchemy import create_engine
#import pandas as pd

sql_creds = creds_path+'postgres_credentials.json'

# Load the credentials
with open(sql_creds, 'r') as file:
    sql_credentials = json.load(file)

def load_data_to_db(json_vector=all_campaigns_details_final, schema='danila', table='stg_aweber__campaign_data'):
    engine = create_engine(sql_credentials['string'])
    df=pd.json_normalize(json_vector)
    # Define CET timezone
    cet = pytz.timezone('Europe/Paris')
        
    # Add current timestamp in CET timezone
    df['updated_at_cet'] = datetime.now(cet)

    # Load data into the specified schema in the database
    df.to_sql(table, engine, if_exists='replace', index=False, schema='danila')

if __name__ == "__main__":
    load_data_to_db()

# %% [markdown]
# # Getting campaign country and brand

# %%
# Function to extract the specific part from the body_text
def extract_cosmic_slot(body_text):
    print(body_text)
    pattern = r'-email-([^-]*)-([^-]*)-([^-]*)-([^-]*)-([a-zA-Z_]*)'
    match = re.search(pattern, body_text)
    #string = '-email-nl-xxxxxxxxxxxxxxxx-justbit-'
    if match:
        return match.group(1), match.group(3), (match.group(5)=='trickyspins_email_welcome')
    return None, None, None

def get_campaign_characteristics(account_id, list_id, campaign_id, campaign_type, access_token):
    try:
        aweber, access_token = get_aweber_session()
        campaign_details_url = f'https://api.aweber.com/1.0/accounts/{account_id}/lists/{list_id}/broadcasts/{campaign_id}'
        
        headers = {
            'Accept': 'application/json',
            'User-Agent': 'AWeber-Python-code-sample/1.0',
            'Authorization': f'Bearer {access_token}'
        }
        response = requests.get(campaign_details_url, headers=headers)
        response.raise_for_status()
        json_data = response.json()
        country_code, brand_name, is_welcome_campaign=extract_cosmic_slot(json_data['body_text'])
        extracted_data = {
            'brand_name': brand_name,
            'country_code': country_code,
            'is_welcome_campaign': is_welcome_campaign,
            'sent_at': json_data['sent_at'],
            'sent_at_cet': convert_to_cet(json_data['sent_at']), # Convert to CET timezone
            'broadcast_id': json_data['broadcast_id'],
            'campaign_type': campaign_type,
            'campaign_id': campaign_id,
            'account_id': account_id,
            'list_id': list_id,
            'subject': json_data['subject'],
            'num_complaints': json_data['stats']['num_complaints'],
            'num_emailed': json_data['stats']['num_emailed'],
            'num_undeliv': json_data['stats']['num_undeliv'],
            'unique_clicks': json_data['stats']['unique_clicks'],
            'unique_opens': json_data['stats']['unique_opens']
        }
        # campaign_details['sent_at_cet'] = convert_to_cet(campaign_details['sent_at'])
        # campaign_details['list_id'] = list_id
        print(f"Details for campaign {campaign_id} fetched successfully!")
        time.sleep(sleep_time_for_one_campaign)
        return extracted_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for campaign {campaign_id}:", e)
        return {}

campaign_id= 57913875 # 57961057
account_id = 2007954  # Replace with actual account ID
list_id = 6405738  # Replace with actual list ID
#aweber, access_token = get_aweber_session()
campaign_characteristics, lists = fetch_all_campaigns(account_id, campaign_type_set='b', data_nature='campaigns_characteristics')


string="email-202301010000-undefined-undefined-0-email-de-xxxxxxxxxxxxxxxx-cobra-undefined-trickyspins_email"
#extract_cosmic_slot(string)
#print(campaign_characteristics)

# %%


# string="202301010000-undefined-undefined-0-email-de-xxxxxxxxxxxxxxxx-cobra-undefined-trickyspins_email_welcome"
# extract_cosmic_slot(string)

# %%
#if __name__ == "__main__":
load_data_to_db(json_vector=campaign_characteristics, schema='danila', table='stg_aweber__campaign_characteristics')

# %%


# %%



