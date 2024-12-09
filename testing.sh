#!/bin/bash
set -e # Stop script if any error occurs

PROXY_BR=$1
PROXY_REPO=$2
CHARGING_BR=$3
CHARGING_REPO=$4
TM_VERSION=$5


if [[ -z $PROXY_BR || -z $CHARGING_BR || -z $TM_VERSION || -z $PROXY_REPO || -z $CHARGING_REPO ]]; then
    echo -e "use structure: command PROXY_BRANCH PROXY_REPO CHARGING_BRANCH CHARGING_REPO TMFORUM_VERSION\033[0m"
    exit 1
fi

# $1 = repo, $2 = branch
clone_repo_branch () {
    echo -e "\033[35mCloning $1 with the branch $2...\033[0m"
    git clone -b $2 $1 "$3"
    cd "$3" || exit 1
    echo -e "\033[35mcharging repo cloned successfully.\033[0m"
    cd docker-dev
    echo -e "\033[35mbuilding docker image...\033[0m"
    docker build -qt $4 .    
    cd ../..
}

wait_server() {
URL=$1
TIMEOUT=600
INTERVAL=5
echo -e "\033[35mwaiting until the server is ready ($URL)...\033[0m"

SECONDS_WAITED=0
while ! curl -s --head --request GET "$URL" | grep "200 OK" > /dev/null; do
    sleep $INTERVAL
    SECONDS_WAITED=$((SECONDS_WAITED + INTERVAL))
    if [ $SECONDS_WAITED -ge $TIMEOUT ]; then
        echo -e "\033[31mTimeout error: waited $TIMEOUT seconds.\033[0m"
        exit 1
    fi
done

echo -e "\033[35m$2 ready in $SECOND_WAITED seconds\033[0m"
}
echo "git token: $GIT_TOKEN"
echo "test: $ERT"
# TODO: repos need to be set dinamically
if [ -z $GIT_TOKEN ]; then
    echo -e "\033[31mGIT_TOKEN is not available\033[0m"
    exit 1
    # PROXY_RP="git@github.com:sluFicodes/business-ecosystem-logic-proxy.git"
    # CHARGING_RP="git@github.com:sluFicodes/business-ecosystem-charging-backend.git"
else
    PROXY_RP="https://$GIT_TOKEN:@github.com/$PROXY_REPO.git"
    CHARGING_RP="https://$GIT_TOKEN:@github.com/$CHARGING_REPO.git"
    echo proxy git: $PROXY_RP
    echo charging git: $CHARGING_RP
fi


# 1. install pre-requirement
echo -e "\033[35mSTART BUILDING\033[0m"
echo -e "\033[35mupdating pre-requesites\033[0m"
apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    vim \
    zip
echo -e "\033[35mpython3 version:\033[0m"
python3 --version
echo -e "\033[35mpip3 version:\033[0m"
pip3 --version


if [ -f "requirements.txt" ]; then
    echo -e "\033[35mInstalling dependencies from requirements.txt...\033[0m"
    pip3 install --no-cache-dir -r requirements.txt
else
    echo -e "\033[35mrequirements.txt  not found\033[0m"
    exit 1
fi
# 2. clone specified repo and build the docker images
echo -e "\033[35mcreating docker networks\033[0m"
docker network create dome
docker network create main
echo -e "\033[35mcloning the specified repo\033[0m"

echo -e "\033[35mcloning proxy\033[0m"
clone_repo_branch $PROXY_RP $PROXY_BR proxy-repo proxy-system-dev || { echo -e "Docker clone failed."; exit 1; }

echo -e "\033[35mcloning charging\033[0m"
clone_repo_branch $CHARGING_RP  $CHARGING_BR charging-repo charging-system-dev || { echo -e "Docker clone failed."; exit 1; }

# 3. docker up and register app in idm

cd scorpiodb
docker compose up -d > /dev/null 2>&1
echo -e "\033[35mscorpio deployed\033[0m"
cd ..

cd api
export TM_VERSION
docker compose up -d > /dev/null 2>&1
echo -e "\033[35mtmforum api deployed\033[0m"
cd ..

wait_server http://localhost:8636/resourceCatalog resourceCatalog
wait_server http://localhost:8637/serviceCatalog serviceCatalog
wait_server http://localhost:8632/productSpecification productCatalog

cd idm-docker
docker compose up -d > /dev/null 2>&1
echo -e "\033[35midm server deployed\033[0m"
cd ..

wait_server http://localhost:3000/version idm

echo -e "\033[35mregistering app in idm ...\033[0m"
admin_token=$(curl -X POST \
     -H "Content-Type:application/json" \
     -d '{ "name": "admin@test.com",
         "password": "1234"
        }' \
     -i \
     http://localhost:3000/v1/auth/tokens | grep -i "X-Subject-Token:" | awk '{print $2}' | sed 's/[[:space:]]//g')

echo -e "\033[35midm admin token saved:\033[0m $admin_token"

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
     http://localhost:3000/v1/applications)

echo -e "\033[35mapp registering response\033[0m"
echo -e $app_json

CLIENT_ID=$(python3 auth_cred.py --attr application --key id --sjson "$app_json")
CLIENT_SECRET=$(python3 auth_cred.py --attr application --key secret --sjson "$app_json")
export CLIENT_ID
export CLIENT_SECRET
echo -e "\033[35mapp client id and secret saved!\033[0m"
echo -e "\033[35mclient_id: $CLIENT_ID\033[0m" 
echo -e "\033[35mclient_secret: $CLIENT_SECRET\033[0m"

echo -e "\033[35msetting seller role in idm\033[0m"
seller=$(curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json"\
     -d '
{
  "role": {
    "name": "seller"
  }
}' \
     http://localhost:3000/v1/applications/$CLIENT_ID/roles)
seller_id=$(python3 auth_cred.py --attr role --key id --sjson $seller)

echo -e "\033[35msetting customer role in idm\033[0m"
customer=$(curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json"\
     -d '
{
  "role": {
    "name": "customer"
  }
}' \
     http://localhost:3000/v1/applications/$CLIENT_ID/roles)
customer_id=$(python3 auth_cred.py --attr role --key id --sjson $customer)

echo -e "\033[35msetting admin role in idm\033[0m"
admin=$(curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json"\
     -d '
{
  "role": {
    "name": "admin"
  }
}' \
     http://localhost:3000/v1/applications/$CLIENT_ID/roles)
admin_id=$(python3 auth_cred.py --attr role --key id --sjson $admin)

echo -e "\033[35massigning roles to the user\033[0m"
echo -e "\033[35massigning seller role to the user\033[0m"
curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json" \
     http://localhost:3000/v1/applications/$CLIENT_ID/users/admin/roles/$seller_id

echo -e "\033[35massigning customer role to the user\033[0m"
curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json" \
     http://localhost:3000/v1/applications/$CLIENT_ID/users/admin/roles/$customer_id

echo -e "\033[35massigning admin role to the user\033[0m"
curl -X POST \
     -H "X-Auth-token: $admin_token" \
     -H "Content-Type: application/json" \
     http://localhost:3000/v1/applications/$CLIENT_ID/users/admin/roles/$admin_id


echo -e "\033[35mdeploying charging\033[0m"
cd charging-docker
docker compose up -d > /dev/null 2>&1 || { echo -e "Docker compose up failed."; exit 1; }
cd ..

echo -e "\033[35mdeploying proxy\033[0m"
cd proxy-docker
docker compose up -d > /dev/null 2>&1 || { echo -e "Docker compose up failed."; exit 1; }
cd ..

echo -e "\033[35mproxy and charging deployed\033[0m"

# 4. execute cloned dockers
echo -e "\033[35mexecuting dockers...\033[0m"

sleep 20

echo -e "\033[35mexecuting proxy...\033[0m"
docker exec -d proxy-docker-proxy-1 node server.js || { echo -e "Docker exec node proxy server failed."; exit 1; }
wait_server http://localhost:8004/version proxy

echo -e "\033[35mexecuting charging...\033[0m"
docker exec charging-docker-charging-1 bash -c "cd /business-ecosystem-charging-backend/src && python3 manage.py migrate" || { echo -e "Docker exec migrate failed."; exit 1; }
docker exec -d charging-docker-charging-1 bash -c "cd /business-ecosystem-charging-backend/src && python3 manage.py runserver 0.0.0.0:8006" || { echo -e "Docker exec run charging server failed."; exit 1; }
wait_server http://localhost:8004/service charging

echo -e "\033[35mBUILD FINISHED\033[0m"


# 5. run system test
echo -e "\033[35mrunning system test\033[0m"
cd src
python3 system_testing.py || { echo -e "system tests failed."; exit 1; }
cd ..
echo -e "\033[35msystem tests passed\033[0m"
# 6. docker down

# cd charging-docker
# docker compose down
# cd ..

# cd proxy-docker
# docker compose down
# cd ..
