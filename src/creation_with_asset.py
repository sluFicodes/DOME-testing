import base64
import json
import requests
import subprocess
from data.data import *

# Prerequisites: 
#   -> ensure apis are using the correct port for listening. Check data.data.API
#   -> turn on mongo, apis, proxy, charging and idm docker containers

asset_id = None
service_spec_id = None
product_spec_id = None
try:
    # step 1: access token creation
    print("-----------------------------------------------------------")
    print("step 1: access token creation")

    auth_url = "http://idm.docker:3000/oauth2/token"
    username = "c49a8f7d-6955-47e7-a8a2-2d7af5c0f942"
    password = "43133f86-5618-418a-a936-e999bdf31ad3"
    basic_token = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {
        "Authorization": f"Basic {basic_token}",
        "Content-type": "application/x-www-form-urlencoded"
    }
    auth_body = {
        "grant_type": "password",
        "username": "admin@test.com",
        "password": "1234",
    }

    result = requests.post(auth_url, headers=headers, data= auth_body).json()
    access_token = result["access_token"]
    print("access_token:" + access_token)
    print("\033[32mstep 1 successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 2: Upload the asset
    print("step 2: Upload the asset")

    asset_url = "http://localhost:8004/charging/api/assetManagement/assets/uploadJob"
    token_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    result = requests.post(asset_url ,headers=token_headers, json=ASSET)
    if result.status_code >= 300:
        raise Exception(str(result.status_code) + result.reason)
    result = result.json()
    asset_id = result["id"]
    print("asset id: " + asset_id)
    print("\033[32mstep 2 successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 3: service spec creation
    print("step 3: service spec creation")


    service_spec_url = "http://proxy.docker:8004/service/serviceSpecification"
    body = service_spec_body(asset_id)
    result = requests.post(service_spec_url, headers=token_headers, json=body)
    if result.status_code >= 300:
        raise Exception(str(result.status_code)+ " " + result.reason)
    result = result.json()
    service_spec_id= result["id"]
    print("service spec id: " + service_spec_id)
    print("\033[32mstep 3 successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 4: check if the asset exists in MongoDB and verify the existence of the service spec in the api
    print("check if the asset exists in MongoDB and verify the existence of the service spec in the api")

    command = [
        "docker", "exec", "-ti", "docker-dev-charging_mongo-1",
        "mongosh", "wstore_db", "--eval", f"db.wstore_resource.find({{_id: ObjectId('{asset_id}')}})"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.stderr:
        raise Exception("asset doesn't found in mongoDB")
    print("output:", result.stdout)

    result = requests.get(service_spec_url + "/" + service_spec_id, headers= token_headers)
    if result.status_code >= 300:
        raise Exception("Error retrieving the service spec. Status: "+ f"{result.status_code}. Message: " + result.reason)

    print("service spec GET status: " + str(result.status_code))
    print("service spec: " + json.dumps(result.json(), indent=4))
    print("\033[32mstep 4 successfully completed\033[0m")
    print("-----------------------------------------------------------")
    
    # step 5: product spec creation
    print("step 5: product spec creation")
    
    product_spec_url = "http://proxy.docker:8004/catalog/productSpecification"
    product_spec_body = product_spec(service_spec_id)
    result = requests.post(product_spec_url, json= product_spec_body, headers=token_headers)
    if result.status_code >=300:
        raise Exception("product spec creation failed. Status: "+ f"{result.status_code}. Message: " + result.reason)
    result = result.json()
    product_spec_id = result["id"]
    print("product spec id: " + product_spec_id)
    print("\033[32mstep 5 successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 6: verify the existence of the product spec in the api
    print("step 6: verify the existence of the product spec in the api")
    result = requests.get(product_spec_url + "/" + product_spec_id, headers= token_headers)
    if result.status_code >= 300:
        raise Exception("Error retrieving the product spec. Status: "+ f"{result.status_code}. Message: " + result.reason)

    print("product spec GET status: " + str(result.status_code))
    print("product spec: " + json.dumps(result.json(), indent=4))
    print("\033[32mstep 6 successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 7: two services creation
    print("step 7: two services creation")
    service_url = "http://proxy.docker:8004/service/service"
    

    print("-----------------------------------------------------------")

finally:
    print("Cleaning up")
    if product_spec_id is not None:
        result = requests.delete(API["product_spec"] + "/" + product_spec_id, headers=token_headers)
        print("deleting product spec status: " + str(result.status_code))
    if service_spec_id is not None:
        result = requests.delete(API["service_spec"] + "/" + service_spec_id, headers=token_headers)
        print("deleting service spec status: " + str(result.status_code))
    if asset_id is not None:
        command = [
        "docker", "exec", "-ti", "docker-dev-charging_mongo-1",
        "mongosh", "wstore_db", "--eval", f"db.wstore_resource.deleteOne({{_id: ObjectId('{asset_id}')}})"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print("cleaning asset output:", result.stdout)
    print("-----------------------------------------------------------")
