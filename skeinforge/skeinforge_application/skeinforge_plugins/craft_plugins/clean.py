"""
This page is in the table of contents.
Hop is a script to raise the extruder when it is not extruding.

The hop manual page is at:
http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Hop

==Operation==
The default 'Activate Hop' checkbox is off.  It is off because Vik and Nophead found better results without hopping.  When it is on, the functions described below will work, when it is off, the functions will not be called.

==Settings==
===Hop Over Layer Thickness===
Default is one.

Defines the ratio of the hop height over the layer thickness, this is the most important hop setting.

===Minimum Hop Angle===
Default is 20 degrees.

Defines the minimum angle that the path of the extruder will be raised.  An angle of ninety means that the extruder will go straight up as soon as it is not extruding and a low angle means the extruder path will gradually rise to the hop height.

==Examples==
The following examples hop the file Screw Holder Bottom.stl.  The examples are run in a terminal in the folder which contains Screw Holder Bottom.stl and hop.py.


> python clean.py
This brings up the clean dialog.


> python clean.py Screw Holder Bottom.stl
The clean tool is parsing the file:
Screw Holder Bottom.stl
..
The clean tool has created the file:
.. Screw Holder Bottom_clean.gcode

"""

#from __future__ import absolute_import
#Init has to be imported first because it has code to workaround the python bug where relative imports don't work if the module is imported as a main module.
import __init__

from fabmetheus_utilities import euclidean
from fabmetheus_utilities import gcodec
from fabmetheus_utilities.fabmetheus_tools import fabmetheus_interpret
from fabmetheus_utilities import settings
from skeinforge_application.skeinforge_utilities import skeinforge_craft
from skeinforge_application.skeinforge_utilities import skeinforge_polyfile
from skeinforge_application.skeinforge_utilities import skeinforge_profile
import math
import sys


__author__ = "Nick McCoy (mccoyn@gmail.com)"
__date__ = "$Date: 2010/09/20 $"
__license__ = "GPL 3.0"


def getCraftedText( fileName, text, cleanRepository = None ):
	"Clean a gcode linear move text."
	return getCraftedTextFromText( gcodec.getTextIfEmpty( fileName, text ), cleanRepository )

def getCraftedTextFromText( gcodeText, cleanRepository = None ):
	"Clean a gcode linear move text."
	if gcodec.isProcedureDoneOrFileIsEmpty( gcodeText, 'clean'):
		return gcodeText
	if cleanRepository == None:
		cleanRepository = settings.getReadRepository( CleanRepository() )
	if not cleanRepository.activateClean.value:
		return gcodeText
	return CleanSkein().getCraftedGcode( gcodeText, cleanRepository )

def getNewRepository():
	"Get the repository constructor."
	return CleanRepository()

def writeOutput( fileName = ''):
	"Clean a gcode linear move file.  Chain clean the gcode if it is not already cleaned. If no fileName is specified, clean the first unmodified gcode file in this folder."
	fileName = fabmetheus_interpret.getFirstTranslatorFileNameUnmodified( fileName )
	if fileName != '':
		skeinforge_craft.writeChainTextWithNounMessage( fileName, 'clean')


class CleanRepository:
	"A class to handle the clean settings."
	def __init__( self ):
		"Set the default settings, execute title & settings fileName."
		skeinforge_profile.addListsToCraftTypeRepository('skeinforge_application.skeinforge_plugins.craft_plugins.clean.html', self )
		self.fileNameInput = settings.FileNameInput().getFromFileName( fabmetheus_interpret.getGNUTranslatorGcodeFileTypeTuples(), 'Open File for Clean', self, '')
		self.openWikiManualHelpPage = settings.HelpPage().getOpenFromAbsolute('http://www.bitsfrombytes.com/wiki/index.php?title=Skeinforge_Clean')
		self.activateClean = settings.BooleanSetting().getFromValue('Activate Clean', self, False )
		self.coolDownTemperature = settings.FloatSpin().getFromValue( 0.0, 'Cool Down Temperature (Celcius):', self, 260.0, 90.0)
		self.timeBetweenCleanings = settings.FloatSpin().getFromValue( 0.0, 'Time Between Cleanings (Minutes):',  self, 5000, 30)
		self.restartExtruderDistance = settings.FloatSpin().getFromValue( 0.0, 'Restart Extruder Distance (mm):', self, 100.0, 0.0 )
		self.fenceWidth = settings.FloatSpin().getFromValue( 0.0, 'Fence Width Over Thread Width:', self, 10, 4)
		self.fenceSize = settings.FloatSpin().getFromValue( 0.0, 'Fence Length (mm):', self, 200, 50)
		self.fenceMargin = settings.FloatSpin().getFromValue( 0.0, 'Fence Margin (mm):', self, 200, 10)
		self.executeTitle = 'Clean'

	def execute( self ):
		"Clean button has been clicked."
		fileNames = skeinforge_polyfile.getFileOrDirectoryTypesUnmodifiedGcode( self.fileNameInput.value, fabmetheus_interpret.getImportPluginFileNames(), self.fileNameInput.wasCancelled )
		for fileName in fileNames:
			writeOutput( fileName )


class CleanSkein:
	"A class to self-clean an extruder."
	def __init__( self ):
		self.distanceFeedRate = gcodec.DistanceFeedRate()
		self.startLineIndex = None
		self.endLineIndex = None
		self.lines = None
		self.feedRateMinute = 1000
		self.oldLocation = None
		self.operatingTemperature = 25

	def getCraftedGcode( self, gcodeText, cleanRepository ):
		"Parse gcode text and store the clean gcode."
		self.lines = gcodec.getTextLines(gcodeText)
		self.timeBetweenCleanings = cleanRepository.timeBetweenCleanings.value
		self.coolDownTemperature = cleanRepository.coolDownTemperature.value
		self.fenceWidth = cleanRepository.fenceWidth.value
		self.fenceSize = cleanRepository.fenceSize.value
		self.restartExtruderDistance = cleanRepository.restartExtruderDistance.value
		self.timeToNextCleaning = self.timeBetweenCleanings
		self.parseInitialization( cleanRepository )
		for lineIndex in xrange( self.startLineIndex, len( self.lines ) ):
			line = self.lines[ lineIndex ]
			self.parseLine(line)
		return self.distanceFeedRate.output.getvalue()

	def parseInitialization( self, cleanRepository ):
		"Parse gcode initialization and store the parameters."		
		self.startLineIndex = None
		for lineIndex in xrange( len( self.lines ) ):
			line = self.lines[ lineIndex ]
			splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
			firstWord = gcodec.getFirstWord( splitLine )
			self.distanceFeedRate.parseSplitLine( firstWord, splitLine )
			if firstWord == '(<layerThickness>':
				self.layerThickness = float(splitLine[1])
			if firstWord == '(<objectNextLayersTemperature>':
				self.operatingTemperature = float(splitLine[1])
			elif firstWord == '(<travelFeedRatePerSecond>':
				travelFeedRatePerSecond = float(splitLine[1])
				self.travelFeedRatePerMinute = travelFeedRatePerSecond * 60.0;
			elif firstWord == '(<operatingFeedRatePerSecond>':
				operatingFeedRatePerSecond = float (splitLine[1])
				self.operatingFeedRatePerMinute = operatingFeedRatePerSecond * 60.0
			elif firstWord == '(<perimeterWidth>':
				self.perimeterWidth = float (splitLine[1])
			elif firstWord == '(</extruderInitialization>)':
				self.distanceFeedRate.addLine('(<procedureDone> clean </procedureDone>)')
			elif firstWord == '(<extrusion>)':
				self.startLineIndex = lineIndex
			elif firstWord == '(</extrusion>)':
				self.endLineIndex = lineIndex
			if self.startLineIndex == None:
				self.distanceFeedRate.addLine(line)
		boundingRectangle = gcodec.BoundingRectangle().getFromGcodeLines( self.lines[self.startLineIndex : self.endLineIndex], cleanRepository.fenceMargin.value )
		self.fencePosition = boundingRectangle.cornerMinimum
		self.fenceZ = self.layerThickness / 2
		self.fenceThread = []
		ii = -self.fenceWidth
		while True:
			self.fenceThread += [self.fencePosition + complex(ii*self.perimeterWidth, self.fenceSize),
			                     self.fencePosition + complex(ii*self.perimeterWidth, ii*self.perimeterWidth),
			                     self.fencePosition + complex(self.fenceSize,         ii*self.perimeterWidth)]
			ii = ii + 1
			if ii <= 0:
				break;
			self.fenceThread += [self.fencePosition + complex(self.fenceSize,         ii*self.perimeterWidth),
			                     self.fencePosition + complex(ii*self.perimeterWidth, ii*self.perimeterWidth),
			                     self.fencePosition + complex(ii*self.perimeterWidth, self.fenceSize)]
			ii = ii + 1
			if ii <= 0:
				break;

	def parseLine( self, line ):
		"Parse a gcode line and add it to the stretch gcode."
		splitLine = gcodec.getSplitLineBeforeBracketSemicolon(line)
		if len( splitLine ) < 1:
			return
		firstWord = splitLine[0]
		if firstWord == 'G1':
			self.feedRateMinute = gcodec.getFeedRateMinute( self.feedRateMinute, splitLine )
			newLocation = gcodec.getLocationFromSplitLine( self.oldLocation, splitLine )
			if self.oldLocation != None:
				distance = self.oldLocation.distance(newLocation)
				self.timeToNextCleaning -= distance / self.feedRateMinute
			self.oldLocation = newLocation
		elif firstWord == 'M101':
			if (self.timeToNextCleaning <= 0.0):
				self.addSelfCleaning()
				self.timeToNextCleaning += self.timeBetweenCleanings
		elif (firstWord == 'M104') or (firstWord == 'M109'):
			self.operatingTemperature = float(gcodec.getStringFromCharacterSplitLine('S', splitLine))
		self.distanceFeedRate.addLine(line)
		
	def addSelfCleaning(self):
		"Move to the idle position, cycle the extruder temperature, build a fence to clean the extruder and move back."
		idlePosition = self.fencePosition + complex(-10, -10)
		self.distanceFeedRate.addParameter('M104', self.coolDownTemperature)
		self.distanceFeedRate.addGcodeMovementZWithFeedRate(self.travelFeedRatePerMinute, idlePosition, self.oldLocation.z)
		self.distanceFeedRate.addGcodeMovementZWithFeedRate(self.travelFeedRatePerMinute, idlePosition, self.fenceZ)
		self.distanceFeedRate.addParameter('M109', self.coolDownTemperature)
		self.distanceFeedRate.addParameter('M109', self.operatingTemperature)
		
		self.distanceFeedRate.addLine( 'M101' )
		self.distanceFeedRate.addGcodeMovementZWithFeedRate(self.travelFeedRatePerMinute, self.fenceThread[0], self.fenceZ)
		
		while self.fenceZ + self.layerThickness/2 < self.oldLocation.z:
			self.distanceFeedRate.addGcodeFromFeedRateThreadZ(self.operatingFeedRatePerMinute, self.fenceThread, self.fenceZ)
			self.fenceZ += self.layerThickness
		self.distanceFeedRate.addGcodeMovementZWithFeedRate(self.travelFeedRatePerMinute, self.oldLocation.dropAxis(2), self.oldLocation.z)
	

def main():
	"Display the clean dialog."
	if len( sys.argv ) > 1:
		writeOutput(' '.join( sys.argv[ 1 : ] ) )
	else:
		settings.startMainLoopFromConstructor( getNewRepository() )

if __name__ == "__main__":
	main()
