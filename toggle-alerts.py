import asyncio
import meraki.aio
import os
import time

RETRIES = 5  # max number of retries per call for 429 rate limit status code

org_id = os.environ.get('MERAKI_ORG_ID')


async def get_tagged_networks(aiomeraki: meraki.aio.AsyncDashboardAPI, orgid, tag):
    print(f'getting networks for org ID {orgid}')
    try:
        networks = await aiomeraki.organizations.getOrganizationNetworks(organizationId=orgid, tags=tag)
        return networks
    except meraki.AsyncAPIError as e:
        print(f"Meraki API error: {e}")
        return False
    except Exception as e:
        print(f"some other error: {e}")
        return False

# Function to enable alerts for gateway APs
async def change_ap_gw_alerts(aiomeraki: meraki.aio.AsyncDashboardAPI, network_id, newstate):
    if newstate == "disable":
        alertstatus = [{"type": "gatewayDown","enabled": False}]
    elif newstate == "enable":
        alertstatus = [{"type": "gatewayDown", "enabled": True}]
    else:
        return
    try:
        await aiomeraki.networks.updateNetworkAlertsSettings(network_id,alerts=alertstatus)
    except meraki.AsyncAPIError as e:
        print(f'Meraki API error: {e}')
        return
    except Exception as e:
        print(f'The following error has occurred: {e}')
        return
    return network_id

# Main function to run the script
async def main():
    # Prompt the user for the API key, organization ID, and tag to filter on
    tag = input("Enter the tag to filter on (e.g., 'NO_ALERTS'): ")
    newstate = ""
    while newstate not in ["enable", "disable"]:
        newstate = input("Do you want to enable or disable alerts for these networks? [enable | disable] ")

    startTime = time.time_ns()

    async with meraki.aio.AsyncDashboardAPI(
        log_file_prefix=__file__[:-3],
        print_console=False,
        maximum_retries=RETRIES
    ) as aiomeraki:
        # define vars
        get_tasks = []
        alert_results = []
        netlist = {}

        # Get all networks that are tagged with specified tag
        networks = await get_tagged_networks(aiomeraki, org_id, tag)
        for net in networks:
            netlist[net['id']] = net['name']
            # Prepare async task to swap the first and second hubs
            get_tasks.append(change_ap_gw_alerts(aiomeraki, net['id'], newstate))

        for task in asyncio.as_completed(get_tasks):
            alert = await task
            alert_results.append(alert)
        for result in alert_results:
            if(result):
                print(f'Alerts {newstate}d on {netlist[result]}!')

    endTime = time.time_ns()
    print(f'Total time to run: {(endTime - startTime)/1000000} ms')

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())