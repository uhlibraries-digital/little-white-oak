# Little White Oak

A collection of Archivematica scripts to handle SIP ingests

## Requirements

Archivematica 1.17

## updatePmArkErcWhere.py

Updates a PM Ark erc.where in [Greens](https://github.com/uhlibraries-digital/greens) to the AIP download location.

The following fields must be given in the metadata.csv file found in the SIP transfer package:

| Field | Value |
| --- | --- |
| dcterms.identifier | PM Ark (ark:/1234/pm4899938) |

## postPmArkToArchivesSpace.py

Posts the PM Ark to a Digital Object that is attached to the archival object in [ArchivesSpace](http://archivesspace.org/).

The following fields must be given in the metadata.csv file found in the SIP transfer package:

| Field | Value |
| --- | --- |
| dcterms.identifier | PM Ark (ark:/1234/pm4899938) |
| uhlib.aSpaceUri | ArchivesSpace archival object uri |

## Installation

Copy `updatePmArkErcWhere.py` and `postPmArkToArchivesSpace.py` to `/usr/lib/archivematica/MCPClient/clientScripts`.

Patch `/usr/lib/archivematica/MCPServer/assets/workflow.json` with the following command:

`patch -b /usr/lib/archivematica/MCPServer/assets/workflow.json workflow.patch`

Add the following lines to `/usr/lib/archivematica/MCPClient/archivematicaClientModules` under `[supportedCommands]`:

```
postPmArkToArchivesSpace_v0.0 = postPmArkToArchivesSpace 
updatePmArkErcWhere_v0.0 = updatePmArkErcWhere

```

Add the following configuration options to your MCPClient config `/etc/archivematica/clientConfig.conf`:

```
[minter]
base_url = <Greens Base url>
update_url = <Greens Ark api update url>
api_key = <Greens API KEY>
archivematica_url = <Archivematica base url>

[aspace]
api_endpoint = <ArchivesSpace API Endpoint>
username = <ArchivesSpace username>
password = <ArchivesSpace password>
```

Restart Archivematica to accept the changes
