#    ____                        _           _
#   / ___| _ __   __ _ _ __  ___| |__   ___ | |_ ___
#   \___ \| '_ \ / _` | '_ \/ __| '_ \ / _ \| __/ __|
#    ___) | | | | (_| | |_) \__ \ | | | (_) | |_\__ \
#   |____/|_| |_|\__,_| .__/|___/_| |_|\___/ \__|___/
#                     |_|

from globals import conn


# isSnapshotExist(imageName) returns True if an image with the name imageName exists.
def isSnapshotExist(imageName):
    return conn.compute.find_image(imageName) is not None


# getSnapshotByName(imageName) returns image object of the image with the name imageName.
# if the image does not exist, the function returns None
def getSnapshotByName(imageName):
    return conn.compute.find_image(imageName)