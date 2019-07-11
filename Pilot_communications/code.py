from DIRAC import gConfig, S_OK, S_ERROR
import json

def get_DN(name_of_group):
    '''This function return DN of users in group
       which is defined as name_of_group from configuration file'''
    if not isinstance(name_of_group, basestring):
        return S_ERROR('Name of group must be string')
    else:
       try:
           string_list=gConfig.getValue('/Registry/Groups/'+name_of_group+'/Users')
           Users_list=string_list.split(',')
           DN_list=[gConfig.getValue('/Registry/Users/'+user+'/DN') for user in Users_list]
           return S_OK(json.dumps(DN_list))
       except AttributeError:
           return S_ERROR('There must be problem with name of group')
print(get_DN('Some_group'))
