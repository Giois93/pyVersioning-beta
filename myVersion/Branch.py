import os 
import os.path as path
import shutil
import distutils.dir_util as dir_uti
import datetime
import natsort
import uti
from uti import BRANCH_FILE
from uti import CHANGESET_FILE
from Changeset import Changeset

class Branch:
	branchDir = ""		#path del branch
	branchTxt = ""		#path del file branch.txt


	def __init__(self, branchDir):
		self.branchDir = branchDir
		self.branchTxt = path.join(self.branchDir, BRANCH_FILE)

	
	def createNew(self, sourceDir, originalChangeset = 0):
		"""crea un nuovo branch sul disco, aggiunge il changeset_0 e il file branch.txt
		se esiste già solleva un'eccezione"""

		if (path.isdir(self.branchDir)):
			raise Exception

		self.addChangeset(sourceDir, "changeset_0", originalChangeset, True)


	def addChangeset(self, sourceDir, comment, changesetNum=None, isBackup=False):
		"""crea il prossimo changeset copiandoci la cartella sourceDir"""
		
		#controllo se è necessario creare un changeset di backup (ne viene fatto uno ogni giorno)
		#cerco l'ultimo changeset di backup
		if(isBackup == False):
			try:
				lastBackupChangeset = self.getLastBackupChangeset(self.getLastChangesetNum())

				#prendo la data dell'ultimo changeset di backup
				dateStr = uti.readFileByTag("date", lastBackupChangeset.changesetTxt)[0]
				date = uti.getDate(dateStr)

				#prendo la data odierna
				today = datetime.date.today()
				#se è passato un giorno dall'ultimo backup ne creo uno
				diff = abs(today - date)
				if(diff.days > 0):
					#creo una cartella temporanea e ci copio una ultima versione completa
					tmpDir = path.join(self.branchDir, "tmp")
					self.getLatestVersion(tmpDir)
					#creo un changeset di backup con l'ultima versione
					self.addChangeset(tmpDir, comment = "backup {}".format(dateStr), isBackup = True)
					shutil.rmtree(tmpDir)
			except:
				pass

		#se non è specificato il changeset iniziale prendo l'id dell'ultimo changeset di questo branch
		if (changesetNum == None):
			changesetNum = self.getNextChangesetNum() 
		
		#creo una cartella per il changeset
		changesetDir = path.join(self.branchDir, str(self.getNextChangesetNum()))
		
		#creo il changeset
		changeset = Changeset(changesetDir)
		changeset.createNew(sourceDir, isBackup)

		#scrivo il suo file
		#se sto inserendo il primo changeset nel branch scrivo anche il tag "changeset_0"
		if (len(os.listdir(self.branchDir)) == 1):
			uti.writeFileByTag("changeset_0", str(changesetNum), self.branchTxt)
		uti.writeFileByTag("last_changeset", str(self.getNextChangesetNum()), self.branchTxt)
		uti.writeFileByTag("comment", comment, changeset.changesetTxt)

		return changesetNum


	def getChangeset(self, changesetNum):
		"""ritorna il changeset associato al "changesetNum" """

		if (path.isdir(path.join(self.branchDir, str(changesetNum))) == False):
			raise Exception("Changeset non presente")

		return Changeset(path.join(self.branchDir, str(changesetNum)))


	def getLastChangeset(self):
		"""ritorna l'ultimo changeset del branch"""

		return getChangeset(self.getLastChangesetNum())


	def getLastChangesetNum(self):
		"""ritorna il numero del last_changeset se il brach esiste, -1 per un nuovo branch"""

		try:
			return int(uti.readFileByTag("last_changeset", self.branchTxt)[0])
		except:
			return -1


	def getNextChangesetNum(self):
		"""ritorna il numero del last_changeset + 1"""
		
		return self.getLastChangesetNum() + 1


	def getChangesetList(self):
		"""ritorna la lista dei changeset"""

		#prendo tutte le cartelle all'interno del branch (i changeset)
		dirs = [ dirName for dirName in os.listdir(self.branchDir) if (path.isdir(path.join(self.branchDir, dirName))) ]
		
		#ritorno una tupla di "chageset - data creazione - commento"
		results = ()
		for dir in natsort.natsorted(dirs):
			changeset = self.getChangeset(int(dir))
			#prendo il path della cartella del changeset
			dirPath = path.join(self.branchDir, dir)
			#prendo la data di creazione del changeset
			date = datetime.datetime.fromtimestamp(path.getctime(changeset.changesetDir)).strftime("%Y-%m-%d %H:%M:%S")
			
			try:
				#prendo il commento dal file del changeset
				comment = uti.readFileByTag("comment", changeset.changesetTxt)[0]
			except:
				comment = ""

			#prendo una lista di tutti i file modificati in questo changeset
			changes = ""
			for elem in uti.listDir(changeset.changesetDir):
				if (path.basename(elem) == "changeset.txt"):
					continue
				
				#scrivo il file modificato in questo changeset
				try:
					tag = uti.readFileByTag("file_{}".format(elem.replace("\\", "")), changeset.changesetTxt)[0]
					changes += "{} ({})\n".format(uti.getPathForPrint(elem), tag)
				except:
					changes += "{}\n".format(uti.getPathForPrint(elem))

			#aggiungo il changeset e le sue statistiche
			results += ("{} - {} - {} \n{}".format(dir, str(date), comment, changes), )

		return results

	
	def getLatestVersion(self, destDir):
		"""copia l'ultima versione completa nella cartella destDir"""
		
		#prendo l'ultimo changeset
		lastChangeset = self.getLastChangesetNum()
		
		#prendo la versione associata all'ultimo changeset
		self.getSpecificVersion(lastChangeset, destDir)

		return lastChangeset

	
	def getSpecificVersion(self, changesetNum, destDir):
		"""copia la versione completa fino al changeset "changesetNum" nella cartella destDir"""
		
		#scorro tutti i changeset all'indietro fino al primo changeset di backup
		currChangeset = self.getLastBackupChangeset(changesetNum)

		#copio tutto il changeset di backup nella cartella provvisoria
		shutil.copytree(currChangeset.changesetDir, destDir)

		#scorro tutti i changeset successivi e copio i file presenti nella cartella temporanea
		for changesetID in range(int(path.basename(currChangeset.changesetDir)) + 1, changesetNum + 1):
			currChangeset = Changeset(path.join(self.branchDir, str(changesetID)))
			#copia di tutti i file e sottocartelle contenute nella cartella sourceDir dentro la cartella destDir
			dir_uti.copy_tree(currChangeset.changesetDir, destDir)

		os.remove(path.join(destDir, CHANGESET_FILE))

	
	def getLastBackupChangeset(self, startChangeset):
		"""ritorna l'ultimo changeset di backup"""

		#scorro tutti i changeset all'indietro fino al primo changeset di backup
		for changesetID in range(startChangeset, -1, -1):
			currChangeset = Changeset(path.join(self.branchDir, str(changesetID)))
			if (currChangeset.isBackup()):
				return currChangeset;
		
		#se non viene trovato nessun changeset di backup alzo un'eccezione
		raise Exception
		
