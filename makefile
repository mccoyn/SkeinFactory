all : skeinfactory/skeinfactory

clean:
	rm -rf skeinfactory
	rm -rf shedskin/build
	
skeinfactory/skeinfactory : skeinfactory/makefile
	cd skeinfactory ; make skeinfactory
	
skeinfactory/makefile : shedskin/build/scripts-2.6/shedskin skeinforge/skeinfactory.py
	cd skeinforge ; "../shedskin/build/scripts-2.6/shedskin" --dir "../skeinfactory" skeinfactory.py
	
shedskin/build/scripts-2.6/shedskin :
	cd shedskin ; ./setup.py build
