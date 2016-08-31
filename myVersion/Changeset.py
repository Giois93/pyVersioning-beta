import os
import os.path as path
import time
import distutils.dir_util as dir_uti
import uti
from uti import CHANGESET_FILE
from uti import COMMIT_FILE

class Changeset:
	
	changesetDir = ""	#path del changeset
	changesetTxt = ""	#path del file changeset.txt.pyV
	commitTxt	 = ""   #path del file commit.txt.pyV

	def __init__(self, changesetDir):
		self.changesetDir = changesetDir
		self.changesetTxt = path.join(self.changesetDir, CHANGESET_FILE)
		self.commitTxt = path.join(self.changesetDir, COMMIT_FILE)


	def isBackup(self):
		"""ritorna True se il changeset è un changeset di backup"""

		try:
			#leggo il tag is_backup del file
			if (int(uti.readFileByTag("is_backup", self.changesetTxt)[0]) == 1):
				return True
			return False
		except:
			return False