import meraki
import os
import time

RETRIES = 5  # max number of retries per call for 429 rate limit status code

org_id = os.environ.get('MERAKI_ORG_ID')

def get_tagged_networks(dashboard, orgid, tag):
    print(f'getting networks for org ID {orgid}')
    try:
        networks = meraki.Organizations.getOrganizationNetworks(dashboard, organizationId=orgid, tags=tag)
        return networks
    except Exception as e:
        print(f"some error: {e}")
        return False

# Function to enable alerts for gateway APs
def change_ap_gw_alerts(dashboard, network_id, newstate):
    if newstate == "disable":
        alertstatus = [{"type": "gatewayDown","enabled": False}]
    elif newstate == "enable":
        alertstatus = [{"type": "gatewayDown", "enabled": True}]
    else:
        return
    try:
        meraki.Networks.updateNetworkAlertsSettings(dashboard, network_id, alerts=alertstatus)
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

    dashboard = meraki.DashboardAPI(print_console=False, maximum_retries=RETRIES)
    # define vars
    get_tasks = []
    alert_results = []
    netlist = {}

    # Get all networks that are tagged with specified tag
    networks = get_tagged_networks(dashboard, org_id, tag)
    for net in networks:
        if change_ap_gw_alerts(dashboard, net['id'], newstate):
            print(f"Alerts {newstate}d on {net['name']}")

    endTime = time.time_ns()
    print(f'Total time to run: {(endTime - startTime)/1000000} ms')

# Run the main function
if __name__ == "__main__":
    main()