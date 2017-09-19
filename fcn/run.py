#!/usr/bin/env python
from app import create_app, db, app
from app.models import User
import os
import imp
import ctypes
import thread
#import win32api

if __name__ == '__main__':
    app = create_app('development')
    with app.app_context():
        db.create_all()
        #if User.query.filter_by(username='john').first() is None:
        #    User.register('john', 'cat')
   
    # Load the DLL manually to ensure its handler gets
    # set before our handler.
    basepath = imp.find_module('numpy')[1]
    # Now set our handler for CTRL_C_EVENT. Other control event
    # types will chain to the next handler.
    def handler(dwCtrlType, hook_sigint=thread.interrupt_main):
    	if dwCtrlType == 0: # CTRL_C_EVENT
    		hook_sigint()
    		return 1 # don't chain to the next handler
    	return 0 # chain to the next handler
    #win32api.SetConsoleCtrlHandler(handler, 1)
    app.run(host='0.0.0.0')
