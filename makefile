all: skeinfactory/skeinfactory

clean:
	rm -rf skeinfactory
	rm -rf shedskin/build
	
skeinfactory/skeinfactory: skeinfactory/Makefile
	cp -ru patch/* skeinfactory
	cd skeinfactory ; make skeinfactory

skeinfactory/Makefile: shedskin/build/scripts-2.6/shedskin skeinforge/skeinfactory.py
	cd skeinforge ; "../shedskin/build/scripts-2.6/shedskin" --dir "../skeinfactory" skeinfactory.py
	
shedskin/build/scripts-2.6/shedskin:
	cd shedskin ; ./setup.py build
