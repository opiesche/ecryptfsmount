ecryptfsmount
=============

Python app to mount ecryptfs file systems from /etc/fstab

If you want to set up more than one ecryptfs file system (separate folders for different purposes, or an ecryptfs inside a cloud storage sync folder, for example), you need to wrap the passphrase into your login password and set up scripts to mount automatically. If you don't want to do that (for instance because you don't want to automount on login for security reasons), you're stuck mounting via terminal everytime. This is a small application to remedy that.

It still requires the ecryptfs and mount point to be properly set up in /etc/fstab. To mount without prompting, a few options are necessary. An example fstab entry:

/home/user/.encrypted /home/user/Encrypted ecryptfs user,noauto,rw,ecryptfs_sig=[sig],ecryptfs_cipher=aes,ecryptfs_key_bytes=32,ecryptfs_passthrough=n,ecryptfs_enable_filename_crypto=n,no_sig_cache 0 0

Where [sig] is the passphrase signature output when first creating the mount. The cipher, key_bytes, passthrough and filename_crypto options have to match the options on creation of the ecryptfs mount.


ecryptfs_mount.py first scans /etc/fstab for available ecryptfs file systems, and then the output of mount to determine which of them are already mounted. Ecryptfs mounts that are not currently mounted are added to a listbox to select from, the passphrase can be entered in a line edit, and a mount button attempts to mount the selected file system.
The passphrase is written in the clear to a text file /tmp/ecfspwXXXX (where XXXX is a 64bit random number to make interception less likely), and passed to mount.ecryptfs via passphrase_passwd_file. The temporary file is deleted immediately after the mount succeeds or fails. This should avoid exposing the clear text passphrase through mount.

NOTES: I have no idea whether this mechanism is secure, or how secure. This is relatively untested, i.e. It Works For Me(tm) on Kubuntu 14.04. 

Dependencies: Python, PyQT4, Python's subprocess, os, and random modules, and of course ecryptfs.
