import os
from openstack import connection
import openstack.config

# ---------------------------------------------------------------
# Global definitions

config = openstack.config.get_cloud_region(cloud='openstack')
conn = connection.Connection(config=config)

# ---------------------------------------------------------------
