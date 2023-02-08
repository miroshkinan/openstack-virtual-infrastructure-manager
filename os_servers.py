#     _____
#    / ____|
#   | (___   ___ _ ____   _____ _ __ ___
#    \___ \ / _ \ '__\ \ / / _ \ '__/ __|
#    ____) |  __/ |   \ V /  __/ |  \__ \
#   |_____/ \___|_|    \_/ \___|_|  |___/
#
import os
import errno
import base64

from globals import conn
from os_images import getImageByName
from os_snapshots import getSnapshotByName
from os_networks import getNetworkByName, createNetworkByName


# createServerByName(config, name) creates a server with the name "name" and the parameters from the "config" structure
def createServerByName(config, name, arguments):
    # Looking for a config of the server to be created
    for servConfig in config["servers"]:
        if servConfig["name"] != name:
            continue

        # The config has been found
        server = conn.compute.find_server(name)

        # If the server exists, skip its creation
        if server is not None:
            print('Creation of server "' + name + '" ...   SKIPPED: The server already exists.')
            return

        snapshot = None
        if "instance_snapshot" in servConfig:
            # Get the instance snapshot name for the server creation
            snapshot = getSnapshotByName(servConfig["instance_snapshot"])
            if snapshot is None:
                print('Creation of server "' + name + '" ...   FAILED: Snapshot "' +
                      servConfig["image"] + '" does not exist.')
                return

        # Get the image for the server creation
        image = getImageByName(servConfig["image"])
        if image is None:
            print('Creation of server "' + name + '" ...   FAILED: Image "' +
                  servConfig["image"] + '" does not exist.')
            return

        # Get the flavor for the server creation
        flavor = conn.compute.find_flavor(servConfig["flavor"])
        if flavor is None:
            print('Creation of server "' + name + '" ...   FAILED: Flavor "' +
                  servConfig["flavor"] + '" does not exist.')
            return

        # Try to create a directory for generated ssh keys
        # Default path is user's "~/.ssh" directory
        ssh_dir = os.path.expanduser("~") + os.path.sep + ".ssh"
        if arguments.ssh_directory is not None:
            ssh_dir = arguments.ssh_directory

        try:
            os.mkdir(ssh_dir)
        # Nothing bad happened. The directory exists.
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e

        # Default sshKeyName = serverName
        sshKeyName = name
        # If config contains new ssh key name, redefine the value
        if "keypair" in servConfig.keys():
            sshKeyName = servConfig["keypair"]

        privateKeyPath = ssh_dir + os.path.sep + sshKeyName
        publicKeyPath = privateKeyPath + ".pub"

        # Attempt to get existing ssh key
        keypair = conn.compute.find_keypair(sshKeyName)

        # The keypair <keyPairName> is absent in Openstack
        if keypair is None:

            # If the private key <keyPairName> is present in local user .ssh folder
            if os.path.isfile(privateKeyPath):

                # The public key <keyPairName> is absent in local user .ssh folder
                if not os.path.isfile(publicKeyPath):
                    # Generate public ssh key from the private one
                    os.system('ssh-keygen -y -f ' + privateKeyPath + ' > ' + publicKeyPath)
                    os.chmod(publicKeyPath, 0o444)

                # Upload  public key to Openstack
                with open(os.path.expanduser(publicKeyPath)) as f:
                    public_key = f.read()
                    keypair = conn.compute.create_keypair(name=sshKeyName, public_key=public_key)
                    if keypair is None:
                        print('Creation of server "' + name + '" ...   FAILED: Error during upload public ssh key "' +
                              sshKeyName + '" to Openstack')
                        return

            # If the keypair <keyPairName> is absent in local user .ssh folder
            else:

                # Generate new ssh keypair
                keypair = conn.compute.create_keypair(name=sshKeyName)

                # Save the private key to local .ssh folder
                with open(privateKeyPath, 'w') as f:
                    f.write("%s" % keypair.private_key)
                os.chmod(privateKeyPath, 0o400)

                # If error
                if keypair is None:
                    print('Creation of server "' + name + '" ...   FAILED: Error during ssh keypair "' + sshKeyName +
                          '" creation for the server "' + name + '".')
                    return

        # Prepare the list networks for connecting the server
        networks = []
        for netw in servConfig["networks"]:
            # If the network does not exist, create it
            network = getNetworkByName(netw["name"])
            if network is None:
                network = createNetworkByName(config, netw["name"])

            # If config contains desired IPv4 addresses, append them to networks config
            if "ipv4" in netw.keys():
                networks.append({"uuid": network.id, "fixed_ip": netw["ipv4"]})
            else:
                networks.append({"uuid": network.id})

        # Load post-installation init script from file
        user_data = ""
        if "init-script" in servConfig:
            # If the script file doesn't exists
            if not os.path.isfile(servConfig["init-script"]):
                print('Creation of server "' + name + '" ...   FAILED: Init script file "' +
                      servConfig["init-script"] + '" does not exist.')
                return

            with open(servConfig["init-script"], "r") as initfile:
                initscript = initfile.read()
                # OpenStack requires special encoding for the user_data argument
                user_data = base64.b64encode(initscript.encode('ascii')).decode('ascii')

        if snapshot is not None:
            image = snapshot

        # Create server
        server = conn.compute.create_server(
            name=name,
            image_id=image.id,
            flavor_id=flavor.id,
            networks=networks,
            user_data=user_data,
            key_name=keypair["name"])

        # It takes some time
        conn.compute.wait_for_server(server)

        # If the server is absent, an error occured
        if server is None:
            print('Creation of server "' + name + '" ...   FAILED: Error during the server creation.')
            return

        print('Creation of server "' + name + '" ...   OK')
        return

    # Unknown server name
    print('Creation of server "' + name + '" ...   FAILED: There is no entry for the server "' + name +
          '" in the configuration file.')
    return


# createAllServers(config) creates servers with the parameters from the "config" structure.
def createAllServers(config, arguments):
    if "servers" in config.keys():
        for servConfig in config["servers"]:
            createServerByName(config, servConfig["name"], arguments)
    else:
        print('No "servers" section has been found in the configuration file.')


# deleteServerByName(name) deletes the server with a special name if it exists
def deleteServerByName(name):
    serv = conn.compute.find_server(name)
    if serv is not None:
        conn.compute.delete_server(serv)
        conn.compute.wait_for_delete(serv, wait=300)
        print('Deleting of the server "' + name + '" ...   OK')
    else:
        print('Deleting of the server "' + name + '" ...   SKIPPED: The server does not exist.')
    return


# deleteAllServers(config) deletes all servers with the parameters from the "config" structure.
def deleteAllServers(config):
    if "servers" in config.keys():
        for servConfig in config["servers"]:
            deleteServerByName(servConfig["name"])
