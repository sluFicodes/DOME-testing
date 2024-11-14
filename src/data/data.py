
CONFIG = {
    "related_party_id": "urn:ngsi-ld:individual:7ffcd2cc-c730-4ab4-819f-1ec7288e0eac"
}
# For cleaning tests
API ={
    "service_spec": "http://localhost:8637/serviceSpecification",
    "product_spec": "http://localhost:8632/productSpecification"
}

ASSET = {
    "resourceType": "Basic Service",
    "content": "https://www.google.com/?hl=es",
    "contentType": "URL"
}
def service_spec_body(asset_id):
    return {
        "version": "0.1",
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
                        "value": ASSET["resourceType"],
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
                        "value": ASSET["contentType"],
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
                        "value": ASSET["content"],
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
                        "valueFrom": "",
                        "valueTo": ""
                    }
                ]
            }
        ],
        "serviceSpecRelationship": [],
        "attachment": [],
        "relatedParty": [
            {
                "id": CONFIG["related_party_id"],
                "href": F"http://proxy.docker:8004/party/individual/urn:ngsi-ld:individual:{CONFIG['related_party_id']}",
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