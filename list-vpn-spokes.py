import requests
import os

# Define your Meraki API key and organization ID
api_key = 'Bearer ' + os.environ.get('MERAKI_DASHBOARD_API_KEY')
org_id = os.environ.get('MERAKI_ORG_ID')

# Define the URL for Meraki API endpoints
base_url = 'https://api.meraki.com/api/v1'

# Set up headers for API requests
headers = {
    'Authorization': api_key,
    'Content-Type': 'application/json'
}

# Function to fetch a list of networks in the organization
def get_organization_sec_networks(headers):
    url = f'{base_url}/organizations/{org_id}/networks'
    response = requests.get(url, headers=headers).json()
    appliances = []
    for network in response:
        if 'appliance' in network['productTypes']:
            appliances.append(network)
    return appliances

# Function to get the hub name for tag purposes
def get_hub_name(headers,hubId):
    url = f'{base_url}/networks/{hubId}'
    response = requests.get(url, headers=headers).json()
    return response['name'].replace(' ','_')

# Main function to iterate through networks and check site-to-site VPN settings
def main():
    networks = get_organization_sec_networks(headers)
    
    for network in networks:
        network_id = network['id']
        
        # Fetch site-to-site VPN settings
        url = f'{base_url}/networks/{network_id}/appliance/vpn/siteToSiteVpn'
        response = requests.get(url, headers=headers)
        vpn_settings = response.json()
        
        # Check if the first hub has the specified hubId
        if vpn_settings['mode'] == "spoke": 
            hubname = get_hub_name(headers,vpn_settings['hubs'][0]['hubId'])
            print(f"Spoke {network['name']} (ID: {network_id}) has its primary hub set to: {hubname}")

if __name__ == '__main__':
    main()

