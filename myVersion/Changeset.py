import os
import os.path as path
import time
import distutils.dir_util as dir_uti
import uti



""" TODO:
- nel changeset devono esserci solo i file modificati (salvo backup), da gestire con la sourceDir esternamente
  chi crea il changeset "NON" backup deve creare una cartella temporanea, passarla in modo che venga copiata nel changeset e poi eliminarla
- NON ANNOTO l'utente che ha creato il changeset
"""

class Changeset:
	
	changesetDir = ""	#path del changeset
	changesetTxt = ""	#path del file changeset.txt


	def __init__(self, changesetDir):
		self.changesetDir = changesetDir
		self.changesetTxt = path.join(self.changesetDir, "changeset.txt")


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
		if(isBackup):
			uti.writeFile("is_backup: 1", self.changesetTxt, False)
		else:
			uti.writeFile("is_backup: 0", self.changesetTxt, False);

		#scrivo data e ora di crezione
		uti.writeFile("date: " + time.strftime("%d/%m/%Y") + " " + time.strftime("%H:%M:%S"), self.changesetTxt)


	#ritorna True se il changeset è un changeset di backup
	def isBackup(self):
		#leggo il tag is_backup del file
		if(int(uti.readFileByTag("is_backup: ", self.changesetTxt)) == 1):
			return True
		
		return False