all: resources.py autostapleconfig_ui.py

resources.py : resources.qrc action_icon.png
	/System/Library/Frameworks/Python.framework/Versions/2.6/bin/pyrcc4 -o $@ $<

autostapleconfig_ui.py : autostapleconfig.ui
	/System/Library/Frameworks/Python.framework/Versions/2.6/bin/pyuic4 $< > $@