#    _   _      _                      _
#   | \ | |    | |                    | |
#   |  \| | ___| |___      _____  _ __| | _____
#   | . ` |/ _ \ __\ \ /\ / / _ \| '__| |/ / __|
#   | |\  |  __/ |_ \ V  V / (_) | |  |   <\__ \
#   |_| \_|\___|\__| \_/\_/ \___/|_|  |_|\_\___/
#
#
from globals import conn


# isNetworkExist(networkName) returns True if a network with the name networkName exists.
def isNetworkExist(networkName):
    return conn.network.find_network(networkName) is not None


# getNetworkByName(networkName) returns network object of the network with the name networkName.
# if the network does not exist, the function returns None
def getNetworkByName(networkName):
    return conn.network.find_network(networkName)


# getNetworkByID(networkID) returns network object of the network with the desired ID.
# if the network does not exist, the function returns None
def getNetworkByID(networkID):
    for n in conn.network.networks():
        if n.id == networkID:
            return n
    return None


# getNetworkBySubnetID(networkID) returns network object of the network, that contains the subnet with id subnetID.
# if the network does not exist, the function returns None
def getNetworkBySubnetID(subnetID):
    for sn in conn.network.subnets():
        if sn["id"] == subnetID:
            for n in conn.network.networks():
                if n["id"] == sn["network_id"]:
                    return n
    return None


# createAllNetworks(config) creates all networks and subnets with the parameters from the "config" structure.
def createNetworkByName(config, name):
    # Look for an appropriate config entry in "config" dictionary
    for netConfig in config["networks"]:
        if netConfig["name"] != name:
            continue

        # The network config has been found
        network = conn.network.find_network(netConfig["name"])
        # Check if the network already exists
        if network is not None:
            print('Creation of the network "' + netConfig['name'] + '" ...   SKIPPED: The network already exists.')
            return network
        # Creation of a new network without subnet
        network = conn.network.create_network(name=netConfig["name"])
        if network is None:
            print('Creation of the network "' + netConfig['name'] + '" ...   FAILED: Error during the network creation.')
            return None

        # If the subnet exists, report an error and exit
        subnet = conn.network.find_subnet(netConfig["name"])
        if subnet is not None:
            print('Creation of the network "' + netConfig['name'] + '" ...   FAILED: '
                  'Subnet with the name "' + netConfig["name"] + '" exists')
            return None

        subnet_args = {"name": netConfig["name"],
                       "network_id": network.id,
                       "ip_version": "4",
                       "enable_dhcp": False,
                       "disable_gateway_ip": True,
                       "gateway_ip": None,
                       "cidr": netConfig["cidr"]}

        # If DNS addresses on hostnames are in the config file, provide the information to the subnet creation process
        if "parameters" in config.keys():
            if "dns_nameservers" in config["parameters"]:
                subnet_args["dns_nameservers"] = config["parameters"]["dns_nameservers"]

        try:
            subnet = conn.network.create_subnet(**subnet_args)
        except Exception:
            print('Creation of the network "' + netConfig['name'] + '" ...   FAILED: '
                  'Please, check parameters for a subnet creation')
            return None

        # For some reason the subnet might not be created and no exceptions occurred
        if subnet is None:
            print('Creation of the network "' + netConfig['name'] + '" ...   FAILED: Error during subnet creation.')
            return None
        print('Creation of the network "' + netConfig['name'] + '" ...   OK')
        return network


# createAllNetworks(config) creates all networks and subnets with the parameters from the "config" structure.
def createAllNetworks(config):
    for netConfig in config["networks"]:
        createNetworkByName(config, netConfig["name"])


# deleteNetworkByName(name) deletes the network with a special name if it exists
def deleteNetworkByName(name):
    # If the network exists, try to delete it
    netw = conn.network.find_network(name)
    if netw is not None:
        try:
            conn.network.delete_network(netw)
        except Exception:
            print('Deleting of the network "' + name + '" with its subnet(s) ...   '
                  'FAILED: Some hosts might be still connected to the network.')
        print('Deleting of the network "' + name + '" with its subnet(s) ...   OK')
    # The network doesn't exist yet, nothing to delete
    else:
        print('Deleting of the network "' + name + '" with its subnet(s) ...   SKIPPED: The network does not exist.')


# deleteServers(config) deletes servers with the parameters from the "config" structure.
def deleteAllNetworks(config):
    if "networks" in config.keys():
        for netwConfig in config["networks"]:
            deleteNetworkByName(netwConfig["name"])
