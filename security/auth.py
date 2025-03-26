from fastapi import HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

security = HTTPBasic()

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    valid_username = 'ai developers'
    valid_password = 'T3am@1deV3l0peR5'
    if credentials.username != valid_username or credentials.password != valid_password:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return credentials  # Returns credentials if needed