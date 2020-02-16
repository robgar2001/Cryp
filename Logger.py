import datetime
def Log(message):
    print('('+str(datetime.datetime.now())+')'+' | '+str(message))
    return