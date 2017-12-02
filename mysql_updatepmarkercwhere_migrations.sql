# Installs updatePmArkErcWhere Task into MicroServiceChainLinks

SET @UpdatePmArkSTC = 'cb2d2ba3-12e0-469c-9cc6-118aeaf48e4d';
SET @UpdatePmArkTC = '113dc1ed-2495-465a-b3e6-de86fd9fc952';
SET @UpdatePMArkMCL = '93ab3b4b-57d3-41b1-8d33-f380c248eebd';
SET @UpdatePMArkMCLEC = 'b14b5bad-a46c-4d8e-9c45-ef5a40ad291c';

-- Insert the update pm ark task
INSERT INTO StandardTasksConfigs (pk, execute, arguments) VALUES (@UpdatePmArkSTC, 'updatePmArkErcWhere_v0.0', '"%SIPDirectory%" "%SIPUUID%"');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES (@UpdatePmArkTC, '36b2e239-4a57-4aa5-8ebc-7a29139baca6', @UpdatePmArkSTC, 'Update PM Ark erc.where');

-- Update to inject task into MicroServiceChainLinks
INSERT INTO MicroServiceChainLinks (pk, microserviceGroup, currentTask, defaultExitMessage, defaultNextChainLink) VALUES (@UpdatePMArkMCL, 'Update PM Ark', @UpdatePmArkTC, 'Failed', NULL);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, exitMessage, nextMicroServiceChainLink) VALUES (@UpdatePMArkMCLEC, @UpdatePMArkMCL, 0, 'Completed successfully', 'f1e286f9-4ec7-4e19-820c-dae7b8ea7d09');
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink = @UpdatePMArkMCL WHERE pk = '4d703bf8-12ce-4fe7-9ddc-4dac274d8424';
