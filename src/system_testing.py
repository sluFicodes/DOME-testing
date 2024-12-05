import base64
import json
import os
import string
import time
import traceback
import requests
import subprocess
from data.data import *
import sys
import plugin_manager as t
# Prerequisites: 
#   -> ensure apis are using the correct port for listening. Check data.data.API
#   -> turn on mongo, apis, proxy, charging and idm docker containers

prereq = 0
step = 0
asset_id = None
service_spec_id = None
product_spec_id = None
service_id1 = None
service_id2 = None
product_id= None
offering_price_id = None
offering_id = None

def _cleaning_api(api, id):
    if id is not None:
        result = requests.delete(API[api] + "/" + id, headers=token_headers)
        print(f"deleting {api} with id: {id}. Status:  {result.status_code}")

try:
    print("Loading plugin to charging...")
    t.zip_file()
    prereq = 1
    t.copy_zip()
    prereq = 2
    t.load_plugin()
    prereq = 3
    print("finished!")
    # step 1: access token creation
    print("-----------------------------------------------------------")
    print("step 1: access token creation")
    step = 1

    auth_url = "http://localhost:3000/oauth2/token"
    username = os.environ.get("CLIENT_ID")
    password = os.environ.get("CLIENT_SECRET")
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
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 2: Upload the asset
    print("step 2: Upload the asset")
    step = 2

    asset_url = "http://localhost:8004/charging/api/assetManagement/assets/uploadJob"
    token_headers = {
        "Authorization": f"Bearer {access_token}",
    }

    result = requests.post(asset_url ,headers=token_headers, json=ASSET)
    result.raise_for_status()
    result = result.json()
    asset_id = result["id"]
    print("asset id: " + asset_id)
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 3: service spec creation
    print("step 3: service spec creation")
    step = 3
    related_party = requests.get("http://localhost:8633/individual?externalReferenceType.name=admin").json()[0]["id"]
    service_spec_url = "http://localhost:8004/service/serviceSpecification"
    body = service_spec(asset_id, ASSET, "0.1", related_party)
    print(body)
    result = requests.post(service_spec_url, headers=token_headers, json=body)
    result.raise_for_status()
    result = result.json()
    service_spec_id= result["id"]
    service_spec_name= result["name"]
    service_spec_version= result["version"]
    print("service spec id: " + service_spec_id)
    print("service spec name: " + service_spec_name)
    print("service spec version: " + service_spec_version)
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 4: check if the asset exists in MongoDB and verify the existence of the service spec in the api
    print("step 4: check if the asset exists in MongoDB and verify the existence of the service spec in the api")
    step = 4

    command = [
        "docker", "exec", "-i", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--eval", f"db.wstore_resource.find({{_id: ObjectId('{asset_id}')}})"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    if result.stderr or len(result.stdout.strip("\n")) == 0:
        raise Exception("asset doesn't found in mongoDB")
    print("mongoDB:", result.stdout)

    result = requests.get(service_spec_url + "/" + service_spec_id, headers= token_headers)
    if result.status_code >= 300:
        raise Exception("Error retrieving the service spec. Status: "+ f"{result.status_code}. Message: " + result.reason)

    print("service spec GET status: " + str(result.status_code))
    print("service spec: " + json.dumps(result.json(), indent=4))
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")
    
    # step 5: product spec creation
    print("step 5: product spec creation")
    step = 5

    product_spec_url = "http://localhost:8004/catalog/productSpecification"
    product_spec_body = product_spec(service_spec_id, related_party)
    result = requests.post(product_spec_url, json= product_spec_body, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    product_spec_id = result["id"]
    print("product spec id: " + product_spec_id)
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 6: verify the existence of the product spec in the api
    print("step 6: verify the existence of the product spec in the api")
    step = 6

    result = requests.get(product_spec_url + "/" + product_spec_id, headers= token_headers)
    result.raise_for_status()

    print("product spec GET status: " + str(result.status_code))
    print("product spec: " + json.dumps(result.json(), indent=4))
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 7: two services creation with api
    print("step 7: two services creation with api")
    step = 7

    service_url = API["service"]
    body1 = service("service1" , service_spec_id, service_spec_version, service_spec_name, asset_id, related_party)
    body2 = service("service2" , service_spec_id, service_spec_version, service_spec_name, asset_id, related_party)
    result = requests.post(service_url, json=body1, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    service_id1 = result["id"]
    assert result["serviceSpecification"]["id"] == service_spec_id, "missing service spec in service1"
    print(f"API created service1 with id: {service_id1}")
    result = requests.post(service_url, json=body2, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    service_id2= result["id"]
    assert result["serviceSpecification"]["id"] == service_spec_id, "missing service spec in service2"
    print(f"API created service2 with id: {service_id2}")
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 8: product creation with api
    print("step 8: product creation with api")
    step = 8

    product_url = "http://localhost:8004/inventory/product" # Cannot use it
    body = product_with_service_list("product1", ["service1", "service2"], [service_id1, service_id2])
    result = requests.post(API["product"], json= body, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    product_id = result["id"]
    print(f"API created product with id: {product_id}")
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 9: product offering price creation
    print("step 9: product offering price creation")
    step = 9

    offer_price_url = "http://localhost:8004/catalog/productOfferingPrice"
    body = offering_price("price", "1.0", "EUR", "1.0")
    result = requests.post(offer_price_url, json=body, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    offering_price_id = result["id"]
    offering_price_name = result["name"]
    offering_price_version = result["version"]
    
    print(f"created product offering price with id: {offering_price_id}")
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 10: verify the existence of the product offering creation
    print("step 10: verify the existence of the product offering price creation")
    step = 10

    result = requests.get(offer_price_url + "/" +offering_price_id, headers= token_headers)
    result.raise_for_status()

    print("offering price GET status: " + str(result.status_code))
    print("offering price: " + json.dumps(result.json(), indent=4))
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 11: product offering creation
    print("step 11: product offering creation")
    step = 11

    offering_url = "http://localhost:8004/catalog/productOffering"
    body = offering("offering", product_spec_id, offering_price_id, offering_price_name, offering_price_version)
    result = requests.post(offering_url, json= body, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    offering_id = result["id"]
    print(f"created offering with id: {offering_id}")
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 12: check if the offering exists in MongoDB and verify its existence in the api
    print("step 12: check if the offering exists in MongoDB and verify its existence in the api")
    step = 12

    command = [
        "docker", "exec", "-i", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--eval", f"db.wstore_offering.find({{off_id: '{offering_id}'}})"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    assert len(result.stdout.strip("\n")) != 0, "not found offering in mongoDB"

    print("mongoDB:", result.stdout)

    result = requests.get(offering_url + "/" + offering_id, headers= token_headers)
    result.raise_for_status()
    print("offering GET status: " + str(result.status_code))
    print("offering: " + json.dumps(result.json(), indent=4))
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 13: upgrading asset
    print("step 13: upgrading asset")
    step = 13

    upgrading_asset_url = f"http://localhost:8004/charging/api/assetManagement/assets/{asset_id}/upgradeJob"
    result = requests.post(upgrading_asset_url, json=UPGRADED_ASSET, headers=token_headers)
    result.raise_for_status()
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 14: verify asset have 'upgrading' state
    print("step 14: verify asset have 'upgrading' state")
    step = 14

    command = [
        "docker", "exec", "-i", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--quiet", "--eval", f"db.wstore_resource.find({{_id: ObjectId('{asset_id}') , state: 'upgrading'}})"
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    assert len(result.stdout.strip("\n")) !=0 ,"asset doesn't found in mongoDB"
    print("asset:   " + result.stdout)
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 15: wait 20 second
    print("step 15: wait 16 second")
    step = 15
    time.sleep(16)
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 16: Verify asset doesn't upgraded
    print("step 16: Verify asset is not upgraded")
    step = 16

    command = [
        "docker", "exec", "-i", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--quiet", "--eval", f"db.wstore_resource.find({{_id: ObjectId('{asset_id}') , state: 'upgrading'}})"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    assert len(result.stdout.strip("\n")) == 0, "asset is upgraded when it should not"

    command = [
        "docker", "exec", "-i", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--quiet", "--eval", f"db.wstore_resource.find({{_id: ObjectId('{asset_id}') , state: 'attached'}})"
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    assert len(result.stdout.strip("\n")) != 0, f"asset state error: {result.stdout}"

    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 17: upgrading asset
    print("step 17: upgrading asset")
    step = 17

    upgrading_asset_url = f"http://localhost:8004/charging/api/assetManagement/assets/{asset_id}/upgradeJob"
    result = requests.post(upgrading_asset_url, json=UPGRADED_ASSET, headers=token_headers)
    result.raise_for_status()
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 18: patching service specification
    print("step 18: patching service specification")
    step = 18

    body = service_spec(asset_id, UPGRADED_ASSET, "0.5", related_party)
    result = requests.patch(service_spec_url + "/" + service_spec_id, json=body, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    assert result["version"] == "0.5", "upgraded service spec was not changed"
    print("upgraded service spec: " + json.dumps(result, indent=4))
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 19: check if the asset was upgraded in MongoDB and verify the upgradion of the service spec in the api
    print("step 19: check if the asset was upgraded in MongoDB and verify the upgradion of the service spec in the api")
    step = 19

    command = [
        "docker", "exec", "-i", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--eval", f"db.wstore_resource.find({{_id: ObjectId('{asset_id}'), state: 'attached', version: '0.5'}})"
    ]

    result = subprocess.run(command, capture_output=True, text=True)
    assert len(result.stdout.strip("\n")) != 0, "asset with the new version doesn't found in mongoDB"
    print("mongoDB:", result.stdout)

    result = requests.get(service_spec_url + "/" + service_spec_id, headers= token_headers)
    result.raise_for_status()
    print("service spec GET status: " + str(result.status_code))
    result = result.json()
    assert result["version"] == '0.5', "the version of the service spec should be '0.5'"
    print("service spec: " + json.dumps(result, indent=4))
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    # step 20: Checking service 1 and service 2 have been upgraded
    print("step 20: Checking service 1 and service 2 have been upgraded")
    time.sleep(10)
    step = 20
    print("checking service 1")
    result = requests.get(service_url + "/" + service_id1, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    for char in result["serviceCharacteristic"]:
        name = char["name"]
        if name.lower() == "asset type":
            assert char["value"] == UPGRADED_ASSET["resourceType"], f"wrong asset type, expected: {UPGRADED_ASSET['resourceType']}, actual: {char['value']}"
            print(f"{name} = {char['value']}")
        elif name.lower() == "media type":
            assert char["value"] == UPGRADED_ASSET["contentType"], f"wrong media type, expected: {UPGRADED_ASSET['contentType']}, actual: {char['value']}"
            print(f"{name} = {char['value']}")
        elif name.lower() == "location":
            assert char["value"] == UPGRADED_ASSET["content"], f"wrong location, expected: {UPGRADED_ASSET['content']}, actual: {char['value']}"
            print(f"{name} = {char['value']}")
        elif name.lower() == "asset":
            assert char["value"] == asset_id, "wrong asset id"
            print(f"{name} = {char['value']}")
        else:
            raise AssertionError(f"error in {name} characteristic")

    print("checking service 2")
    result = requests.get(service_url + "/" + service_id2, headers=token_headers)
    result.raise_for_status()
    result = result.json()
    for char in result["serviceCharacteristic"]:
        name = char["name"]
        if name.lower() == "asset type":
            assert char["value"] == UPGRADED_ASSET["resourceType"], f"wrong asset type, expected: {UPGRADED_ASSET['resourceType']}, actual: {char['value']}"
            print(f"{name} = {char['value']}")
        elif name.lower() == "media type":
            assert char["value"] == UPGRADED_ASSET["contentType"], f"wrong media type, expected: {UPGRADED_ASSET['contentType']}, actual: {char['value']}"
            print(f"{name} = {char['value']}")
        elif name.lower() == "location":
            assert char["value"] == UPGRADED_ASSET["content"], f"wrong location, expected: {UPGRADED_ASSET['content']}, actual: {char['value']}"
            print(f"{name} = {char['value']}")
        elif name.lower() == "asset":
            assert char["value"] == asset_id, "wrong asset id"
            print(f"{name} = {char['value']}")
        else:
            raise AssertionError(f"error in {name} characteristic")
            
    print(f"\033[32mstep {step} successfully completed\033[0m")
    print("-----------------------------------------------------------")

    print("\033[32mall steps are successfully completed\033[0m")
    sys.exit(0)

except requests.exceptions.HTTPError as e:
    print(f"\033[31mrequest error at step {step}\033[0m")
    if e.response is not None:
        print(f"\033[31mURL Error: {e.response.url}\033[0m")
        print(f"\033[31mstatus Code: {e.response.status_code}\033[0m")
        print(f"\033[31mresponse Body:  {e.response.text}\033[0m")
    else:
        print(f"\033[31mrequest error: {e}\033[0m")
    sys.exit(1)
except Exception as e:
    print(f"\033[31m-----------------------------------------------------------\033[0m")
    print(f"\033[31merror at step {step}\033[0m")
    print(f"\033[31m    {e}\033[0m")
    # Imprime la línea donde ocurrió el error
    traceback.print_exc()
    print(f"\033[31m-----------------------------------------------------------\033[0m")
    sys.exit(1)


finally:
    print("Cleaning up")
    _cleaning_api("offering_price", offering_price_id)
    _cleaning_api("offering", offering_id)
    _cleaning_api("product", product_id)
    _cleaning_api("service", service_id1)
    _cleaning_api("service", service_id2)
    _cleaning_api("product_spec", product_spec_id)
    _cleaning_api("service_spec", service_spec_id)
    if asset_id is not None:
        command = [
        "docker", "exec", "-ti", "charging-docker-charging_mongo-1",
        "mongosh", "wstore_db", "--eval", f"db.wstore_resource.deleteOne({{_id: ObjectId('{asset_id}')}})"
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        print("cleaning asset output:", result.stdout)
    if prereq > 0:
        t.delete_zip()
    if prereq > 1:
        t.remote_delete_zip()
    if prereq > 2:
        t.remove_plugin()
    print("-----------------------------------------------------------")
