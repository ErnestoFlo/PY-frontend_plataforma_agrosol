import requests
import os

API_BASE_URL = "https://192.168.1.55:7155/api/Proveedores"

session = requests.Session()
session.verify = False

def get_all():
    return session.get(API_BASE_URL).json()

def get_by_id(id):
    return session.get(f"{API_BASE_URL}/{id}").json()

def create(data):
    return session.post(API_BASE_URL, json=data)

def update(id, data):
    return session.put(f"{API_BASE_URL}/{id}", json=data)

def delete(id):
    return session.delete(f"{API_BASE_URL}/{id}") 