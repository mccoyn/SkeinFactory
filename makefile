all: skeinfactory/skeinfactory

clean:
	rm -rf skeinfactory
	rm -rf shedskin/build
	
skeinfactory/skeinfactory: skeinfactory/Makefile
	cp -ru patch/* skeinfactory
	cd skeinfactory ; make skeinfactory

skeinfactory/Makefile: shedskin/build/lib.linux-i686-2.6/shedskin/__init__.py skeinforge/skeinfactory.py
	cd skeinforge ; python ../shedskin/build/lib.linux-i686-2.6/shedskin/__init__.py --dir "../skeinfactory" skeinfactory.py
	
shedskin/build/lib.linux-i686-2.6/shedskin/__init__.py: shedskin/setup.py
	cd shedskin ; ./setup.py build
