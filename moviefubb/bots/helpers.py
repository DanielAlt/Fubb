import random

def updateConfig(args, kwargs):
    for arg in args.keys():
        if arg in kwargs.keys():
            args[arg] = kwargs[arg]
    return (args)

def generateUUID():
    return ( "".join([ chr(random.randrange(65,90)) if ( (random.randrange(0,2)%2) == 0) else ( chr(random.randrange(65,90)).lower()) for x in range(0,33)]) )
