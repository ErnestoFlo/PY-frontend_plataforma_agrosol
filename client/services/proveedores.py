import requests
import os

API_BASE_URL = "https://192.168.1.55:7155/api/Proveedores"

# Configura verify según el ambiente
VERIFY_SSL = os.getenv('VERIFY_SSL', 'False') == 'True'

def get_all_proveedores():
    return requests.get(API_BASE_URL, verify=VERIFY_SSL).json()

def get_by_id(id):
    return requests.get(f"{API_BASE_URL}/{id}", verify=VERIFY_SSL).json()

def create(data):
    return requests.post(API_BASE_URL, json=data, verify=VERIFY_SSL)

def update(id, data):
    return requests.put(f"{API_BASE_URL}/{id}", json=data, verify=VERIFY_SSL)

def delete(id):
    return requests.delete(f"{API_BASE_URL}/{id}", verify=VERIFY_SSL)


## en caso de funcionar:
# import requests
# import os

# API_BASE_URL = "https://192.168.1.55:7155/api/Proveedores"

# # Crea una sesión reutilizable
# session = requests.Session()
# session.verify = False  # O True para producción

# def get_all():
#     return session.get(API_BASE_URL).json()

# def get_by_id(id):
#     return session.get(f"{API_BASE_URL}/{id}").json()

# def create(data):
#     return session.post(API_BASE_URL, json=data)

# def update(id, data):
#     return session.put(f"{API_BASE_URL}/{id}", json=data)

# def delete(id):
#     return session.delete(f"{API_BASE_URL}/{id}") 