#!/usr/bin/env python
import os
import yaml
import argparse

from os_configs import generateConfig
from os_servers import deleteAllServers, deleteServerByName, createAllServers, createServerByName
from os_networks import deleteAllNetworks, deleteNetworkByName, createAllNetworks, createNetworkByName


def loadYamlConfig(fileName):
    if not os.path.exists(fileName):
        print('File ' + fileName + ' does not exist. Plese, use the "--config" argument to provide path to '
                                   'existing configuration file.')
        return None
    with open(fileName) as f:
        config = yaml.full_load(f)
        return config


def manageInfrastructure(config, arguments):
    objectsToDelete = None
    if arguments.object_d is not None:
        objectsToDelete = arguments.object_d
    if arguments.object_r is not None:
        objectsToDelete = arguments.object_r

    if objectsToDelete is not None:
        if "all" in objectsToDelete:
            deleteAllServers(config)
            deleteAllNetworks(config)
            if len(objectsToDelete) > 1:
                print('Operation "--delete" with the argument "all" has been executed. Other parameters were ignored.')
        elif "servers" in objectsToDelete:
            deleteAllServers(config)
            if len(objectsToDelete) > 1:
                print('Operation "--delete" with the argument "servers" has been executed. '
                      'Other parameters were ignored.')
        elif "networks" in objectsToDelete:
            deleteAllNetworks(config)
            if len(objectsToDelete) > 1:
                print('Operation "--delete" with the argument "networks" has been executed. '
                      'Other parameters were ignored.')
        else:
            for obj in objectsToDelete:
                isDeleted = False
                for servConfig in config["servers"]:
                    if servConfig["name"] == obj:
                        deleteServerByName(obj)
                        isDeleted = True
                        break
                if not isDeleted:
                    for netwConfig in config["networks"]:
                        if netwConfig["name"] == obj:
                            deleteNetworkByName(obj)
                            isDeleted = True
                            break
                if not isDeleted:
                    print('The arguments "' + obj + '" for operation "--delete" is unknown.')

    objectsToCreate = None
    if arguments.object_r is not None:
        objectsToCreate = arguments.object_r
    if arguments.object_c is not None:
        objectsToCreate = arguments.object_c

    if objectsToCreate is not None:
        if "all" in objectsToCreate:
            createAllNetworks(config)
            createAllServers(config, arguments)
            if len(objectsToCreate) > 1:
                print('Operation "--create" with the argument "all" has been executed. Other parameters were ignored.')
        elif "servers" in objectsToCreate:
            createAllServers(config, arguments)
            if len(objectsToCreate) > 1:
                print('Operation "--create" with the argument "servers" has been executed. '
                      'Other parameters were ignored.')
        elif "networks" in objectsToCreate:
            createAllNetworks(config)
            if len(objectsToCreate) > 1:
                print('Operation "--create" with the argument "networks" has been executed. '
                      'Other parameters were ignored.')
        else:
            for obj in objectsToCreate:
                isCreated = False
                for servConfig in config["servers"]:
                    if servConfig["name"] == obj:
                        createServerByName(config, obj, arguments)
                        isCreated = True
                        break
                if not isCreated:
                    for netwConfig in config["networks"]:
                        if netwConfig["name"] == obj:
                            createNetworkByName(config, obj)
                            isCreated = True
                            break
                if not isCreated:
                    print('The arguments "' + obj + '" for operation "--create" is unknown.')
    return


############################################################
#    __  __       _        __ __
#   |  \/  |     (_)      / / \ \
#   | \  / | __ _ _ _ __ | |   | |
#   | |\/| |/ _` | | '_ \| |   | |
#   | |  | | (_| | | | | | |   | |
#   |_|  |_|\__,_|_|_| |_| |   | |
#                         \_\ /_/
#############################################################
def main():
    parser = argparse.ArgumentParser(description='Manage virtual OpenStack infrastructure.',
                                     formatter_class=argparse.RawTextHelpFormatter)

    group_operations = parser.add_argument_group('Operation')

    groupAction = group_operations.add_mutually_exclusive_group()
    groupAction.add_argument("--create", action="store", dest='object_c', nargs='+', default=None, type=str,
                             help="Create the virtual infrastructure.\n"
                                  "OBJECT_TO_CREATE = [ <server_name> | <network_name> | servers | networks | all ]")
    groupAction.add_argument("--delete", dest='object_d', nargs='+', default=None, type=str,
                             help="Delete the virtual infrastructure.\n"
                                  "OBJECT_TO_DELETE = [ <server_name> | <network_name> | servers | networks | all ]")
    groupAction.add_argument("--restart", dest='object_r', nargs='+', default=None, type=str,
                             help="Delete the virtual infrastructure and create it from scratch.\n"
                                  "OBJECT_TO_RESTART = [ <server_name> | <network_name> | servers | networks | all ]")

    group_config = parser.add_argument_group('Generating configurations options')
    group_config.add_argument("--generate-config", dest='config_type', default=None, type=str,
                              choices=['all', 'ssh', 'ansible'],
                              help="Generate ssh config file and/or ansible inventory file "
                                   "based on infrastructure config\n"
                                   "CONFIG_TYPE = [ ssh | ansible | all ]")

    parser.add_argument("--config", dest='configuration_file', type=str, default="config.yml",
                        help="Virtual infrastructure configuration file")
    parser.add_argument("--ssh-dir", dest='ssh_directory', type=str,
                        default=os.path.expanduser("~") + os.path.sep + ".ssh",
                        help="Path to a folder for saving generated ssh keys")

    arguments = parser.parse_args()

    if arguments.object_c is None and \
            arguments.object_r is None and \
            arguments.object_d is None and \
            arguments.config_type is None:
        print('No operation is specified. ')
        print('Please, use "--create", "--delete", "--restart" or "--generate-config" operation.')
        print('Run "' + os.path.basename(__file__) + ' -h|--help" for additional information.')
        return

    config = loadYamlConfig(arguments.configuration_file)
    if config is None:
        return

    # If any of "--create", "--delete" or "--restart" arguments is provided, need to change the infrastructure
    if arguments.object_c is not None or \
            arguments.object_d is not None or \
            arguments.object_r is not None:
        manageInfrastructure(config, arguments)

    # If "--generate-config" argument is provided, need to generate config(s)
    if arguments.config_type is not None:
        generateConfig(config, arguments)


#
# Program entry point
#
if __name__ == "__main__":
    main()
