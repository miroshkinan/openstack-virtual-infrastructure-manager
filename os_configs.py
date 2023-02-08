#     _____             __ _
#    / ____|           / _(_)
#   | |     ___  _ __ | |_ _  __ _ ___
#   | |    / _ \| '_ \|  _| |/ _` / __|
#   | |___| (_) | | | | | | | (_| \__ \
#    \_____\___/|_| |_|_| |_|\__, |___/
#                             __/ |
#                            |___/

import os
import re

from os_networks import getNetworkBySubnetID, getNetworkByID
from globals import conn


# printSSHConfig(config, filename, path, ssh_dir) makes a file of ssh syntax with the existing hosts parameters
def printSSHConfig(config, arguments):
    ssh_dir = os.path.expanduser("~") + os.path.sep + ".ssh"
    if arguments.ssh_directory is not None:
        ssh_dir = arguments.ssh_directory

    # Group hosts entries by the network name
    hosts = sorted(config, key=lambda i: i['network'])

    # Regular expression pattern to separate IPv4 and IPv6 addresses
    pattern = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    curr_netw = ""
    with open(os.path.expanduser(".") + os.path.sep + "config", "w") as f:
        for host in hosts:
            # If new network, make a subtitle in a comment
            if curr_netw != host["network"]:
                curr_netw = host["network"]
                f.write('\n# SSH configuration for network "' + curr_netw + '"\n')

            # The hosts have the next hostname pattern: <server>_<network>_[ipv4|ipv6]
            if pattern.match(host["ip"]):
                f.write("Host " + host["name"] + "_v4\n")
            else:
                f.write("Host " + host["name"] + "_v6\n")

            # Write hosts parameters using ssh config syntax
            f.write("    Hostname " + host["ip"] + "\n")
            f.write("    User " + host["username"] + "\n")
            f.write("    IdentityFile " + ssh_dir + os.path.sep + host["keypair"] + "\n")
            f.write("    StrictHostKeyChecking no\n\n")

    # Final print message
    print('ssh config is generated and saved to "' + os.path.expanduser(".") + os.path.sep + 'config"')
    print('To see generated ssh config run')
    print('    cat ' + os.path.expanduser(".") + os.path.sep + 'config')
    print('To append generated config to ssh config file run')
    print('    cat ' + os.path.expanduser(".") + os.path.sep + 'config' + ' >> ' + ssh_dir + os.path.sep + 'config')
    return


# printAnsibleInventory(config, filename, path, ssh_dir) makes a file of ssh syntax with the existing hosts parameters
def printAnsibleInventory(config, arguments):
    ssh_dir = os.path.expanduser("~") + os.path.sep + ".ssh"
    if arguments.ssh_directory is not None:
        ssh_dir = arguments.ssh_directory

    # Group hosts entries by the network name
    hosts = sorted(config, key=lambda i: (i['network'], i["ipversion"]))

    # Regular expression pattern to separate IPv4 and IPv6 addresses
    pattern = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

    with open(os.path.expanduser(".") + os.path.sep + "inventory.yml", "w") as f:
        # root element "All" with its "children" subelement
        f.write("all:\n")
        f.write("  children:\n")

        curr_netw = ""
        curr_ipversion = 0
        for host in hosts:
            # If a new network or a new IP version, make a new ansible template subtree
            if curr_netw != host["network"] or curr_ipversion != host["ipversion"]:
                curr_netw = host["network"]
                curr_ipversion = host["ipversion"]

                f.write('\n# Network "' + curr_netw + '", IPv' + str(curr_ipversion) + "\n")
                f.write("    " + curr_netw + "_ipv" + str(curr_ipversion) + ":\n")
                f.write("      hosts:\n")

            # The hosts have the next hostname pattern: <server>_<network>_[ipv4|ipv6]
            if pattern.match(host["ip"]):
                f.write("        " + host["name"] + "_v4:\n")
            else:
                f.write("        " + host["name"] + "_v6:\n")

            # Write hosts parameters using ansible inventory syntax
            f.write('          ansible_host: ' + host["ip"] + "\n")
            f.write('          ansible_user: ' + host["username"] + "\n")
            f.write('          ansible_ssh_private_key_file: ' + ssh_dir + os.path.sep + host["keypair"] + "\n")
            f.write('          ansible_ssh_common_args: \'-o StrictHostKeyChecking=no\'\n')

    # Final print message
    print('Ansible inventory file is generated and saved to "' + os.path.expanduser(".") + os.path.sep + 'inventory.yml"')
    print('To see generated Ansible inventory file run')
    print('    cat ' + os.path.expanduser(".") + os.path.sep + 'inventory.yml')
    return


# generateSSHConfig(config) prepares the list of running hosts with their parameters for ssh config and
# ansible inventory template generation
def generateSSHConfig(config):
    # Empty list of running hosts
    conf = []
    for servConfig in config["servers"]:
        server = conn.compute.find_server(servConfig["name"])

        # Ignore servers, that are not running
        if server is None:
            print('Server "' + servConfig["name"] + '" is not running.')
            continue

        # Regular expression pattern to separate IPv4 and IPv6 addresses
        pattern = re.compile("^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")

        # Looking for ports of current server
        for port in conn.network.ports():
            if port["device_id"] == server["id"]:
                # Every port IP address has to have separate "host" entry
                for fi in port["fixed_ips"]:
                    host = {"name": servConfig["name"] + "_" + getNetworkBySubnetID(fi["subnet_id"])["name"],
                            "network": getNetworkByID(port["network_id"])["name"],
                            "ip": fi["ip_address"],
                            "keypair": servConfig["keypair"]}

                    # Get the username for the server
                    try:
                        username = config["parameters"]["users"][servConfig["image"]]
                    except Exception:
                        username = None

                    # Include only initialized value
                    if username is not None:
                        host["username"] = username

                    # IP version
                    if pattern.match(host["ip"]):
                        host["ipversion"] = 4
                    else:
                        host["ipversion"] = 6

                    # Save gathered information
                    conf.append(host)
    return conf


# generateConfig(config, arguments) prepares hosts information and generates ssh config and/or
# ansible inventory file template
def generateConfig(config, arguments):
    # If any config generation is required
    if arguments.config_type is not None:
        # Make special structure with the information about running virtual hosts
        hostsConfig = generateSSHConfig(config)
        # Generate both configs
        if "all" in arguments.config_type:
            printSSHConfig(hostsConfig, arguments)
            printAnsibleInventory(hostsConfig, arguments)
        else:
            # Only one of them
            if "ssh" in arguments.config_type:
                printSSHConfig(hostsConfig, arguments)
            if "ansible" in arguments.config_type:
                printAnsibleInventory(hostsConfig, arguments)
