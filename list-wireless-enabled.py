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
def get_organization_wireless_networks(headers):
    url = f'{base_url}/organizations/{org_id}/networks'
    response = requests.get(url, headers=headers).json()
    wireless = []
    for network in response:
        if 'wireless' in network['productTypes']:
            wireless.append(network)
    return wireless


# Function to get the hub name for tag purposes
def get_ssids(headers, networkId):
    url = f'{base_url}/networks/{networkId}/wireless/ssids'
    response = requests.get(url, headers=headers).json()
    return response


# Main function to iterate through networks and check wireless settings
def main():
    networks = get_organization_wireless_networks(headers)

    for network in networks:
        network_id = network['id']

        # Fetch wireless settings
        wireless_settings = get_ssids(headers, network_id)

        # Check if ssid is enabled
        for ssid in wireless_settings:
            if ssid['enabled'] == True:
                print(f"SSID {ssid['name']} on network {network['name']} (network ID: {network_id}) is enabled")


if __name__ == '__main__':
    main()
