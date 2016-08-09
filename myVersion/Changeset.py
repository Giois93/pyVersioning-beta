import os
import os.path as path
import time
import distutils.dir_util as dir_uti
import uti
from uti import CHANGESET_FILE

class Changeset:
	
	changesetDir = ""	#path del changeset
	changesetTxt = ""	#path del file changeset.txt


	def __init__(self, changesetDir):
		self.changesetDir = changesetDir
		self.changesetTxt = path.join(self.changesetDir, CHANGESET_FILE)


	#crea un nuovo changeset sul disco
	def createNew(self, sourceDir, isBackup=False):

		#copio il contenuto della sourceDir nella cartella del nuovo changeset
		dir_uti.copy_tree(sourceDir, self.changesetDir)
		#elimino il vecchio file se sto facendo una copia del changeset
		try:
			os.remove(self.changesetTxt)
		except: 
			pass

		#scrivo il file del nuovo changeset
		#scrivo se il changeset è un backup
		if (isBackup):
			uti.writeFileByTag("is_backup", 1, self.changesetTxt)
		else:
			uti.writeFileByTag("is_backup", 0, self.changesetTxt);

		#scrivo data e ora di crezione
		uti.writeFile("date: {} {}".format(time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S")), self.changesetTxt)


	#ritorna True se il changeset è un changeset di backup
	def isBackup(self):
		try:
			#leggo il tag is_backup del file
			if (int(uti.readFileByTag("is_backup", self.changesetTxt)[0]) == 1):
				return True
			return False
		except:
			return False