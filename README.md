# OpenStack Infrastructure Manager

## Infrastructure Configuration

Virtual infrastructure configuration is stored in a YAML-file.
Default name for the configuration is **config.yml**.
In case of another name is used, it has to be specified with the "--config" argument:

    johndoe@server:~/openstack$ ./main.py --config my_another_config_file.yml

The configuration file contains three root sections:

1. parameters
2. networks
3. servers

### Parameters

Common infrastructure parameters are stored in the optional **"parameters"** root element.
The next children elements are supported:

#### 1. dns_nameservers

Optional list of DNS servers hostnames or IP addresses.

Example:

        parameters:
          dns_nameservers:
            - dns_hostname1|dns_ip_address1
            [- dns_hostname2|dns_ip_address2]
            [- ...]

#### 2. users

Optional dictionary of default user names for different OS images.

Example:

        parameters:
          users:
            Ubuntu 18.04: ubuntu
            [image_name: user_name]
            [...: ...]

### Networks

To store networks description a **"networks"** root element can be used.
It is a list of dictionaries of the next structure:

#### 1. name

A unique name of a network. Type: _string_. 

#### 2. cidr

An IPv4 Classless Inter-Domain Routing (CIDR) of the network in the next format: `x.x.x.x/y`.
Type: _string_. 

##### 3. description

Optional description of the network. Type: _string_.

An example of a minimal possible network configuration:

      networks:
        - name: my_network
          cidr: 10.0.0.0/24

### Servers

For storing servers configuration a **"servers"** root element is used.
It is a list of dictionaries of the next structure:

#### 1. name

A unique name of a server. Type: _string_. 

#### 2. image

An image type to be used for the server creation. Type: _string_.
A supported values for "image" parameter can be obtained with `openstack image list`.

#### 3. flavor

A flavor type to be used for the server creation. Type: _string_.
The flavor value encodes the number of VCPU and amount of RAM.
A supported values of "flavor" parameter can be obtained with `openstack flavor list`.

#### 4. networks

A list of server's network connections. Every connection is a dictionary with mandatory
**"name"** and optional **"ipv4"** parameters.

Network name has to match one of the "networks" elements, described above. Type: _string_. 

Network IPv4 address has to fit the corresponding network cidr. Type: _string_. 
        
        
#### 5. keypair

A name of the ssh keypair, that is used for connection to the server. Type: _string_. 

With a ssh keypair
the nest three situations are possible:
1. The public ssh key exists in OpenStack **--->**
it will be uploaded to the server during its creation.
2. The public ssh key is absent in OpenStack, but the private key is in user's ssh directory **--->**
the public ssh key will be generated from the existing private one and then uploaded to OpenStack.
3. The ssh key is absent both in OpenStack and in user's ssh directory **-->**
a new keypair will be generated.

#### 6. init-script

To perform any post-installation steps during the first boot of a created server a user's init script can be used.
The script should have a regular syntax of bash, python or any other interpreter,
i.e. starts with `#!/bin/bash`, `#!/usr/bin/python` or `#!/usr/bin/env python`
(preferred option if are not sure, what python version is used and where the python is located).
The **init-script** argument contains a path to a script on user's machine. Type: _string_. 

If Ansible is used for further configuration of a virtual server, it is highly recommended
to use the next simple script for Ubuntu-based virtual servers:

    #!/bin/bash
    sudo apt -y install python-minimal 2>&1 

An example of possible server configuration:

      - name: my_server
        image: "Ubuntu 18.04"
        flavor: small
        networks:
          - name: public-network
          - name: my_network
            ipv4: 10.0.0.5
        keypair: my_new_ssh_key
        init-script: /home/johndoe/openstack/init.sh

## OpenStack authorization

In the current release of Openstack Infrastructure Manager a v3 version of an authentication is implemented.
This means, one have to generate the **OpenStack application credentials** before the credentials can be used to authenticate the user.

To generate the credentials one need to visit **Dashboard -> Identity -> Application Credentials -> Create Application Credentials** in the OpenStack GUI and generate the credentials. Download a **clouds.yaml** file as well, since it is used in the Openstack Infrastructure Manager operation.

**Note**. The simplest way to use the **clouds.yaml** file is to put it into the local project directory. But that is not the only way. See the [Documentation](https://docs.openstack.org/openstacksdk/latest/user/connection.html#openstack.connection.from_config).

## Virtual infrastructure creating

To create a virtual infrastructure one needs to use the next script syntax:

    ./main.py --create (all|servers|networks|<servers_list>|<networks_list>)

The script operates 
* all - creates all networks, then all servers
* servers - creates all servers (and required networks)
* networks - creates all networks only
* <servers_list> - space separated list of server names from the configuration file
* <networks_list> - space separated list of network names from the configuration file

The output should be similar to:

    johndoe@server:~/openstack$ ./main.py start
    Creation of the network "johndoe_network1" ...   OK
    Creation of the network "johndoe_network2" ...   OK
    Creation of the network "johndoe_network3" ...   OK
    Creation of server "johndoe_srv0" ...   OK
    Creation of server "johndoe_srv1" ...   OK
    Creation of server "johndoe_srv2" ...   OK
    Creation of server "johndoe_srv3" ...   OK
    
In case of any errors please, carefully check the syntax of the configuration script

## Virtual infrastructure restarting

Restarting of the virtual infrastructure uses the same calling syntax:

    ./main.py --restart (all|servers|networks|<servers_list>|<networks_list>)

The main difference - all servers, networks, etc. are deleted, then created from scratch again.

For explanation of the parameters, please refer to **Virtual infrastructure creating** section above.

The output should be similar to:

    johndoe@server:~/openstack$ ./main.py --restart all
    Deleting of the server "johndoe_srv0" ...   OK
    Deleting of the server "johndoe_srv1" ...   OK
    Deleting of the server "johndoe_srv2" ...   OK
    Deleting of the server "johndoe_srv3" ...   OK
    Deleting of the network "johndoe_network1" with its subnet(s) ...   OK
    Deleting of the network "johndoe_network2" with its subnet(s) ...   OK
    Deleting of the network "johndoe_network3" with its subnet(s) ...   OK
    Creation of the network "johndoe_network1" ...   OK
    Creation of the network "johndoe_network2" ...   OK
    Creation of the network "johndoe_network3" ...   OK
    Creation of server "johndoe_srv0" ...   OK
    Creation of server "johndoe_srv1" ...   OK
    Creation of server "johndoe_srv2" ...   OK
    Creation of server "johndoe_srv3" ...   OK

In case of any errors please, carefully check the syntax of the configuration script.

## Virtual infrastructure deleting

To stop and delete all servers and/or networks run the script with "--delete" argument:

    ./main.py --delete (all|servers|networks|<servers_list>|<networks_list>)

For explanation of the parameters, please refer to **Virtual infrastructure creating** section above.

Example of scripts output:

    johndoe@server:~/openstack$ ./main.py --delete all
    Deleting of the server "johndoe_srv0" ...   OK
    Deleting of the server "johndoe_srv1" ...   OK
    Deleting of the server "johndoe_srv2" ...   OK
    Deleting of the server "johndoe_srv3" ...   OK
    Deleting of the network "johndoe_network1" with its subnet(s) ...   OK
    Deleting of the network "johndoe_network2" with its subnet(s) ...   OK
    Deleting of the network "johndoe_network3" with its subnet(s) ...   OK

In case of any errors please, carefully check the syntax of the configuration script.

## Connection to other services

A few additional features were implemented to simplify a connection to other services.
User can generate ssh config and/or ansible inventory file template for the
virtual insrastructure.

### SSH config

To generate ssh config run the script with **"--generate-config ssh"** argument:

    johndoe@server:~/openstack$ ./main.py --generate-config ssh
    ssh config is generated and saved to "./config"
    To see generated ssh config run
        cat ./config
    To append generated config to ssh config file run
        cat ./config >> /home/johndoe/.ssh/config

### Ansible inventory file template

To use the virtual infrastructure the Ansible automaion and configuration service can be used.
The script allows user to generate Ansible inventory file template for current virtual infrastructure.

To generate Ansible inventory file template run the script with **"--generate-config ansible"** argument:

    johndoe@server:~/openstack$ ./main.py --generate-config ansible
    Ansible inventory file is generated and saved to "./inventory.yml"
    To see generated Ansible inventory file run
        cat ./inventory.yml

User can generate both ssh config and Ansible inventory file template with the **"--generate-config all"** argument.

