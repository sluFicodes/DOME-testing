import json
import requests

f = open("data/sTest/package.json", "r")
plugin = f.read()
plugin = json.loads(plugin)

# TODO: Need to be transferred to system_testing.py and get the data as parameter
body = requests.get("http://localhost:8633/individual?externalReferenceType.name=admin").json()

CONFIG = {
    "related_party_id": body[0]["id"]
}
# For cleaning tests
API ={
    "service_spec": "http://localhost:8637/serviceSpecification",
    "product_spec": "http://localhost:8632/productSpecification",
    "service": "http://localhost:8643/service",
    "product": "http://localhost:8642/product",
    "offering_price": "http://localhost:8632/productOfferingPrice",
    "offering": "http://localhost:8632/productOffering"
}

ASSET = {
    "resourceType": plugin["name"],
    "content": "https://www.google.com/?hl=es",
    "contentType": plugin["formats"][0]
}

UPGRADED_ASSET = {
    "resourceType": plugin["name"],
    "content": "https://www.bing.com/?setlang=es",
    "contentType": plugin["name"][0]
}
def service_spec(asset_id, asset, version):
    return {
        "version": version,
        "lifecycleStatus": "Active",
        "isBundle": False,
        "specCharacteristic": [
            {
                "id": "urn:ngsi-ld:characteristic:06dc819a-41ea-478b-9173-2995d5fd2a5c",
                "name": "Asset type",
                "description": "Type of the digital asset described in this service specification",
                "valueType": "string",
                "configurable": False,
                "characteristicValueSpecification": [
                    {
                        "isDefault": True,
                        "unitOfMeasure": "",
                        "value": asset["resourceType"],
                        "valueFrom": "",
                        "valueTo": ""
                    }
                ]
            },
            {
                "id": "urn:ngsi-ld:characteristic:ec57e38b-45c1-4faa-a94e-3998cfbc8f01",
                "name": "Media type",
                "description": "Media type of the digital asset described in this service specification",
                "valueType": "string",
                "configurable": False,
                "characteristicValueSpecification": [
                    {
                        "isDefault": True,
                        "unitOfMeasure": "",
                        "value": asset["contentType"],
                        "valueFrom": "",
                        "valueTo": ""
                    }
                ]
            },
            {
                "id": "urn:ngsi-ld:characteristic:d3a7418f-f0e9-4256-9b12-e39cd49e2915",
                "name": "Location",
                "description": "URL pointing to the digital asset described in this service specification",
                "valueType": "string",
                "configurable": False,
                "characteristicValueSpecification": [
                    {
                        "isDefault": True,
                        "unitOfMeasure": "",
                        "value": asset["content"],
                        "valueFrom": "",
                        "valueTo": ""
                    }
                ]
            },
            {
                "id": "urn:ngsi-ld:characteristic:2ca03823-68bb-4d69-9de1-3be1179a8f96",
                "name": "Asset",
                "description": "ID of the asset being offered as registered in the BAE",
                "valueType": "string",
                "configurable": False,
                "characteristicValueSpecification": [
                    {
                        "isDefault": True,
                        "unitOfMeasure": "",
                        "value": asset_id,
                        # "valueFrom": "",
                        # "valueTo": ""
                    }
                ]
            }
        ],
        "serviceSpecRelationship": [],
        "attachment": [],
        "relatedParty": [
            {
                "id": CONFIG["related_party_id"],
                "href": f"http://proxy.docker:8004/party/individual/urn:ngsi-ld:individual:{CONFIG['related_party_id']}",
                "role": "Owner"
            }
        ],
        "name": "uu",
        "brand": "uu",
        "resourceSpecification": []
    }


def product_spec(service_spec_id):
    return {
    "version": "0.1",
    "lifecycleStatus": "Active",
    "isBundle": False,
    "serviceSpecRelationship": [],
    "attachment": [],
    "relatedParty": [
        {
            "id": CONFIG["related_party_id"],
            "href": F"http://proxy.docker:8004/party/individual/{CONFIG['related_party_id']}",
            "role": "Owner"
        }
    ],
    "name": "uu",
    "brand": "brand",
    "description": "product description",
    "resourceSpecification": [],
    "serviceSpecification": [
        {
            "id": service_spec_id,
            "href": service_spec_id,
            "version": "0.1"
        }
    ],
    "bundledProductSpecification": []
}

def service(name ,service_spec_id, service_spec_version, service_spec_name, asset_id):
    return {
    "name": name,
    "catalogType": "test",
    "serviceSpecification": {
        "version": service_spec_version,
        "id":  service_spec_id,
        "href": service_spec_id,
        "name": service_spec_name
    },
    "supportingResource": [],
    "relatedParty": [
            {
                "id": CONFIG["related_party_id"],
                "href": f"http://proxy.docker:8004/party/individual/urn:ngsi-ld:individual:{CONFIG['related_party_id']}",
                "role": "Owner"
            }
        ],
    "serviceCharacteristic": [
        {
            "id": "urn:ngsi-ld:characteristic:06dc819a-41ea-478b-9173-2995d5fd2a5c",
            "name": "Asset type",
            "valueType": "string",
            "value": ASSET["resourceType"]
        },
        {
            "id": "urn:ngsi-ld:characteristic:ec57e38b-45c1-4faa-a94e-3998cfbc8f01",
            "name": "Media type",
            "valueType": "string",
            "value": ASSET["contentType"]
        },
        {
            "id": "urn:ngsi-ld:characteristic:d3a7418f-f0e9-4256-9b12-e39cd49e2915",
            "name": "Location",
            "valueType": "string",
            "value": ASSET["content"]
        },
        {
            "id": "urn:ngsi-ld:characteristic:2ca03823-68bb-4d69-9de1-3be1179a8f96",
            "name": "Asset",
            "valueType": "string",
            "value": asset_id
        }
    ]
}

def product(product_name, service_name, service_id):
    return {
    "name": product_name,
    "catalogType": "test",
    "realizingService": [
        {
            "id":  service_id,
            "name": service_name,
            "href":   service_id
        }
    ]
}

def product_with_service_list(product_name, service_names, service_ids):
    size = len(service_names)
    if size != len(service_ids):
        raise Exception("service_names and service_ids must be the same size")
    return {
    "name": product_name,
    "catalogType": "test",
    "realizingService": [
        {
            "id":  service_ids[i],
            "name": service_names[i],
            "href":   service_ids[i]
        } for i in range(size)
    ]
}

def offering(name, product_spec_id, offering_price_id, offering_price_name, offering_price_version):
    return {
        "isBundle": False,
        "name": name,
        "version": "1.0",
        "productSpecification": {"id": product_spec_id, "href": product_spec_id},
        "productOfferingPrice": [
            {
                "name": offering_price_name,
                "version": offering_price_version,
                "id": offering_price_id,
                "href": offering_price_id
            }
        ],
    }

def offering_price(name, version, price_unit, price_value):
    return {
        "name": name,
        "isBundle": False,
        "version": version,
        "name": "plan",
        "priceType": "one time",
        "price": {
            "unit": price_unit,
            "value": price_value
        
        },
        "validFor": {
            "startDateTime": "2028-11-19T10:13:00.948Z"
        }
    }
