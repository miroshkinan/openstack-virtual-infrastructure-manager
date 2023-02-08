#    _____
#   |_   _|
#     | |  _ __ ___   __ _  __ _  ___  ___
#     | | | '_ ` _ \ / _` |/ _` |/ _ \/ __|
#    _| |_| | | | | | (_| | (_| |  __/\__ \
#   |_____|_| |_| |_|\__,_|\__, |\___||___/
#                           __/ |
#                          |___/

from globals import conn


# isImageExist(imageName) returns True if an image with the name imageName exists.
def isImageExist(imageName):
    return conn.compute.find_image(imageName) is not None


# getImageByName(imageName) returns image object of the image with the name imageName.
# if the image does not exist, the function returns None
def getImageByName(imageName):
    return conn.compute.find_image(imageName)