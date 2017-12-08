# Little White Oak

A collection of Archivematica scripts to handle SIP ingests

## updatePmArkErcWhere.py

Updates a PM Ark erc.where in [Greens](https://github.com/uhlibraries-digital/greens) to the AIP download location.

The following fields must be given in the metadata.csv file found in the SIP transfer package:

| Field | Value |
| --- | --- |
| dcterms.identifier | PM Ark (ark:/1234/pm4899938) |

## postPmArkToArchivesSpace.py

Posts the PM Ark to a archival objects External Document in [ArchivesSpace](http://archivesspace.org/).

The following fields must be given in the metadata.csv file found in the SIP transfer package:

| Field | Value |
| --- | --- |
| dcterms.identifier | PM Ark (ark:/1234/pm4899938) |
| uhlib.aSpaceUri | ArchivesSpace archival object uri |

## Installation

Copy `updatePmArkErcWhere.py` and `postPmArkToArchivesSpace.py` to `/usr/lib/archivematica/MCPClient/clientScripts`.

Run the `mysql_little_white_oak_migrations.sql` file into the Archivematica
database. Always make a backup of your databases.

```
# mysql -uroot MCP < mysql_little_white_oak_migrations.sql
```

Add the following lines to `/usr/lib/archivematica/MCPClient/archivematicaClientModules` under `[supportedCommands]`. The `archivematicaClientModules` list is in alphabetical order.

```
postPmArkToArchivesSpace_v0.0 = %clientScriptsDirectory%postPmArkToArchivesSpace.py
updatePmArkErcWhere_v0.0 = %clientScriptsDirectory%updatePmArkErcWhere.py
```

Add the following configuration options to your MCPClient config `/etc/archivematica/MCPClient/clientConfig.conf`

```
minterBaseUrl = <Greens Base url>
minterUpdateUrl = <Greens Ark api update url>
minterApiKey = <Greens API KEY>
minterArchivematicaUrl = <Archivematica base url>
aSpaceApiEndpoint = <ArchivesSpace API Endpoint>
aSpaceUsername = <ArchivesSpace username>
aSpacePassword = <ArchivesSpace password>
```

Restart Archivematica to accept the changes
