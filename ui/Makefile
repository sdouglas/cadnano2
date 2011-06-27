IMAGES = images/data-svg.png images/data-new_32.png images/data-open_32.png images/data-save_32.png images/part-new-honeycomb.png images/part-new-square.png images/slice-delete-last.png images/slice-move.png images/slice-renumber.png images/slice-edit.png images/slice-go-last.png images/slice-go-first.png images/add-bases.svg images/remove-bases.svg images/path-insert.png images/path-pen_48.png images/path-paint_48.png images/path-move.png images/path-skip.png images/path-sequence.png images/path-force-xover.png images/path-break_48.png images/path-erase_32.png images/path-edit_32.png images/path-autostaple_32.png 


all: ui_mainwindow.py icons_rc.py

ui_mainwindow.py : mainwindow.ui
	/System/Library/Frameworks/Python.framework/Versions/2.6/bin/pyuic4 $< > $@

icons_rc.py : icons.qrc $(IMAGES)
	/System/Library/Frameworks/Python.framework/Versions/2.6/bin/pyrcc4 -o $@ $<
