#!/bin/bash
set -e # Stop script if any error occurs

proxy_br=$1
charging_br=$2

if [[ -z $proxy_br || -z $charging_br ]]; then
    echo "use structure: command proxy_branch charging_branch"
    exit 1
fi

# $1 = repo, $2 = branch
clone_repo_branch () {
    echo "Cloning $1 with the branch $2..."
    git clone -b $2 $1 "$3"
    cd "$3" || exit 1
    echo "charging repo cloned successfully."
    cd docker-dev
    echo "building docker image..."
    docker build -t $4 .    
    cd ../..
}


# TODO: repos need to be set dinamically
proxy_rp="git@github.com:sluFicodes/business-ecosystem-logic-proxy.git"
charging_rp="git@github.com:sluFicodes/business-ecosystem-charging-backend.git"

# 1. install pre-requirement
echo "updating pre-requesites"
sudo apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    vim \
    zip
echo "python3 version:"
python3 --version
echo "pip3 version:"
pip3 --version


if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip3 install --no-cache-dir -r requirements.txt
else
    echo "requirements.txt  not found"
    exit 1
fi
# 2. clone specified repo and build the docker images
clone_repo_branch $proxy_rp $proxy_br proxy_repo proxy-system-dev

clone_repo_branch $charging_rp  $charging_br charging_repo charging-system-dev

# 3. docker up and register app in idm
cd idm-docker
docker compose up -d
echo "idm server deployed"
cd ..
echo "registering app in idm ..."
admin_token=$(curl -X POST \
     -H "Content-Type:application/json" \
     -d '{ "name": "admin@test.com",
         "password": "1234"
        }' \
     -i \
     http://idm.docker:3000/v1/auth/tokens | grep -i "X-Subject-Token:" | awk '{print $2}' | sed 's/[[:space:]]//g')

echo "idm admin token saved!"

app_json=$(curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json"\
     -d '{
            "application": {
                "name": "Test_application 1",
                "description": "description",
                "redirect_uri": "http://localhost/login",
                "redirect_sign_out_uri": "http://localhost/logout",
                "url": "http://localhost",
                "grant_type": [
                "authorization_code",
                "implicit",
                "password",
                "refresh_token",
                "client_credentials"
                ],
                "token_types": [
                    "jwt",               
                "permanent"
                ]            
            }                   
        }' \                      
     http://idm.docker:3000/v1/applications)

echo "app registering response"
echo $app_json

CLIENT_ID=$(python3 auth_cred.py --key id --sjson $app_json)
CLIENT_SECRET=$(python3 auth_cred.py --key secret --sjson $app_json)
export CLIENT_ID
export CLIENT_SECRET
echo "app client id and secret saved!"
echo "client_id: $CLIENT_ID" 
echo "client_secret: $CLIENT_SECRET" 

cd charging-docker
docker compose up -d
cd ..

cd proxy-docker
docker compose up -d
cd ..

echo "proxy and charging deployed"

# 4. execute cloned dockers TODO: idm

docker exec charging-docker-charging-1 python3 /business-ecosystem-charging-backend/src/manage.py migrate
docker exec charging-docker-charging-1 python3 /business-ecosystem-charging-backend/src/manage.py runserver 0.0.0.0:8006

docker exec proxy-docker-proxy-1 /business-ecosystem-logic-proxy/node server.js

# 5. run system test
cd src
python3 system_testing.py
cd ..
# 6. docker down

cd charging-docker
docker compose down
cd ..

cd proxy-docker
docker compose down
cd ..
