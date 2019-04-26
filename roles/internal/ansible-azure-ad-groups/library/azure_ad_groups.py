#!/usr/bin/python
# -*- coding: utf-8 -*-
__version__ = "1.0.0"
DOCUMENTATION = '''
---
module: ansible-azure-ad-groups
short_description: Azure role to manage AD groups
description:
     - Allows for the management of Azure AD groups.
version_added: "1.0"
options:
  group_id:
    description:
      - The target group guid
    required: true
    default: null

  user_name:
    description:
      - The user name to be added. (without the domain part)
    required: true
    default: null

  client_id:
    description:
      - Azure clientID. If not set then the value of the AZURE_CLIENT_ID environment variable is used.
    required: false
    default: null
    aliases: [ 'azure_client_id', 'client_id' ]

  client_secret:
    description:
      - Azure Client secret key. If not set then the value of the AZURE_CLIENT_SECRET environment variable is used.
    required: false
    default: null
    aliases: [ 'azure_client_secret', 'client_secret' ]

  tenant_domain:
    description:
      - This is your tenant domain name, usually something.onmicrosoft.com (e.g. AnsibleDomain.onmicrosoft.com)
    required: True
    default: null

'''.format(__version__)

EXAMPLES = '''
# Basic user creation example
tasks:
- name: Add a user to a group
  azure_ad_groups:
    group_id       : "b4bda672-1fba-4711-8fb1-5383c40b2c14"
    user_name      : "username"
    tenant_domain  : "AnsibleDomain.onmicrosoft.com"
    client_id      : "6359f1g62-6543-6789-124f-398763x98112"
    client_secret  : "HhCDbhsjkuHGiNhe+RE4aQsdjjrdof8cSd/q8F/iEDhx="

'''


class AzureAdGroups():
    def __init__(self, module):
        self.module = module
        self.group_id = self.module.params["group_id"]
        self.user_name = self.module.params["user_name"]
        self.user_id = None
        self.tenant_domain = self.module.params["tenant_domain"]
        self.client_id = self.module.params["client_id"]
        self.client_secret = self.module.params["client_secret"]
        self.graph_url = self.module.params["graph_url"]
        self.login_url  = self.module.params["login_url"]
        if not self.graph_url:
            self.graph_url = "https://graph.windows.net/{}".format(self.tenant_domain)
        if not self.login_url:
            self.login_url = "https://login.windows.net/{}/oauth2/token?api-version=1.0".format(self.tenant_domain)

        # Geting azure cred from ENV if not defined
        if not self.client_id:
            if 'azure_client_id' in os.environ:
                self.client_id = os.environ['azure_client_id']
            elif 'AZURE_CLIENT_ID' in os.environ:
                self.client_id = os.environ['AZURE_CLIENT_ID']
            elif 'client_id' in os.environ:
                self.client_id = os.environ['client_id']
            elif 'CLIENT_ID' in os.environ:
                self.client_id = os.environ['CLIENT_ID']
            else:
                # in case client_id came in as empty string
                self.module.fail_json(msg="Client ID is not defined in module arguments or environment.")

        if not self.client_secret:
            if 'azure_client_secret' in os.environ:
                self.client_secret = os.environ['azure_client_secret']
            elif 'AZURE_CLIENT_SECRET' in os.environ:
                self.client_secret = os.environ['AZURE_CLIENT_SECRET']
            elif 'client_secret' in os.environ:
                self.client_secret = os.environ['client_secret']
            elif 'CLIENT_SECRET' in os.environ:
                self.client_secret = os.environ['CLIENT_SECRET']
            else:
                # in case secret_key came in as empty string
                self.module.fail_json(msg="Client Secret is not defined in module arguments or environment.")
        self.headers = None
        self.data = None
        self.azure_version = "api-version=1.6"

    # TODO: might not be needed
    def convert(self, data):
        if isinstance(data, basestring):
            return str(data)
        elif isinstance(data, collections.Mapping):
            return dict(map(self.convert, data.iteritems()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.convert, data))
        else:
            return data

    def login(self):
        headers = { 'User-Agent': 'ansible-azure-0.0.1', 'Connection': 'keep-alive', 'Content-Type': 'application/x-www-form-urlencoded' }
        payload = { 'grant_type': 'client_credentials', 'client_id': self.client_id, 'client_secret': self.client_secret }
        payload = urllib.urlencode(payload)

        try:
            r = open_url(self.login_url, method="post", headers=headers ,data=payload)
        except urllib2.HTTPError, err:
            response_code = err.getcode()
            response_msg = err.read()
            response_json = json.loads(response_msg)
            self.module.fail_json(msg="Failed to login error code = '{}' and message = {}".format(response_code, response_msg))

        response_msg = r.read()
        # TODO: Should try and catch if failed to seriolize to json
        token_response = json.loads(response_msg)
        token = token_response.get("access_token", False)
        if not token:
            self.module.fail_json(msg="Failed to extract token type from reply")
        token_type = token_response.get("token_type", 'Bearer')
        self.headers = { 'Authorization' : '{} {}'.format(token_type, token),
                         'Accept' : 'application/json', "content-type": "application/json" }

    def get_user_id(self):
        # https://msdn.microsoft.com/en-us/Library/Azure/Ad/Graph/api/users-operations
        #self.user_id_login()
        #print self.user_principal_name, self.tenant_domain
        #exit(1)
        url = "https://graph.windows.net/{}/users/{}%40{}/objectId?api-version=1.6".format(self.tenant_domain, self.user_name, self.tenant_domain)
        #print url
        #exit(1)
        try:
            r = open_url(url, method="get", headers=self.headers) #,data=payload)
        except urllib2.HTTPError, err:
            response_code = err.getcode()
            response_msg = err.read()
            response_json = json.loads(response_msg)
            if response_json.get("odata.error", False) and "Insufficient privileges" in response_json.get("odata.error").get("message",{}).get("value"):
                self.module.exit_json(msg="You have to add this Service Principal to the \"User Account Administrator Role\" this can be done using Powershell.", changed=False)
            else:
                error_msg = response_json.get("odata.error").get("message")
                self.module.fail_json(msg="Error happend while trying to get the user object id. Error code='{}' msg='{}'".format(response_code, error_msg))
        user_ObjectId = json.loads(r.read())
        user_ObjectId = user_ObjectId.get("value")
        #print user_ObjectId
        return user_ObjectId
        #Print r
        #self.module.exit_json(msg="User ID retrived.", changed=True)

    def add_user_to_group(self):
        # https://msdn.microsoft.com/en-us/Library/Azure/Ad/Graph/api/users-operations#BasicoperationsonusersCreateauser
        self.login()
        self.user_id = self.get_user_id()
        payload = { 'url': 'https://graph.windows.net/{}/directoryObjects/{}'.format(self.tenant_domain, self.user_id)  }
        # convert payload to json
        payload = json.dumps(payload)
        url = self.graph_url + "/groups/{}/$links/members?{}".format(self.group_id, self.azure_version)
        try:
            r = open_url(url, method="post", headers=self.headers ,data=payload)
        except urllib2.HTTPError, err:
            response_code = err.getcode()
            response_msg = err.read()
            response_json = json.loads(response_msg)
            #print response_json
            if response_json.get("odata.error", False) and "already exist" in response_json.get("odata.error").get("message",{}).get("value"):
                self.module.exit_json(msg="The User is already a member of this group", changed=False)
            else:
                error_msg = response_json.get("odata.error").get("message")
                self.module.fail_json(msg="Error happend while trying to create user. Error code='{}' msg='{}'".format(response_code, error_msg))

        self.module.exit_json(msg="The user has been added to the group.", changed=True)

    def main(self):

            self.add_user_to_group()

def main():
    module = AnsibleModule(
        argument_spec=dict(
            group_id=dict(default=None, type="str", required=True),
            user_name=dict(default=None, type="str", required=True),
            tenant_domain = dict(default=None, type="str", required=True),
            client_id = dict(default=None, alias="azure_client_id", type="str", no_log=True),
            client_secret = dict(default=None, alias="azure_client_secret", type="str", no_log=True),
            graph_url = dict(default=None, type="str"),
            login_url  = dict(default=None, type="str"),
        ),
        #mutually_exclusive=[['ip', 'mask']],
        #required_together=[['ip', 'mask']],
        #required_one_of=[['ip', 'mask']],
        supports_check_mode=False
    )

    AzureAdGroups(module).main()

import collections # might not be needed
import json
import urllib
import urllib2

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *
main()
