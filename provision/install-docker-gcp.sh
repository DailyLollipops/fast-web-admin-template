#!/bin/bash

# Variables
MOUNT_POINT="/mnt/disk"
DOCKER_DATA_ROOT="$MOUNT_POINT/docker"

# Step 1: Format and mount the existing disk
echo "Mounting the existing disk..."
# Replace /dev/sdb with your actual disk identifier
sudo mkfs.ext4 /dev/sdb  # Only run if the disk is unformatted
sudo mkdir -p $MOUNT_POINT
sudo mount /dev/sdb $MOUNT_POINT

# Make the mount persistent
echo "/dev/sdb $MOUNT_POINT ext4 defaults 0 2" | sudo tee -a /etc/fstab

# Step 2: Install Docker
echo "Installing Docker..."
sudo apt-get update
sudo apt-get install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the Docker repository
echo "Adding Docker repository..."
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

# Install Docker
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Step 3: Change Docker default storage location
echo "Changing Docker's default storage location..."
sudo systemctl stop docker
sudo mkdir -p $DOCKER_DATA_ROOT
sudo rsync -aP /var/lib/docker/ $DOCKER_DATA_ROOT/
sudo rm -rf /var/lib/docker
echo '{"data-root": "'"$DOCKER_DATA_ROOT"'"}' | sudo tee /etc/docker/daemon.json
sudo systemctl start docker

# Verification
echo "Docker installation and configuration complete."
echo "Docker root dir: $(docker info | grep 'Docker Root Dir')"
