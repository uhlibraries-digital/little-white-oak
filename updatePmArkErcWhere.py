#!/usr/bin/env python2

# Update PM Ark Erc.where to AIP download link location
# UUID: cb2d2ba3-12e0-469c-9cc6-118aeaf48e4d
#
# @author Sean Watkins <slwatkins@uh.edu>

import sys
import re
import urllib, urllib2
import ConfigParser

import django
django.setup()

# archivematicaCommon
import archivematicaFunctions
from archivematicaCreateMETSMetadataCSV import parseMetadata

def get_pm_ark(job, baseDirectory):
    metadata = parseMetadata(job, baseDirectory, {})
    if not metadata:
        return ''

    ark = ''
    for entry, data in metadata.items():
        for name, values in data.items():
            if name == 'dcterms.identifier' and ark == '':
                ark = get_pm_ark_in_values(values)

    return ark

def get_pm_ark_in_values(values):
    for value in values:
        if re.match('ark:\/\d+\/pm.*', value):
            return value

    return ''

def updatePMArk(job, uuid, ark):
    client_config_path = '/etc/archivematica/clientConfig.conf'
    config = ConfigParser.SafeConfigParser()
    config.read(client_config_path)

    minter_baseurl = config.get('minter', 'update_url')
    minter_key = config.get('minter', 'api_key')
    minter_ambaseurl = config.get('minter', 'archivematica_url')

    ercWhere = minter_ambaseurl + 'archival-storage/' + uuid + '/'
    req = urllib2.Request(minter_baseurl + ark, "where=" + urllib.quote_plus(ercWhere))
    req.add_header('api-key', minter_key)
    req.get_method = lambda: 'PUT'
    response = urllib2.urlopen(req)
    job.pyprint("PM Ark Update Response: {}".format(response.read()))

def update_aspace(job):
    baseDirectory = job.args[1]
    uuid = job.args[2]

    ark = get_pm_ark(job, baseDirectory)
    if ark == '':
        job.pyprint("No PM Ark to update. Move along, nothing to see here.")
        return 0

    job.pyprint("Found PM Ark: {}".format(ark))
    updatePMArk(job, uuid, ark)

    return 0


def call(jobs):
    for job in jobs:
        with job.JobContext():
            job.set_status(update_aspace(job))
