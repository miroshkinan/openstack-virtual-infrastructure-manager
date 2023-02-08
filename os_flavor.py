#    ______ _
#   |  ____| |
#   | |__  | | __ ___   _____  _ __
#   |  __| | |/ _` \ \ / / _ \| '__|
#   | |    | | (_| |\ V / (_) | |
#   |_|    |_|\__,_| \_/ \___/|_|
#
#


# isFlavorExist(flavorName) returns True if an flavor with the name flavorName exists.
def isFlavorExist(conn, flavorName):
    if conn.compute.find_flavor(flavorName) is not None:
        return True
    return False


# getFlavorByName(flavorName) returns flavor object of the flavor with the name flavorName.
# if the flavor does not exist, the function returns None
def getFlavorByName(conn, flavorName):
    flavor = conn.compute.find_flavor(flavorName)
    if flavor is not None:
        return flavor
    return None
