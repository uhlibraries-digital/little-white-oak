#!/usr/bin/env python2

# Post PM Ark to ArchivesSpace
# UUID: 16f12b79-7604-4ea3-b431-6b1797a7d588
#
# @author Sean Watkins <slwatkins@uh.edu>

from __future__ import print_function
import ConfigParser
import sys
import logging
import re
import urllib, urllib2
import json
import uuid

import django
django.setup()

# archivematicaCommon
import archivematicaFunctions
from archivematicaCreateMETSMetadataCSV import parseMetadata
from custom_handlers import get_script_logger

def get_pm_ark_and_aspace_uri(baseDirectory):
    metadata = parseMetadata(baseDirectory)
    if not metadata:
        return '';

    ark = ''
    uri = ''
    title = ''
    for entry, data in metadata.items():
        for name, values in data.items():
            if name == 'dcterms.identifier' and ark == '':
                ark = get_pm_ark_in_values(values)
            if name == 'uhlib.aSpaceUri' and uri == '':
                uri = values[0]
            if name == 'dcterms.title' and title == '':
                title = values[0]

    return {'ark': ark, 'uri': uri, 'title': title}

def get_pm_ark_in_values(values):
    for value in values:
        if re.match('ark:\/\d+\/pm.*', value):
            return value

    return ''

def post_pm_ark(data):

    new_digital_object = {
        "jsonmodel_type": "digital_object",
        "digital_object_id": str(uuid.uuid4()),
        "external_ids": [],
        "subjects": [],
        "linked_events": [],
        "extends": [],
        "dates": [],
        "external_documents": [],
        "rights_statements": [],
        "linked_agents": [],
        "file_versions": [
            {
                "jsonmodel_type": "file_version",
                "is_representative": False,
                "file_uri": minter_base + data['ark'],
                "use_statement": "",
                "xlink_actuate_attribute": "",
                "xlink_show_attribute": "",
                "file_format_name": "",
                "file_format_version": "",
                "checksum": "",
                "checksum_method": ""

            }
        ],
        "restrictions": False,
        "notes": [],
        "linked_instances": [],
        "title": data['title'] + " (Preservation)",
        "language": ""
    }
    archival_object = aspace_request(data['uri'])

    # Need to check if the archival object already has a PM Ark
    if has_pm_ark(archival_object['instances'], data['ark']):
        print("Archival Object already has a PM Ark of " + data['ark'])
        return

    response_do = aspace_request(archival_object['repository']['ref'] + '/digital_objects', json.dumps(new_digital_object))
    new_instance = {
        "jsonmodel_type": "instance",
        "digital_object": {
            "ref": response_do['uri']
        },
        "instance_type": "digital_object",
        "is_representative": False
    }

    archival_object['instances'].append(new_instance)
    changed_object = {
        "jsonmodel_type": "archival_object",
        "lock_version": archival_object['lock_version'],
        "external_ids": archival_object['external_ids'],
        "subjects": archival_object['subjects'],
        "linked_events": archival_object['linked_events'],
        "extents": archival_object['extents'],
        "dates": archival_object['dates'],
        "external_documents": archival_object['external_documents'],
        "rights_statements": archival_object['rights_statements'],
        "linked_agents": archival_object['linked_agents'],
        "restrictions_apply": archival_object['restrictions_apply'],
        "ancestors": archival_object['ancestors'],
        "instances": archival_object['instances'],
        "notes": archival_object['notes'],
        "ref_id": archival_object['ref_id'],
        "level": archival_object['level'],
        "title": archival_object['title'],
        "resource": archival_object['resource']
    }

    response = aspace_request(data['uri'], json.dumps(changed_object))



def has_pm_ark(instances, ark):
    ark = ark.replace('/', '\/')
    for instance in instances:
        if instance['instance_type'] == 'digital_object':
            do = aspace_request(instance['digital_object']['ref'])
            for do_file in do['file_versions']:
                if re.match('^.*' + ark + '$', do_file['file_uri']):
                    return True
    return False


def get_aspace_session():
    url = aspace_endpoint + '/users/' + aspace_username + '/login'
    req = urllib2.Request(url, "password=" + urllib.quote_plus(aspace_password))
    req.add_header("Content-Type",'application/x-www-form-urlencoded')
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    data_response = response.read()
    data = json.loads(data_response)

    if data['session'] == '':
        print("Failed to log into ArchivesSpace: ",data,file=sys.stderr)
        sys.exit(1)

    return data['session']

def aspace_request(uri, data=None):
    url = aspace_endpoint + uri

    req = urllib2.Request(url, data)
    req.add_header('X-ArchivesSpace-Session', session)
    response = urllib2.urlopen(req)

    return json.loads(response.read())


if __name__ == '__main__':
    logger = get_script_logger("archivematica.mcp.client.postPmArkToArchivesSpace")

    data = get_pm_ark_and_aspace_uri(sys.argv[1])
    if data == '':
        print("Why do I bother since there is no metadata.csv to look at")
        sys.exit(0)
    if data['ark'] == '':
        print("No PM Ark to post. Move along, nothing to see here.")
        sys.exit(0)
    if data['uri'] == '':
        print("No ArchivesSpace uri found. Move along, nothing to see here")
        sys.exit(0)

    print("Found PM Ark:", data['ark'])
    print("Found ASpace Uri:", data['uri'])

    client_config_path = '/etc/archivematica/MCPClient/clientConfig.conf'
    config = ConfigParser.SafeConfigParser()
    config.read(client_config_path)

    aspace_endpoint = config.get('MCPClient', 'aSpaceApiEndpoint')
    aspace_username = config.get('MCPClient', 'aSpaceUsername')
    aspace_password = config.get('MCPClient', 'aSpacePassword')
    minter_base     = config.get('MCPClient', 'minterBaseUrl')

    session = get_aspace_session()
    post_pm_ark(data)
