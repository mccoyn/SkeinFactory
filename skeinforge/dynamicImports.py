#!/usr/bin/python

import __init__

from skeinforge_application.skeinforge_plugins import craft
from skeinforge_application.skeinforge_plugins import analyze
from skeinforge_application.skeinforge_plugins import help
from skeinforge_application.skeinforge_plugins import meta
from skeinforge_application.skeinforge_plugins import profile
from skeinforge_application.skeinforge_plugins.meta_plugins import description
from skeinforge_application.skeinforge_plugins.meta_plugins import polyfile
from skeinforge_application.skeinforge_plugins.profile_plugins import cutting
from skeinforge_application.skeinforge_plugins.profile_plugins import extrusion
from skeinforge_application.skeinforge_plugins.profile_plugins import milling
from skeinforge_application.skeinforge_plugins.profile_plugins import winding
from skeinforge_application.skeinforge_plugins.craft_plugins import carve
from skeinforge_application.skeinforge_plugins.craft_plugins import chamber
from skeinforge_application.skeinforge_plugins.craft_plugins import clean
from skeinforge_application.skeinforge_plugins.craft_plugins import clip
from skeinforge_application.skeinforge_plugins.craft_plugins import comb
from skeinforge_application.skeinforge_plugins.craft_plugins import cool
from skeinforge_application.skeinforge_plugins.craft_plugins import dimension
from skeinforge_application.skeinforge_plugins.craft_plugins import export
from skeinforge_application.skeinforge_plugins.craft_plugins import fill
from skeinforge_application.skeinforge_plugins.craft_plugins import fillet
from skeinforge_application.skeinforge_plugins.craft_plugins import home
from skeinforge_application.skeinforge_plugins.craft_plugins import hop
from skeinforge_application.skeinforge_plugins.craft_plugins import inset
from skeinforge_application.skeinforge_plugins.craft_plugins import jitter
from skeinforge_application.skeinforge_plugins.craft_plugins import lash
from skeinforge_application.skeinforge_plugins.craft_plugins import limit
from skeinforge_application.skeinforge_plugins.craft_plugins import multiply
from skeinforge_application.skeinforge_plugins.craft_plugins import oozebane
from skeinforge_application.skeinforge_plugins.craft_plugins import preface
from skeinforge_application.skeinforge_plugins.craft_plugins import raft
from skeinforge_application.skeinforge_plugins.craft_plugins import speed
from skeinforge_application.skeinforge_plugins.craft_plugins import splodge
from skeinforge_application.skeinforge_plugins.craft_plugins import stretch
from skeinforge_application.skeinforge_plugins.craft_plugins import temperature
from skeinforge_application.skeinforge_plugins.craft_plugins import tower
from skeinforge_application.skeinforge_plugins.craft_plugins import unpause
from skeinforge_application.skeinforge_plugins.craft_plugins import widen
from skeinforge_application.skeinforge_plugins.craft_plugins import wipe
from skeinforge_application.skeinforge_plugins.analyze_plugins import behold
from skeinforge_application.skeinforge_plugins.analyze_plugins import comment
from skeinforge_application.skeinforge_plugins.analyze_plugins import interpret
from skeinforge_application.skeinforge_plugins.analyze_plugins import skeinview
from skeinforge_application.skeinforge_plugins.analyze_plugins import statistic
from skeinforge_application.skeinforge_plugins.analyze_plugins import vectorwrite

def getModuleWithDirectoryPath( directoryPath, fileName ):
	"Get the module from the fileName and folder name."
	if fileName == '':
		print('The file name in getModule in gcodec was empty.')
		return None
	if fileName.endswith('help'):
		return help
	if fileName.find('meta') >= 0:
		if fileName.endswith('meta'):
			return meta
		if fileName.endswith('description'):
			return description
		if fileName.endswith('polyfile'):
			return polyfile

	if fileName.find('profile') >= 0:
		if fileName.endswith('profile'):
			return profile
		if fileName.endswith('cutting'):
			return cutting
		if fileName.endswith('extrusion'):
			return extrusion
		if fileName.endswith('milling'):
			return milling
		if fileName.endswith('winding'):
			return winding

	if fileName.find('craft') >= 0:
		if fileName.endswith('craft'):
			return craft
		if fileName.endswith('carve'):
			return carve
		if fileName.endswith('chamber'):
			return chamber
		if fileName.endswith('clean'):
			return clean
		if fileName.endswith('clip'):
			return clip
		if fileName.endswith('comb'):
			return comb
		if fileName.endswith('cool'):
			return cool
		if fileName.endswith('dimension'):
			return dimension
		if fileName.endswith('export'):
			return export
		if fileName.endswith('fill'):
			return fill
		if fileName.endswith('fillet'):
			return fillet
		if fileName.endswith('home'):
			return home
		if fileName.endswith('hop'):
			return hop
		if fileName.endswith('inset'):
			return inset
		if fileName.endswith('jitter'):
			return jitter
		if fileName.endswith('lash'):
			return lash
		if fileName.endswith('limit'):
			return limit
		if fileName.endswith('multiply'):
			return multiply
		if fileName.endswith('oozebane'):
			return oozebane
		if fileName.endswith('preface'):
			return preface
		if fileName.endswith('raft'):
			return raft
		if fileName.endswith('speed'):
			return speed
		if fileName.endswith('splodge'):
			return splodge
		if fileName.endswith('stretch'):
			return stretch
		if fileName.endswith('temperature'):
			return temperature
		if fileName.endswith('tower'):
			return tower
		if fileName.endswith('unpause'):
			return unpause
		if fileName.endswith('widen'):
			return widen
		if fileName.endswith('wipe'):
			return wipe

	if fileName.find('analyze') >= 0:
		if fileName.endswith('analyze'):
			return analyze
		if fileName.endswith('behold'):
			return behold
		if fileName.endswith('comment'):
			return comment
		if fileName.endswith('interpret'):
			return interpret
		if fileName.endswith('skeinview'):
			return skeinview
		if fileName.endswith('statistic'):
			return statistic
		if fileName.endswith('vectorwrite'):
			return vectorwrite
  	
	print('')
	print('Exception traceback in getModuleWithDirectoryPath in gcodec:')
	traceback.print_exc( file = sys.stdout )
	print('')
	print('That error means; could not import a module with the fileName ' + fileName )
	print('and an absolute directory name of ' + directoryPath )
	print('')
	return None

def getModuleWithPath( path ):
	"Get the module from the path."
	return getModuleWithDirectoryPath( os.path.dirname( path ), os.path.basename( path ) )

