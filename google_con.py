
from Google import Create_Service

def service():
    CLIENT_SECRET_FILE = 'client_secret.json'
    API_NAME = 'drive'
    API_VERSION = 'v3'
    SCOPES = ['https://www.googleapis.com/auth/drive']

    servico = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
    if not servico:
        servico = Create_Service(CLIENT_SECRET_FILE,API_NAME,API_VERSION,SCOPES)
    return servico
