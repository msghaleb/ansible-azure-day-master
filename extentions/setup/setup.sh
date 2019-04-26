#!/bin/bash
set -e

## You can do other stuff here like install test-kitchen or whatever
# echo Installing bundler
# sudo gem install bundler

## This is an example setup script that you would encapsulate the installation

# What version of ansible setup to use
SETUP_VERSION="master"

# Whats my path
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

## Array of versions to install

## 1. Install Ansible 2.1
ANSIBLE_VERSIONS[0]="2.1.5.0"
INSTALL_TYPE[0]="pip"
PYTHON_REQUIREMENTS[0]="$DIR/python_requirements.txt"

## 2. Install Ansible 2.2
ANSIBLE_VERSIONS[1]="2.2.3.0"
PYTHON_REQUIREMENTS[1]="$DIR/python_requirements.txt"
INSTALL_TYPE[1]="pip"

## 3. Install Ansible 2.3
ANSIBLE_VERSIONS[2]="2.3.0.0"
PYTHON_REQUIREMENTS[2]="$DIR/python_requirements.txt"
INSTALL_TYPE[2]="pip"

## 5. Install Ansible Devl
ANSIBLE_VERSIONS[3]="devel"
INSTALL_TYPE[3]="git"
PYTHON_REQUIREMENTS[3]="$DIR/python_requirements.txt"

# Make this the default for v1
ANSIBLE_V1_PATH="${ANSIBLE_VERSIONS[2]}"
# Make this default for v2
ANSIBLE_V2_PATH="${ANSIBLE_VERSIONS[1]}"
# Make this the default for development
ANSIBLE_DEV_PATH="${ANSIBLE_VERSIONS[3]}"


# Whats the system default version
ANSIBLE_DEFAULT_VERSION="${ANSIBLE_VERSIONS[2]}"


## Create a temp dir to download the setup script
filename=$( echo ${0} | sed  's|/||g' )
my_temp_dir="$(mktemp -dt ${filename}.XXXX)"
## Get setup script from gitub
curl -s https://raw.githubusercontent.com/AutomationWithAnsible/ansible-setup/$SETUP_VERSION/setup.sh -o $my_temp_dir/setup.sh
## Run the setup
. $my_temp_dir/setup.sh

# You can do other stuff here like install test-kitchen or whatever

exit #!/bin/bash
set -e
