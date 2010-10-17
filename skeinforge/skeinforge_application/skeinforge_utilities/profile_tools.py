from fabmetheus_utilities import settings

def addListsSetCraftProfileArchive( craftSequence, defaultProfile, repository, fileNameHelp ):
	"Set the craft profile archive."
	settings.addListsToRepository( fileNameHelp, '', repository )
	repository.craftSequenceLabel = settings.LabelDisplay().getFromName('Craft Sequence: ', repository )
	craftToolStrings = []
	for craftTool in craftSequence[ : - 1 ]:
		craftToolStrings.append( settings.getEachWordCapitalized( craftTool ) + '->')
	craftToolStrings.append( settings.getEachWordCapitalized( craftSequence[ - 1 ] ) )
	for craftToolStringIndex in xrange( 0, len( craftToolStrings ), 5 ):
		craftLine = ' '.join( craftToolStrings[ craftToolStringIndex : craftToolStringIndex + 5 ] )
		settings.LabelDisplay().getFromName( craftLine, repository )
	settings.LabelDisplay().getFromName('', repository )
	repository.profileList = ProfileList().getFromName('Profile List:', repository )
	repository.profileListbox = ProfileListboxSetting().getFromListSetting( repository.profileList, 'Profile Selection:', repository, defaultProfile )
	repository.addListboxSelection = AddProfile().getFromProfileListboxSettingRepository( repository.profileListbox, repository )
	repository.deleteListboxSelection = DeleteProfile().getFromProfileListboxSettingRepository( repository.profileListbox, repository )
	directoryName = settings.getProfilesDirectoryPath()
	settings.makeDirectory( directoryName )
	repository.windowPosition.value = '0+400'
	
class ProfileList:
	"A class to list the profiles."
	def getFromName( self, name, repository ):
		"Initialize."
		self.craftTypeName = repository.lowerName
		self.name = name
		self.repository = repository
		self.setValueToFolders()
		return self

	def setValueToFolders( self ):
		"Set the value to the folders in the profiles directories."
		self.value = settings.getFolders( settings.getProfilesDirectoryPath( self.craftTypeName ) )
		defaultFolders = settings.getFolders( settings.getProfilesDirectoryInAboveDirectory( self.craftTypeName ) )
		for defaultFolder in defaultFolders:
			if defaultFolder not in self.value:
				self.value.append( defaultFolder )
		self.value.sort()
		
class ProfileListboxSetting( settings.StringSetting ):
	"A class to handle the profile listbox."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
#http://www.pythonware.com/library/tkinter/introduction/x5453-patterns.htm
		self.root = gridPosition.master
		gridPosition.increment()
		scrollbar = HiddenScrollbar( gridPosition.master )
		self.listbox = settings.Tkinter.Listbox( gridPosition.master, selectmode = settings.Tkinter.SINGLE, yscrollcommand = scrollbar.set )
		self.listbox.bind('<ButtonRelease-1>', self.buttonReleaseOne )
		gridPosition.master.bind('<FocusIn>', self.focusIn )
		scrollbar.config( command = self.listbox.yview )
		self.listbox.grid( row = gridPosition.row, column = 0, sticky = settings.Tkinter.N + settings.Tkinter.S )
		scrollbar.grid( row = gridPosition.row, column = 1, sticky = settings.Tkinter.N + settings.Tkinter.S )
		self.setStateToValue()
		self.repository.saveListenerTable['updateProfileSaveListeners'] = updateProfileSaveListeners

	def buttonReleaseOne( self, event ):
		"Button one released."
		self.setValueToIndex( self.listbox.nearest( event.y ) )

	def focusIn( self, event ):
		"The root has gained focus."
		settings.getReadRepository( self.repository )
		self.setStateToValue()

	def getFromListSetting( self, listSetting, name, repository, value ):
		"Initialize."
		self.getFromValueOnly( name, repository, value )
		self.listSetting = listSetting
		repository.archive.append( self )
		repository.displayEntities.append( self )
		return self

	def getSelectedFolder( self ):
		"Get the selected folder."
		settingProfileSubfolder = settings.getSubfolderWithBasename( self.value, settings.getProfilesDirectoryPath( self.listSetting.craftTypeName ) )
		if settingProfileSubfolder != None:
			return settingProfileSubfolder
		toolProfileSubfolder = settings.getSubfolderWithBasename( self.value, settings.getProfilesDirectoryInAboveDirectory( self.listSetting.craftTypeName ) )
		return toolProfileSubfolder

	def setStateToValue( self ):
		"Set the listbox items to the list setting."
		self.listbox.delete( 0, settings.Tkinter.END )
		for item in self.listSetting.value:
			self.listbox.insert( settings.Tkinter.END, item )
			if self.value == item:
				self.listbox.select_set( settings.Tkinter.END )

	def setToDisplay( self ):
		"Set the selection value to the listbox selection."
		currentSelectionTuple = self.listbox.curselection()
		if len( currentSelectionTuple ) > 0:
			self.setValueToIndex( int( currentSelectionTuple[0] ) )

	def setValueToIndex( self, index ):
		"Set the selection value to the index."
		valueString = self.listbox.get( index )
		self.setValueToString( valueString )

	def setValueToString( self, valueString ):
		"Set the value to the value string."
		self.value = valueString
		if self.getSelectedFolder() == None:
			self.value = self.defaultValue
		if self.getSelectedFolder() == None:
			if len( self.listSetting.value ) > 0:
				self.value = self.listSetting.value[0]
				
class AddProfile:
	"A class to add a profile."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.entry = settings.Tkinter.Entry( gridPosition.master )
		self.entry.bind('<Return>', self.addSelectionWithEvent )
		self.entry.grid( row = gridPosition.row, column = 1, columnspan = 3, sticky = settings.Tkinter.W )
		self.addButton = settings.Tkinter.Button( gridPosition.master, activebackground = 'black', activeforeground = 'white', text = 'Add Profile', command = self.addSelection )
		self.addButton.grid( row = gridPosition.row, column = 0 )

	def addSelection( self ):
		"Add the selection of a listbox setting."
		entryText = self.entry.get()
		if entryText == '':
			print('To add to the profiles, enter the material name.')
			return
		self.profileListboxSetting.listSetting.setValueToFolders()
		if entryText in self.profileListboxSetting.listSetting.value:
			print('There is already a profile by the name of %s, so no profile will be added.' % entryText )
			return
		self.entry.delete( 0, settings.Tkinter.END )
		craftTypeProfileDirectory = settings.getProfilesDirectoryPath( self.profileListboxSetting.listSetting.craftTypeName )
		destinationDirectory = os.path.join( craftTypeProfileDirectory, entryText )
		shutil.copytree( self.profileListboxSetting.getSelectedFolder(), destinationDirectory )
		self.profileListboxSetting.listSetting.setValueToFolders()
		self.profileListboxSetting.value = entryText
		self.profileListboxSetting.setStateToValue()

	def addSelectionWithEvent( self, event ):
		"Add the selection of a listbox setting, given an event."
		self.addSelection()

	def getFromProfileListboxSettingRepository( self, profileListboxSetting, repository ):
		"Initialize."
		self.profileListboxSetting = profileListboxSetting
		self.repository = repository
		repository.displayEntities.append( self )
		return self


class DeleteProfile( AddProfile ):
	"A class to delete the selection of a listbox profile."
	def addToDialog( self, gridPosition ):
		"Add this to the dialog."
		gridPosition.increment()
		self.deleteButton = settings.Tkinter.Button( gridPosition.master, activebackground = 'black', activeforeground = 'white', text = "Delete Profile", command = self.deleteSelection )
		self.deleteButton.grid( row = gridPosition.row, column = 0 )

	def deleteSelection( self ):
		"Delete the selection of a listbox setting."
		DeleteProfileDialog( self.profileListboxSetting, settings.Tkinter.Tk() )


class DeleteProfileDialog:
	"A dialog to delete a profile."
	def __init__( self, profileListboxSetting, root ):
		"Display a delete dialog."
		self.profileListboxSetting = profileListboxSetting
		self.root = root
		self.row = 0
		root.title('Delete Warning')
		self.gridPosition.increment()
		self.label = settings.Tkinter.Label( self.root, text = 'Do you want to delete the profile?')
		self.label.grid( row = self.row, column = 0, columnspan = 3, sticky = settings.Tkinter.W )
		columnIndex = 1
		deleteButton = settings.Tkinter.Button( root, activebackground = 'black', activeforeground = 'red', command = self.delete, fg = 'red', text = 'Delete')
		deleteButton.grid( row = self.row, column = columnIndex )
		columnIndex += 1
		noButton = settings.Tkinter.Button( root, activebackground = 'black', activeforeground = 'darkgreen', command = self.no, fg = 'darkgreen', text = 'Do Nothing')
		noButton.grid( row = self.row, column = columnIndex )

	def delete( self ):
		"Delete the selection of a listbox setting."
		self.profileListboxSetting.setToDisplay()
		self.profileListboxSetting.listSetting.setValueToFolders()
		if self.profileListboxSetting.value not in self.profileListboxSetting.listSetting.value:
			return
		lastSelectionIndex = 0
		currentSelectionTuple = self.profileListboxSetting.listbox.curselection()
		if len( currentSelectionTuple ) > 0:
			lastSelectionIndex = int( currentSelectionTuple[0] )
		else:
			print('No profile is selected, so no profile will be deleted.')
			return
		settings.deleteDirectory( settings.getProfilesDirectoryPath( self.profileListboxSetting.listSetting.craftTypeName ), self.profileListboxSetting.value )
		settings.deleteDirectory( getProfilesDirectoryInAboveDirectory( self.profileListboxSetting.listSetting.craftTypeName ), self.profileListboxSetting.value )
		self.profileListboxSetting.listSetting.setValueToFolders()
		if len( self.profileListboxSetting.listSetting.value ) < 1:
			defaultSettingsDirectory = settings.getProfilesDirectoryPath( os.path.join( self.profileListboxSetting.listSetting.craftTypeName, self.profileListboxSetting.defaultValue ) )
			settings.makeDirectory( defaultSettingsDirectory )
			self.profileListboxSetting.listSetting.setValueToFolders()
		lastSelectionIndex = min( lastSelectionIndex, len( self.profileListboxSetting.listSetting.value ) - 1 )
		self.profileListboxSetting.value = self.profileListboxSetting.listSetting.value[ lastSelectionIndex ]
		self.profileListboxSetting.setStateToValue()
		self.no()

	def no( self ):
		"The dialog was closed."
		self.root.destroy()


