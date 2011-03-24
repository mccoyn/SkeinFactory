"""
This page is in the table of contents.
Meta is a script to access the plugins which handle meta information.

"""

#from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_meta


__author__ = 'Enrique Perez (perez_enrique@yahoo.com)'
__date__ = '$Date: 2008/21/04 $'
__license__ = 'GPL 3.0'


def getNewPlugin():
	return MetaPlugin()

class MetaPlugin (settings.Plugin):
	def getPluginName(self):
		return 'meta'

	def addToMenu( self, master, menu, repository, window ):
		"Add a tool plugin menu."
		settings.addPluginsParentToMenu( skeinforge_meta.getPluginsDirectoryPath(), menu, __file__, skeinforge_meta.getPluginFileNames() )

	def getNewRepository(self):
		"Get the repository constructor."
		return skeinforge_meta.MetaRepository()


def main():
	"Display the meta dialog."
	settings.startMainLoopFromConstructor( MetaPlugin.getNewRepository() )

if __name__ == "__main__":
	main()
