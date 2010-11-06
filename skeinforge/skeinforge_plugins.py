#!/usr/bin/python

import __init__

from fabmetheus_utilities import gcodec
from skeinforge_application.skeinforge_plugins import analyze
from skeinforge_application.skeinforge_plugins import craft
from skeinforge_application.skeinforge_plugins import help
from skeinforge_application.skeinforge_plugins import meta
from skeinforge_application.skeinforge_plugins import profile
#from skeinforge_application.skeinforge_plugins.analyze_plugins import behold
#from skeinforge_application.skeinforge_plugins.analyze_plugins import comment
#from skeinforge_application.skeinforge_plugins.analyze_plugins import interpret
#from skeinforge_application.skeinforge_plugins.analyze_plugins import skeinview
#from skeinforge_application.skeinforge_plugins.analyze_plugins import statistic
#from skeinforge_application.skeinforge_plugins.analyze_plugins import vectorwrite
from skeinforge_application.skeinforge_plugins.craft_plugins import carve
#from skeinforge_application.skeinforge_plugins.craft_plugins import chamber
#from skeinforge_application.skeinforge_plugins.craft_plugins import chop
#from skeinforge_application.skeinforge_plugins.craft_plugins import cleave
#from skeinforge_application.skeinforge_plugins.craft_plugins import clip
#from skeinforge_application.skeinforge_plugins.craft_plugins import coil
#from skeinforge_application.skeinforge_plugins.craft_plugins import comb
#from skeinforge_application.skeinforge_plugins.craft_plugins import cool
#from skeinforge_application.skeinforge_plugins.craft_plugins import dimension
#from skeinforge_application.skeinforge_plugins.craft_plugins import drill
#from skeinforge_application.skeinforge_plugins.craft_plugins import export
#from skeinforge_application.skeinforge_plugins.craft_plugins import feed
#from skeinforge_application.skeinforge_plugins.craft_plugins import fill
#from skeinforge_application.skeinforge_plugins.craft_plugins import fillet
#from skeinforge_application.skeinforge_plugins.craft_plugins import flow
#from skeinforge_application.skeinforge_plugins.craft_plugins import home
#from skeinforge_application.skeinforge_plugins.craft_plugins import hop
#from skeinforge_application.skeinforge_plugins.craft_plugins import inset
#from skeinforge_application.skeinforge_plugins.craft_plugins import jitter
#from skeinforge_application.skeinforge_plugins.craft_plugins import lash
#from skeinforge_application.skeinforge_plugins.craft_plugins import lift
#from skeinforge_application.skeinforge_plugins.craft_plugins import limit
#from skeinforge_application.skeinforge_plugins.craft_plugins import mill
#from skeinforge_application.skeinforge_plugins.craft_plugins import multiply
#from skeinforge_application.skeinforge_plugins.craft_plugins import oozebane
#from skeinforge_application.skeinforge_plugins.craft_plugins import outset
#from skeinforge_application.skeinforge_plugins.craft_plugins import preface
#from skeinforge_application.skeinforge_plugins.craft_plugins import raft
#from skeinforge_application.skeinforge_plugins.craft_plugins import speed
#from skeinforge_application.skeinforge_plugins.craft_plugins import splodge
#from skeinforge_application.skeinforge_plugins.craft_plugins import stretch
#from skeinforge_application.skeinforge_plugins.craft_plugins import temperature
#from skeinforge_application.skeinforge_plugins.craft_plugins import tower
#from skeinforge_application.skeinforge_plugins.craft_plugins import unpause
#from skeinforge_application.skeinforge_plugins.craft_plugins import whittle
#from skeinforge_application.skeinforge_plugins.craft_plugins import widen
#from skeinforge_application.skeinforge_plugins.craft_plugins import wipe
from skeinforge_application.skeinforge_plugins.meta_plugins import description
from skeinforge_application.skeinforge_plugins.meta_plugins import polyfile
from skeinforge_application.skeinforge_plugins.profile_plugins import cutting
from skeinforge_application.skeinforge_plugins.profile_plugins import extrusion
from skeinforge_application.skeinforge_plugins.profile_plugins import milling
from skeinforge_application.skeinforge_plugins.profile_plugins import winding

def add_all():
	"add all of the plugins to the dictionary"

	# skeinforge plugins
	gcodec.Plugins.add(analyze.getNewPlugin())
	gcodec.Plugins.add(craft.getNewPlugin())
	gcodec.Plugins.add(help.getNewPlugin())
	gcodec.Plugins.add(meta.getNewPlugin())
	gcodec.Plugins.add(profile.getNewPlugin())
	
	# analyze plugins
	#gcodec.Plugins.add(behold.getNewPlugin())
	#gcodec.Plugins.add(comment.getNewPlugin())
	#gcodec.Plugins.add(interpret.getNewPlugin())
	#gcodec.Plugins.add(skeinview.getNewPlugin())
	#gcodec.Plugins.add(statistic.getNewPlugin())
	#gcodec.Plugins.add(vectorwrite.getNewPlugin())

	# carve plugins
	gcodec.Plugins.add(carve.getNewPlugin())
	#gcodec.Plugins.add(chamber.getNewPlugin())
	#gcodec.Plugins.add(chop.getNewPlugin())
	#gcodec.Plugins.add(cleave.getNewPlugin())
	#gcodec.Plugins.add(clip.getNewPlugin())
	#gcodec.Plugins.add(coil.getNewPlugin())
	#gcodec.Plugins.add(comb.getNewPlugin())
	#gcodec.Plugins.add(cool.getNewPlugin())
	#gcodec.Plugins.add(dimension.getNewPlugin())
	#gcodec.Plugins.add(drill.getNewPlugin())
	#gcodec.Plugins.add(export.getNewPlugin())
	#gcodec.Plugins.add(feed.getNewPlugin())
	#gcodec.Plugins.add(fill.getNewPlugin())
	#gcodec.Plugins.add(fillet.getNewPlugin())
	#gcodec.Plugins.add(flow.getNewPlugin())
	#gcodec.Plugins.add(home.getNewPlugin())
	#gcodec.Plugins.add(hop.getNewPlugin())
	#gcodec.Plugins.add(inset.getNewPlugin())
	#gcodec.Plugins.add(jitter.getNewPlugin())
	#gcodec.Plugins.add(lash.getNewPlugin())
	#gcodec.Plugins.add(lift.getNewPlugin())
	#gcodec.Plugins.add(limit.getNewPlugin())
	#gcodec.Plugins.add(mill.getNewPlugin())
	#gcodec.Plugins.add(multiply.getNewPlugin())
	#gcodec.Plugins.add(oozebane.getNewPlugin())
	#gcodec.Plugins.add(outset.getNewPlugin())
	#gcodec.Plugins.add(preface.getNewPlugin())
	#gcodec.Plugins.add(raft.getNewPlugin())
	#gcodec.Plugins.add(speed.getNewPlugin())
	#gcodec.Plugins.add(splodge.getNewPlugin())
	#gcodec.Plugins.add(stretch.getNewPlugin())
	#gcodec.Plugins.add(temperature.getNewPlugin())
	#gcodec.Plugins.add(tower.getNewPlugin())
	#gcodec.Plugins.add(unpause.getNewPlugin())
	#gcodec.Plugins.add(whittle.getNewPlugin())
	#gcodec.Plugins.add(widen.getNewPlugin())
	#gcodec.Plugins.add(wipe.getNewPlugin())

	# meta plugins
	gcodec.Plugins.add(description.getNewPlugin())
	gcodec.Plugins.add(polyfile.getNewPlugin())
	
	# profile plugins
	gcodec.Plugins.add(cutting.getNewPlugin())
	gcodec.Plugins.add(extrusion.getNewPlugin())
	gcodec.Plugins.add(milling.getNewPlugin())
	gcodec.Plugins.add(winding.getNewPlugin())

if __name__ == "__main__":
	add_all()
