import requests
import os
import re
import time

# Define your Meraki API key and organization ID
api_key = "Bearer " + os.environ.get('MERAKI_DASHBOARD_API_KEY')
org_id = os.environ.get('MERAKI_ORG_ID')

# Define the URL for Meraki API endpoints
base_url = 'https://api.meraki.com/api/v1'

# Set up headers for API requests
headers = {
    'Authorization': api_key,
    'Content-Type': 'application/json'
}

def get_tagged_networks(orgid, tag):
    print(f'getting networks for org ID {orgid}')
    taglist = { "tags": [ tag ] }
    try:
        url = f'{base_url}/organizations/{org_id}/networks'
        response = requests.get(url, headers=headers, json=taglist).json()
        return response
    except Exception as e:
        print(f"some error: {e}")
        return False

# Function to enable alerts for gateway APs
def change_ap_gw_alerts(network_id, newstate):
    if newstate == "disable":
        alertstatus = [{"type": "gatewayDown","enabled": False}]
    elif newstate == "enable":
        alertstatus = [{"type": "gatewayDown", "enabled": True}]
    else:
        return
    alertlist = {"alerts":alertstatus}
    try:
        url = f'{base_url}/networks/{network_id}/alerts/settings'
        response = requests.put(url, headers=headers, json=alertlist).json()
        return network_id
    except Exception as e:
        print(f'The following error has occurred: {e}')
        return


# Main function to run the script
def main():
    # Prompt the user for the API key, organization ID, and tag to filter on
    tag = input("Enter the tag to filter on (e.g., 'NO_ALERTS'): ")
    newstate = ""
    while newstate not in ["enable", "disable"]:
        newstate = input("Do you want to enable or disable alerts for these networks? [enable | disable] ")

    startTime = time.time_ns()

    # Get all networks that are tagged with specified tag
    networks = get_tagged_networks(org_id, tag)
    for net in networks:
        if change_ap_gw_alerts(net['id'], newstate):
            print(f"Alerts {newstate}d on {net['name']}")

    endTime = time.time_ns()
    print(f'Total time to run: {(endTime - startTime)/1000000} ms')

# Run the main function
if __name__ == "__main__":
    main()