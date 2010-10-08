#!/usr/bin/python

import __init__

from skeinforge_application import skeinforge
from fabmetheus_utilities import settings

def forwardDeclartions():
	"Force some functions to be dynamic"
	mockRepository = settings.Repository()
	settings.addListsToRepository(None, None, mockRepository)
	settings.cancelRepository(mockRepository)
	settings.getArchiveText(mockRepository)
	settings.getDisplayedDialogFromConstructor(mockRepository)
	settings.getProfileBaseName(mockRepository)
	settings.getReadRepository(mockRepository)
	settings.readSettingsFromText(mockRepository, '')
	settings.saveRepository(mockRepository)
	settings.startMainLoopFromConstructor(mockRepository)
	settings.writeSettings(mockRepository)
	settings.writeSettingsPrintMessage(mockRepository)
	settings.StringSetting().getFromValueOnly('', mockRepository, '')
	settings.FileNameInput().getFromFileName([('','')], '', mockRepository, '')
	settings.GridVertical(0, 0).setExecutablesRepository(mockRepository)
	settings.HelpPage().setToNameRepository('', mockRepository)
	settings.HelpPage().getFromNameAfterHTTP('', '', mockRepository)
	settings.HelpPageRepository.__init__(settings.HelpPageRepository(), mockRepository)
	settings.LabelDisplay().getFromName('', mockRepository)
	settings.MenuButtonDisplay().getFromName('', mockRepository)
	settings.Radio().getFromRadio(None, '', mockRepository, False)
	settings.WindowPosition().getFromValue(mockRepository, '')
	settings.RepositoryDialog(mockRepository, None).addButtons(mockRepository, None)
	settings.RepositoryDialog.__init__(RepositoryDialog(), mockRepository, None)

def main():
	forwardDeclartions()
	skeinforge.main()

if __name__ == "__main__":
	main()
