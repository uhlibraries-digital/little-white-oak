# Little White Oak

A collection of Archivematica scripts to handle SIP ingests

## updatePmArkErcWhere.py

Updates a PM Ark erc.where in [Greens](https://github.com/uhlibraries-digital/greens) to the AIP download location.

### Installation

Copy `updatePmArkErcWhere.py` to `/usr/lib/archivematica/MCPClient/clientScripts`.

Run the `mysql_updatepmarkercwhere_migrations.sql` file into the Archivematica
database. Always make a backup of your databases.

```
# mysql -uroot MCP < mysql_updatepmarkercwhere_migrations.sql
```

Add the following line to `/usr/lib/archivematica/MCPClient/archivematicaClientModules` under `[supportedCommands]`. This list is in alphabetical order.

```
updatePmArkErcWhere_v0.0 = %clientScriptsDirectory%updatePmArkErcWhere.py
```

Add the following configuration options to your MCPClient config `/etc/archivematica/MCPClient/clientConfig.conf`

```
minterUpdateUrl = <Greens Ark api update url>
minterApiKey = <Greens API KEY>
minterArchivematicaUrl = <Archivematica base url>
```
