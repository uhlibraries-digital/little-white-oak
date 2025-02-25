#!/usr/bin/env python3

# Post PM Ark to ArchivesSpace
# UUID: 16f12b79-7604-4ea3-b431-6b1797a7d588
#
# @author Sean Watkins <slwatkins@uh.edu>

import os
import sys
import re
import urllib.request, urllib.error, urllib.parse
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
    do_uuid = ''
    for entry, data in metadata.items():
        for name, values in data.items():
            if name == 'dcterms.identifier' and ark == '':
                ark = get_pm_ark_in_values(values)
            if name == 'uhlib.aSpaceUri' and uri == '':
                uri = values[0]
            if name == 'dcterms.title' and title == '':
                title = values[0]
            if name == 'uhlib.doUuid' and do_uuid == '':
                do_uuid = values[0]

    return {'ark': ark, 'uri': uri, 'do_uuid': do_uuid, 'title': title}

def get_pm_ark_in_values(values):
    for value in values:
        if re.match('ark:\/\d+\/pm.*', value):
            return value

    return ''

def post_pm_ark(job, data):
    global minter_base

    archival_object = aspace_request(data['uri'])

    new_digital_object = False
    digital_object = get_digital_object(archival_object['instances'], data['do_uuid'])
    if digital_object == None:
        new_digital_object = True
        job.pyprint("Creating new digital object with UUID: {}".format(data['do_uuid']))
        digital_object = {
            "jsonmodel_type": "digital_object",
            "digital_object_id": data['do_uuid'],
            "external_ids": [],
            "subjects": [],
            "linked_events": [],
            "extends": [],
            "dates": [],
            "external_documents": [],
            "rights_statements": [],
            "linked_agents": [],
            "file_versions": [],
            "restrictions": False,
            "notes": [],
            "linked_instances": [],
            "title": data['title'],
            "language": "",
            "publish": True
        }
    else:
        job.pyprint("Using existing digital object with UUID: {}".format(data['do_uuid']))

    # Need to check if the archival object already has a PM Ark
    if has_pm_ark(digital_object['file_versions'], data['ark']):
        job.pyprint("Archival Object already has a PM Ark of {}".format(data['ark']))
        return 0
    
    digital_object['file_versions'].append({
        "jsonmodel_type": "file_version",
        "is_representative": False,
        "file_uri": minter_base + data['ark'],
        "use_statement": "Preservation",
        "xlink_actuate_attribute": "",
        "xlink_show_attribute": "",
        "file_format_name": "",
        "file_format_version": "",
        "checksum": "",
        "checksum_method": "",
        "publish": False
    })

    if new_digital_object:
        try:
            response_do = aspace_request(archival_object['repository']['ref'] + '/digital_objects', json.dumps(digital_object))
        except UnicodeDecodeError:
            job.pyprint("Unable to post digital object. You have non-utf8 characters in you metadata.csv file: {}".format(digital_object),file=sys.stderr)
            return 1
        except:
            job.pyprint ("Unable to post digital object, make sure it doesn't already exist elsewhere in ASpace",file=sys.stderr)
            return 1

        archival_object['instances'].append({
            "jsonmodel_type": "instance",
            "digital_object": {
                "ref": response_do['uri']
            },
            "instance_type": "digital_object",
            "is_representative": False
        })

        response = aspace_request(data['uri'], json.dumps(archival_object))
    else:
        try:
            job.pyprint("Updating digital object with UUID: {}".format(data['do_uuid']))
            response_do = aspace_request(digital_object['uri'], json.dumps(digital_object))
        except:
            job.pyprint("Unable to update digital object: {}".format(digital_object),file=sys.stderr)
            return 1

    return 0


def has_pm_ark(file_versions, ark):
    ark = ark.replace('/', '\/')
    for do_file in file_versions:
        if re.match('^.*' + ark + '$', do_file['file_uri']):
            return True

    return False

def get_digital_object(instances, uuid):
    for instance in instances:
        if instance['instance_type'] == 'digital_object':
            do = aspace_request(instance['digital_object']['ref'])
            if do['digital_object_id'] == uuid:
                return do
    
    return None

def get_aspace_session(job):
    global aspace_endpoint, aspace_username, aspace_password

    url = aspace_endpoint + '/users/' + aspace_username + '/login'
    req = urllib.request.Request(url, "password=" + urllib.parse.quote_plus(aspace_password))
    req.add_header("Content-Type",'application/x-www-form-urlencoded')
    req.get_method = lambda: 'POST'
    response = urllib.request.urlopen(req)
    data_response = response.read()
    data = json.loads(data_response)

    if data['session'] == '':
        job.pyprint("Failed to log into ArchivesSpace: {}".format(data),file=sys.stderr)
        return ''

    return data['session']

def aspace_request(uri, data=None):
    global aspace_endpoint, session

    url = aspace_endpoint + uri

    req = urllib.request.Request(url, data)
    req.add_header('X-ArchivesSpace-Session', session)
    response = urllib.request.urlopen(req)

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
    if data['do_uuid'] == '':
        job.pyprint("No ArchivesSpace digital object UUID. Move along, nothing to see here")
        return 0

    job.pyprint("Found PM Ark: {}".format(data['ark']))
    job.pyprint("Found ASpace Uri: {}".format(data['uri']))
    job.pyprint("Found ASpace digital object UUID: {}".format(data['do_uuid']))

    aspace_endpoint = os.environ.get('ASPACE_API_ENDPOINT')
    aspace_username = os.environ.get('ASPACE_USERNAME')
    aspace_password = os.environ.get('ASPACE_PASSWORD')
    minter_base     = os.environ.get('MINTER_BASE_URL')

    session = get_aspace_session(job)
    if session == '':
        return 1

    return_status = post_pm_ark(job, data)

    return return_status


def call(jobs):
    for job in jobs:
        with job.JobContext():
            job.set_status(post_aspace(job))
