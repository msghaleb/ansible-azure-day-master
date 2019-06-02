# Azure Day
### Introduction
This repo is created to automate the user account creation for an Azure Day Event as well as creating on demand jumphosts.

#Create the Project:
tower-cli project create -n "azure day master" -d "This repo is for user creation and jumphost creation" --scm-type git --scm-url "https://github.com/msghaleb/ansible-azure-day-master.git" --scm-clean true --organization Default

#Create Credentials:
- Cloud creds
- .vpass

#create inventory
vars:
ansible_winrm_transport: basic 
ansible_winrm_operation_timeout_sec: 60 
ansible_winrm_read_timeout_sec: 70 
ansible_winrm_server_cert_validation: ignore

groups:
[azure-jumphosts]

[azure_day_users]