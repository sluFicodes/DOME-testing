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

# 3. docker up  TODO: idm
cd charging-docker
docker compose up -d
cd ..

cd proxy-docker
docker compose up -d
cd ..


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
