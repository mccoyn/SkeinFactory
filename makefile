SHEDSKIN=shedskin/build/lib.linux-i686-2.6/shedskin/__init__.py

all: skeinfactory/skeinfactory

clean:
	rm -rf skeinfactory
	rm -rf shedskin/build
	rm -f `find ./skeinforge -name '*.pyc'`
	rm -f skeinforge/operator.py
	rm -f skeinforge/shutil.py
	rm -f skeinforge/tkFileDialog.py
	rm -f skeinforge/Tkinter.py
	rm -f skeinforge/traceback.py
	rm -f skeinforge/cmath.py
	rm -f skeinforge/struct.py
	
runinpy:
	rm -f skeinforge/operator.py
	rm -f skeinforge/shutil.py
	rm -f skeinforge/tkFileDialog.py
	rm -f skeinforge/Tkinter.py
	rm -f skeinforge/traceback.py
	rm -f skeinforge/cmath.py
	rm -f skeinforge/struct.py
	cd skeinforge ; ./skeinfactory.py
	
skeinfactory/skeinfactory: skeinfactory/Makefile
	cp -ru patch/* skeinfactory
	cd skeinfactory ; make skeinfactory

skeinfactory/Makefile: $(SHEDSKIN) skeinforge/skeinfactory.py
	cp -u skeinforge/operator.ss skeinforge/operator.py
	cp -u skeinforge/shutil.ss skeinforge/shutil.py
	cp -u skeinforge/tkFileDialog.ss skeinforge/tkFileDialog.py
	cp -u skeinforge/Tkinter.ss skeinforge/Tkinter.py
	cp -u skeinforge/traceback.ss skeinforge/traceback.py
	cp -u skeinforge/cmath.ss skeinforge/cmath.py
	cp -u skeinforge/struct.ss skeinforge/struct.py
	cd skeinforge ; python ../$(SHEDSKIN) --dir "../skeinfactory" skeinfactory.py
	
$(SHEDSKIN): shedskin/setup.py
	cd shedskin ; ./setup.py build
