import re

# for validating an Email 
def validate_email(email):  
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    if(re.search(regex,email)):  
        return True 
    return False