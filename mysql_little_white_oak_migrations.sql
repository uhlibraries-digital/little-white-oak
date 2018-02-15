# Installs updatePmArkErcWhere Task into MicroServiceChainLinks

SET @UpdatePmArkSTC = 'cb2d2ba3-12e0-469c-9cc6-118aeaf48e4d';
SET @UpdatePmArkTC = '113dc1ed-2495-465a-b3e6-de86fd9fc952';
SET @UpdatePMArkMCL = '93ab3b4b-57d3-41b1-8d33-f380c248eebd';
SET @UpdatePMArkMCLEC = 'b14b5bad-a46c-4d8e-9c45-ef5a40ad291c';

SET @PostPmArkSTC = '16f12b79-7604-4ea3-b431-6b1797a7d588';
SET @PostPmArkTC = 'd558cac4-f2d5-4313-9dc3-eec6d8644ee0';
SET @PostPmArkMCL = '760f721a-7a92-4566-8ab1-dd001038854d';
SET @PostPmArkMCLEC = '274629b9-b39f-458c-a9eb-36461040f1c8';

SET @FailedMCL = '7d728c39-395f-4892-8193-92f086c0546f';

-- Insert the post pm ark to ArchivesSpace task
INSERT INTO StandardTasksConfigs (pk, execute, arguments) VALUES (@PostPmArkSTC, 'postPmArkToArchivesSpace_v0.0', '"%SIPDirectory%"');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES (@PostPmArkTC, '36b2e239-4a57-4aa5-8ebc-7a29139baca6', @PostPmArkSTC, 'Post PM Ark to ArchivesSpace');

INSERT INTO MicroServiceChainLinks (pk, microserviceGroup, currentTask, defaultExitMessage, defaultNextChainLink) VALUES (@PostPmArkMCL, 'Update PM Ark', @PostPmArkTC, 'Failed', @FailedMCL);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, exitMessage, nextMicroServiceChainLink) VALUES (@PostPmArkMCLEC, @PostPmArkMCL, 0, 'Completed successfully', 'f1e286f9-4ec7-4e19-820c-dae7b8ea7d09');

-- Insert the update pm ark task
INSERT INTO StandardTasksConfigs (pk, execute, arguments) VALUES (@UpdatePmArkSTC, 'updatePmArkErcWhere_v0.0', '"%SIPDirectory%" "%SIPUUID%"');
INSERT INTO TasksConfigs (pk, taskType, taskTypePKReference, description) VALUES (@UpdatePmArkTC, '36b2e239-4a57-4aa5-8ebc-7a29139baca6', @UpdatePmArkSTC, 'Update PM Ark erc.where');

-- Update to inject task into MicroServiceChainLinks
INSERT INTO MicroServiceChainLinks (pk, microserviceGroup, currentTask, defaultExitMessage, defaultNextChainLink) VALUES (@UpdatePMArkMCL, 'Update PM Ark', @UpdatePmArkTC, 'Failed', @FailedMCL);
INSERT INTO MicroServiceChainLinksExitCodes (pk, microServiceChainLink, exitCode, exitMessage, nextMicroServiceChainLink) VALUES (@UpdatePMArkMCLEC, @UpdatePMArkMCL, 0, 'Completed successfully', @PostPmArkMCL);
UPDATE MicroServiceChainLinksExitCodes SET nextMicroServiceChainLink = @UpdatePMArkMCL WHERE pk = '4d703bf8-12ce-4fe7-9ddc-4dac274d8424';
