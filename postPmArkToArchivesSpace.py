#!/usr/bin/env python2

# Post PM Ark to ArchivesSpace
# UUID: 16f12b79-7604-4ea3-b431-6b1797a7d588
#
# @author Sean Watkins <slwatkins@uh.edu>

import ConfigParser
import sys
import re
import urllib, urllib2
import json
import uuid

import django
django.setup()

# archivematicaCommon
import archivematicaFunctions
from archivematicaCreateMETSMetadataCSV import parseMetadata

aspace_endpoint = ''
aspace_username = ''
aspace_password = ''
minter_base     = ''
session         = ''

def get_pm_ark_and_aspace_uri(job, baseDirectory):
    metadata = parseMetadata(job, baseDirectory, {})
    if not metadata:
        return ''

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

def post_pm_ark(job, data):
    global minter_base

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
                "checksum_method": "",
                "publish": False
            }
        ],
        "restrictions": False,
        "notes": [],
        "linked_instances": [],
        "title": data['title'] + " (Preservation)",
        "language": "",
        "publish": False
    }
    archival_object = aspace_request(data['uri'])

    # Need to check if the archival object already has a PM Ark
    if has_pm_ark(archival_object['instances'], data['ark']):
        job.pyprint("Archival Object already has a PM Ark of {}".format(data['ark']))
        return 0

    try:
        response_do = aspace_request(archival_object['repository']['ref'] + '/digital_objects', json.dumps(new_digital_object))
    except UnicodeDecodeError:
        job.pyprint("Unable to post digital object. You have non-utf8 characters in you metadata.csv file: {}".format(new_digital_object),file=sys.stderr)
        return 1
    except:
        job.pyprint ("Unable to post digital object",file=sys.stderr)
        return 1

    new_instance = {
        "jsonmodel_type": "instance",
        "digital_object": {
            "ref": response_do['uri']
        },
        "instance_type": "digital_object",
        "is_representative": False
    }

    archival_object['instances'].append(new_instance)

    response = aspace_request(data['uri'], json.dumps(archival_object))

    return 0


def has_pm_ark(instances, ark):
    ark = ark.replace('/', '\/')
    for instance in instances:
        if instance['instance_type'] == 'digital_object':
            do = aspace_request(instance['digital_object']['ref'])
            for do_file in do['file_versions']:
                if re.match('^.*' + ark + '$', do_file['file_uri']):
                    return True
    return False


def get_aspace_session(job):
    global aspace_endpoint, aspace_username, aspace_password

    url = aspace_endpoint + '/users/' + aspace_username + '/login'
    req = urllib2.Request(url, "password=" + urllib.quote_plus(aspace_password))
    req.add_header("Content-Type",'application/x-www-form-urlencoded')
    req.get_method = lambda: 'POST'
    response = urllib2.urlopen(req)
    data_response = response.read()
    data = json.loads(data_response)

    if data['session'] == '':
        job.pyprint("Failed to log into ArchivesSpace: {}".format(data),file=sys.stderr)
        return ''

    return data['session']

def aspace_request(uri, data=None):
    global aspace_endpoint, session

    url = aspace_endpoint + uri

    req = urllib2.Request(url, data)
    req.add_header('X-ArchivesSpace-Session', session)
    response = urllib2.urlopen(req)

    return json.loads(response.read())


def post_aspace(job):
    global aspace_endpoint, aspace_username, aspace_password, minter_base, session

    baseDirectory = job.args[1]

    data = get_pm_ark_and_aspace_uri(job, baseDirectory)
    if data == '':
        job.pyprint("Why do I bother since there is no metadata.csv to look at")
        return 0
    if data['ark'] == '':
        job.pyprint("No PM Ark to post. Move along, nothing to see here.")
        return 0
    if data['uri'] == '':
        job.pyprint("No ArchivesSpace uri found. Move along, nothing to see here")
        return 0

    job.pyprint("Found PM Ark: {}".format(data['ark']))
    job.pyprint("Found ASpace Uri: {}".format(data['uri']))

    client_config_path = '/etc/archivematica/MCPClient/clientConfig.conf'
    config = ConfigParser.SafeConfigParser()
    config.read(client_config_path)

    aspace_endpoint = config.get('aspace', 'api_endpoint')
    aspace_username = config.get('aspace', 'username')
    aspace_password = config.get('aspace', 'password')
    minter_base     = config.get('minter', 'base_url')

    session = get_aspace_session(job)
    if session == '':
        return 1

    return_status = post_pm_ark(job, data)

    return return_status


def call(jobs):
    for job in jobs:
        with job.JobContext():
            job.set_status(post_aspace(job))