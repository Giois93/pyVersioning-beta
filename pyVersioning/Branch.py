import os 
import os.path as path
import shutil
import distutils.dir_util as dir_uti
import datetime
import time
import natsort
import uti
from consts import *
from Changeset import Changeset

class Branch:
	branchDir = ""		#path del branch
	branchTxt = ""		#path del file branch.txt.pyV


	def __init__(self, branchDir):

		self.branchDir = branchDir
		self.branchTxt = path.join(self.branchDir, BRANCH_FILE)


	def addChangeset(self, comment, isBackup=False):
		"""crea il prossimo changeset"""
		
		#controllo se è necessario creare un changeset di backup (ne viene fatto uno ogni giorno)
		#cerco l'ultimo changeset di backup
		if (isBackup == False):
			try:
				lastBackupChangeset = self.getLastBackupChangeset(self.getLastChangesetNum())

				#prendo la data dell'ultimo changeset di backup
				dateStr = uti.readFileByTag(DATE, lastBackupChangeset.changesetTxt)[0]
				date = uti.getDate(dateStr)

				#prendo la data odierna
				today = datetime.date.today()
				#se è passato un giorno dall'ultimo backup ne creo uno
				diff = abs(today - date)
				if (diff.days > 0):
					#creo una cartella temporanea e ci copio una ultima versione completa
					tmpDir = self.getLatestVersion()
					#creo un changeset di backup con l'ultima versione
					changeset = self.addChangeset(comment = "backup {}".format(dateStr), isBackup=True)
					#copio l'ultima versione nella cartella del changeset
					dir_uti.copy_tree(tmpDir, changeset.changesetDir)
			except:
				pass

		#creo il changeset
		changeset = Changeset(path.join(self.branchDir, str(self.getNextChangesetNum() )))

		if (path.isdir(changeset.changesetDir)):
			raise Exception

		os.makedirs(changeset.changesetDir)

		#aggiorno l'ultimo changeset
		uti.writeFileByTag(LAST_CHANGESET, str(self.getNextChangesetNum()), self.branchTxt)

		#scrivo il commento per il nuovo changeset
		uti.writeFileByTag(COMMENT, comment, changeset.changesetTxt)
		
		#scrivo se il changeset è un backup
		if (isBackup):
			uti.writeFileByTag(IS_BACKUP, 1, changeset.changesetTxt)
		else:
			uti.writeFileByTag(IS_BACKUP, 0, changeset.changesetTxt)

		#scrivo data e ora di crezione
		uti.writeFileByTag(DATE, "{} {}".format(time.strftime("%d/%m/%Y"), time.strftime("%H:%M:%S")), changeset.changesetTxt)

		return changeset


	def getChangeset(self, changesetNum):
		"""ritorna il changeset associato al "changesetNum" """

		if (path.isdir(path.join(self.branchDir, str(changesetNum))) == False):
			raise Exception("Changeset non presente")

		return Changeset(path.join(self.branchDir, str(changesetNum)))


	def getLastChangeset(self):
		"""ritorna l'ultimo changeset del branch"""

		return self.getChangeset(self.getLastChangesetNum())


	def getLastChangesetNum(self):
		"""ritorna il numero del last_changeset se il brach esiste, -1 per un nuovo branch"""

		try:
			return int(uti.readFileByTag(LAST_CHANGESET, self.branchTxt)[0])
		except:
			return -1


	def getNextChangesetNum(self):
		"""ritorna il numero del last_changeset + 1"""
		
		return self.getLastChangesetNum() + 1


	def getChangesetList(self):
		"""ritorna la lista dei changesets con modifiche"""

		#prendo tutte le cartelle all'interno del branch (i changeset)
		dirs = [ dirName for dirName in os.listdir(self.branchDir) if ((path.isdir(path.join(self.branchDir, dirName))) & (dirName.isdigit())) ]
		
		#ritorno una tupla di "chageset - data creazione - commento"
		results = []

		#for dir in dirs:"""
		for currDir in natsort.natsorted(dirs):
			changeset = self.getChangeset(int(currDir))
			#prendo il path della cartella del changeset
			#prendo la data di creazione del changeset
			date = datetime.datetime.fromtimestamp(path.getctime(changeset.changesetDir)).strftime("%Y-%m-%d %H:%M:%S")
			
			try:
				#prendo il commento dal file del changeset
				comment = uti.readFileByTag(COMMENT, changeset.changesetTxt)[0]
			except:
				comment = ""

			#prendo una lista di tutti i file modificati in questo changeset
			changes = ""
			try:
				for file in uti.readFileByTag(EDIT, changeset.commitTxt):
					changes += "{} ({})\n".format(file, EDIT)
			except: 
				pass

			try:
				for file in uti.readFileByTag(OLD, changeset.commitTxt):
					changes += "{} ({})\n".format(file, OLD)
			except: 
				pass

			try:
				for file in uti.readFileByTag(ADD, changeset.commitTxt):
					changes += "{} ({})\n".format(file, ADD)
			except: 
				pass

			try:
				for file in uti.readFileByTag(REMOVED, changeset.commitTxt):
					changes += "{} ({})\n".format(file, REMOVED)
			except: 
				pass
			
			#aggiungo il changeset e le sue statistiche
			results.append("{} - {} - {} \n{}".format(currDir, str(date), comment, changes))

		return results

	
	def getLatestVersion(self):
		"""copia l'ultima versione completa in una cartella temporanea"""

		#prendo l'ultimo changeset
		lastChangeset = self.getLastChangesetNum()
		
		#prendo la versione associata all'ultimo changeset
		destdir = self.getSpecificVersion(lastChangeset)

		return destdir

	
	def getSpecificVersion(self, changesetNum):
		"""copia la versione completa fino al changeset "changesetNum" nella cartella branchDir/tmp"""
		
		#creo la cartella temporanea
		destDir = path.join(self.branchDir, TMP_DIR)
		if (path.isdir(destDir)):
			shutil.rmtree(destDir)

		#scorro tutti i changeset all'indietro fino al primo changeset di backup
		currChangeset = self.getLastBackupChangeset(changesetNum)

		#copio tutto il changeset di backup nella cartella provvisoria
		shutil.copytree(currChangeset.changesetDir, destDir)

		#scorro tutti i changeset successivi e copio i file presenti nella cartella temporanea
		for changesetID in range(int(path.basename(currChangeset.changesetDir)) + 1, changesetNum + 1):
			currChangeset = Changeset(path.join(self.branchDir, str(changesetID)))
			#copia di tutti i file e sottocartelle contenute nella cartella sourceDir dentro la cartella destDir
			dir_uti.copy_tree(currChangeset.changesetDir, destDir)
			#rimuove tutti i file cancellati con questo changeset
			for fileToRemove in uti.readFileByTag(REMOVED, currChangeset.commitTxt):
				os.remove(path.join(destDir, fileToRemove))
		try:
			os.remove(path.join(destDir, CHANGESET_FILE))
			os.remove(path.join(destDir, COMMIT_FILE))
		except:
			pass

		return destDir

	
	def getLastBackupChangeset(self, startChangeset):
		"""ritorna l'ultimo changeset di backup"""

		#scorro tutti i changeset all'indietro fino al primo changeset di backup
		for changesetID in range(startChangeset, -1, -1):
			currChangeset = Changeset(path.join(self.branchDir, str(changesetID)))
			if (currChangeset.isBackup()):
				return currChangeset

		#se non viene trovato nessun changeset di backup alzo un'eccezione
		raise Exception