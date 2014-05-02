#!/usr/bin/python

from PyQt4.QtGui import *   
from subprocess import call, check_output
import random
import os

def mount(target, passw):
    strn = "mount " + target + " -o passphrase_passwd_file=" + passw
    ret = call(["kdesudo", strn], shell=False)
    return ret;


class CryptMount(QDialog):
    def __init__(self, parent=None):
	self.mountedFSList = []
	
        super(CryptMount, self).__init__(parent)
        self.setWindowTitle("Mount Encrypted File Systems")
        self.textPass = QLineEdit(self)
        self.textPass.setEchoMode(QLineEdit.Password)
        self.mountbutton = QPushButton('Mount', self)
        self.mountbutton.clicked.connect(self.mountButtonClicked)
        self.fsList = QListWidget(self)
        hlayout = QHBoxLayout()
        hlayout.addWidget( QLabel("Passphrase: ") )
        hlayout.addWidget(self.textPass)
        layout = QVBoxLayout(self)
        
        layout.addWidget( QLabel("Available unmounted eCryptFS file systems: ") )
        layout.addWidget(self.fsList)
        
        layout.addLayout(hlayout)
        self.display = QLabel("")
        layout.addWidget(self.mountbutton)
        layout.addWidget(self.display)
        self.resize(350, 250)
        
        self.findMounted()
        self.findCryptFS()
        
        
    ### read /etc/fstab and find all ecryptfs mounts; if one is found, push the FS name
    ### to the list widget for the user to select from, if the respective directory isn't
    ### found in the already mounted list
    ###
    def findCryptFS(self):
	fstabfile = open("/etc/fstab", "r")
	lines = fstabfile.readlines()
	
	for l in lines:
	    sections = l.split(" ")
	    if len(sections)>=2 and sections[0].startswith("#")==False and sections[0].startswith("\n")==False:
	      if sections[2]=="ecryptfs":
		  alreadyMounted = False
		  for mounted in self.mountedFSList:
		      if mounted == sections[0]:
			  alreadyMounted = True;
			  
		  if alreadyMounted==False:
		      self.fsList.addItem(sections[0])
		      
	self.fsList.setCurrentRow(0)

 
    ### runs mount, grabbing the output and splitting it into lines
    ### then scans the lines for a fstype of ecryptfs, and adds all found
    ### ecryptfs file systems that are already mounted to self.mountedFSList
    ###
    def findMounted(self):
	mountstring = check_output(["mount"])
	if len(mountstring):
	    lines = mountstring.split("\n")
	    for l in lines:
		sections = l.split(" ")
		fstypeSection = -1
		for s in range(0, len(sections)):
		    if sections[s] == "type":
			fstypeSection = s+1
			break
		if fstypeSection>=0 and sections[fstypeSection] == "ecryptfs":
		    self.mountedFSList.append(sections[1])
        
        
        
    ### user has clicked the mouse button; try to mount the selected directory
    ### exit if succeeded, stay open and show message if mount failed 
    ###
    def mountButtonClicked(self):
	mountReturn = 0
	
	self.display.setText("Mounting...")
	
	### write the passphrase to a file; mount.ecryptfs will read it from there
	### so we don't later have the clear text passphrase exposed when just running 'mount'
	### we append a large random number to the file name to make it less likely that the file
	### can be intercepted before it's deleted
	###
	filename = "/tmp/ecfspw"
	rnum = random.getrandbits(64)
	filename += str(rnum)
	passwdfile = open(filename, "wt")
	passwdfile.write("passphrase_passwd=" + str(self.textPass.text()) );
	passwdfile.close()
	mountReturn = mount( str(self.fsList.currentItem().text()), filename);
	
	### remove the file as soon as the mount is complete. Note that this may still expose
	### the passphrase if an attacker would manage to intercept the file before it's written
	os.remove(filename)
	
	if mountReturn==0:
	    self.display.setText("Mounted.")
	    self.accept()
	else:
	    self.display.setText("Error " + str(mountReturn) + ". Incorrect passphrase?")


import sys

app = QApplication(sys.argv)
ret = CryptMount().exec_();

