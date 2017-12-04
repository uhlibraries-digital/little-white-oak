#!/usr/bin/env python2

# Update PM Ark Erc.where to AIP download link location
# UUID: cb2d2ba3-12e0-469c-9cc6-118aeaf48e4d
#
# @author Sean Watkins <slwatkins@uh.edu>

from __future__ import print_function
import ConfigParser
import sys
import logging
import re
import urllib, urllib2

import django
django.setup()

# archivematicaCommon
import archivematicaFunctions
from archivematicaCreateMETSMetadataCSV import parseMetadata
from custom_handlers import get_script_logger

def get_pm_ark(baseDirectory):
    metadata = parseMetadata(baseDirectory)
    if not metadata:
        return '';

    ark = ''
    for entry, data in metadata.items():
        for name, values in data.items():
            if name == 'dcterms.identifier' and ark == '':
                ark = get_pm_ark_in_values(values)

    return ark;

def get_pm_ark_in_values(values):
    for value in values:
        if re.match('ark:\/\d+\/pm.*', value):
            return value

    return ''

def updatePMArk(ark, uuid):
    client_config_path = '/etc/archivematica/MCPClient/clientConfig.conf'
    config = ConfigParser.SafeConfigParser()
    config.read(client_config_path)

    minter_baseurl = config.get('MCPClient', 'minterUpdateUrl')
    minter_key = config.get('MCPClient', 'minterApiKey')
    minter_ambaseurl = config.get('MCPClient', 'minterArchivematicaUrl')

    ercWhere = minter_ambaseurl + 'archival-storage/' + uuid + '/'
    req = urllib2.Request(minter_baseurl + ark, "where=" + urllib.quote_plus(ercWhere));
    req.add_header('api-key', minter_key)
    req.get_method = lambda: 'PUT'
    response = urllib2.urlopen(req)
    print("PM Ark Update Response:", response.read())


if __name__ == '__main__':
    logger = get_script_logger("archivematica.mcp.client.updatePmArkErcWhere")

    ark = get_pm_ark(sys.argv[1])
    if ark == '':
        print("No PM Ark to update. Move along, nothing to see here.")
        sys.exit(0)

    print("Found PM Ark:", ark)

    updatePMArk(ark, sys.argv[2])
