import asyncio
import itertools
import os
import meraki.aio
import time

RETRIES = 5  # max number of retries per call for 429 rate limit status code

# Define your Meraki API key and organization ID
org_id = os.environ.get('MERAKI_ORG_ID')

#
# Make sure to define your API key in environment variable 'MERAKI_DASHBOARD_API_KEY'
#

# Function to fetch APs and status across org
async def get_wireless_status(aiomeraki: meraki.aio.AsyncDashboardAPI, orgid):
    try:
        aps = await aiomeraki.organizations.getOrganizationDevicesAvailabilities(organizationId=orgid,productTypes=['wireless'])
    except meraki.AsyncAPIError as e:
        print(f"Meraki API error: {e}")
        return str(orgid)
    except Exception as e:
        print(f"some other error: {e}")
        return str(orgid)

    # filter for just wireless networks
    return aps

# Function to fetch a list of networks in the organization
async def get_networks(aiomeraki: meraki.aio.AsyncDashboardAPI, orgid):
    try:
        networks = await aiomeraki.organizations.getOrganizationNetworks(organizationId=orgid)
    except meraki.AsyncAPIError as e:
        print(f"Meraki API error: {e}")
        return str(orgid)
    except Exception as e:
        print(f"some other error: {e}")
        return str(orgid)

    aps = []
    for network in networks:
        if 'wireless' in network['productTypes']:
            aps.append(network)
    return aps


async def get_mesh(aiomeraki: meraki.aio.AsyncDashboardAPI, netid):
    try:
        meshaps = await aiomeraki.wireless.getNetworkWirelessMeshStatuses(networkId=netid)
    except meraki.AsyncAPIError as e:
        # Aborting silently if error, as expecting 4xx series errors if no mesh APs found
        return None
    except Exception as e:
        # Aborting silently if issue.
        return None
    return meshaps

# Main function to iterate through networks
async def main():
    # track runtime
    startTime = time.time_ns()

    async with meraki.aio.AsyncDashboardAPI(
        log_file_prefix=__file__[:-3],
        print_console=False,
        maximum_retries=RETRIES
    ) as aiomeraki:
        # define vars
        get_tasks = []
        netNames = {}
        csvout = ""
        apserial = {}
        meshes = []


        networks = await get_networks(aiomeraki, org_id)
        for net in networks:
            # save names of all networks for future reference
            netNames[net['id']] = net['name']
            get_tasks.append(get_mesh(aiomeraki, net['id']))

        # Gather results of mesh AP searching
        for task in asyncio.as_completed(get_tasks):
            mesh = await task
            meshes.append(mesh)

        # remove None entries from iterative functions
        meshes = list(itertools.filterfalse(lambda item: not item, meshes))


        aps = await get_wireless_status(aiomeraki, org_id)
        # prep CSV header row
        csvout += (f'Network Name,AP Name,AP MAC,Status\n')
        for ap in aps:
            apserial[ap['serial']] = ap
            if ap['status'] != "online":
                csvout += (f'"{netNames[ap['network']['id']]}","{ap['name']}","{ap['mac']}","{ap['status']}"\n')

        for meshNet in meshes:
            for meshAp in meshNet:
                csvout += (f'"{netNames[apserial[meshAp['serial']]['network']['id']]}","{apserial[meshAp['serial']]['name']}","{apserial[meshAp['serial']]['mac']}","repeater"\n')
        print(csvout)
        with open("aps.csv","w") as apfile:
            apfile.write(csvout)

    endTime = time.time_ns()
    print(f'Total time to run: {(endTime - startTime)/1000000} ms')

if __name__ == '__main__':
    asyncio.run(main())