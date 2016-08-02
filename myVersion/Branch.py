import os 
import os.path as path
import distutils.dir_util as dir_uti
import datetime
import uti
from Changeset import Changeset

class Branch:
	branchDir = ""		#path del branch
	branchTxt = ""		#path del file branch.txt


	#sourceDir: path della cartella con il changeset di backup del trunk - verrà spostata nella ./branchRoot/0
	#branchRoot: path del branch
	def __init__(self, branchDir):
		self.branchDir = branchDir
		self.branchTxt = path.join(self.branchDir, "branch.txt")


	#crea un nuovo branch sul disco, aggiunge il changeset_0 e il file branch.txt
	#se esiste già solleva un'eccezione
	def createNew(self, sourceDir, originalChangeset = 0):
		if(path.isdir(self.branchDir)):
			raise Exception

		self.addChangeset(sourceDir, "changeset_0", originalChangeset, True)


	#crea il prossimo changeset copiandoci la cartella sourceDir
	def addChangeset(self, sourceDir, comment, originalChangesetNum = None, isBackup = False):
		
		#se non è specificato il changeset iniziale prendo l'id dell'ultimo changeset di questo branch
		if(originalChangesetNum == None):
			originalChangesetNum = self.getNextChangesetNum() 
		
		#creo una cartella per il changeset
		changesetDir = path.join(self.branchDir, str(self.getNextChangesetNum()))
		
		#creo il changeset
		changeset = Changeset(changesetDir)
		changeset.createNew(sourceDir, isBackup)

		#scivo il suo file
		#se sto inserendo il primo changeset nel branch scrivo anche il tag "changeset_0"
		if (len(os.listdir(self.branchDir)) == 1):
			uti.writeFile("changeset_0: " + str(originalChangesetNum), self.branchTxt)
		uti.writeFileByTag("last_changeset", str(self.getNextChangesetNum()), self.branchTxt)
		uti.writeFileByTag("comment", comment, self.branchTxt)


	#ritorna il changeset associato al "changesetNum"
	def getChangeset(self, changesetNum):
		return Changeset(path.join(self.branchDir, str(changesetNum)))


	#ritorna l'ultimo changeset del branch
	def getLastChangeset(self):
		return getChangeset(self.getLastChangesetNum())


	#ritorna il numero del last_changeset se il brach esiste, -1 per un nuovo branch
	def getLastChangesetNum(self):
		try:
			return int(uti.readFileByTag("last_changeset", self.branchTxt)[0])
		except:
			return -1


	#ritorna il numero del last_changeset + 1
	def getNextChangesetNum(self):
		return self.getLastChangesetNum() + 1


	#ritorna la lista dei changeset
	def getChangesetList(self):
		#prendo tutte le cartelle all'interno del branch (i changeset)
		dirs = [ dirName for dirName in os.listdir(self.branchDir) if (path.isdir(path.join(self.branchDir, dirName))) ]
		
		#ritorno una tupla di "chageset - data creazione - commento"
		results = ()
		for dir in dirs:
			#prendo il path della cartella del changeset
			dirPath = path.join(self.branchDir, dir)
			#prendo la data di creazione del changeset
			date = datetime.datetime.fromtimestamp(path.getctime(dirPath)).strftime("%Y-%m-%d %H:%M:%S")
			#prendo il commento dal file del changeset
			comment = uti.readFileByTag("comment", self.getChangeset(int(dir)).changesetTxt)
			#aggiungo il changeset e le sue statistiche
			results = results + ("{} - {} - {} ".format(dir, str(date), comment),)

		return results

	
	#copia l'ultima versione completa nella cartella destDir
	def getLatestVersion(self, destDir):
		
		#prendo l'ultimo changeset
		lastChangeset = self.getLastChangesetNum()
		
		#prendo la versione associata all'ultimo changeset
		self.getSpecificVersion(lastChangeset, destDir)

	
	#copia la versione completa fino al "changesetNum" nella cartella destDir
	def getSpecificVersion(self, changesetNum, destDir):
		
		#scorro tutti i changeset all'indietro fino al primo changeset di backup
		for changesetID in range(changesetNum, -1, -1):
			currChangeset = Changeset(path.join(self.branchDir, str(changesetID)))
			if(currChangeset.isBackup()):
				break

		#copio tutto il changeset di backup nella cartella provvisoria
		dir_uti.copy_tree(currChangeset.changesetDir, destDir)

		#scorro tutti i changeset successivi e copio i file presenti nella cartella temporanea
		for changesetID in range(int(path.basename(currChangeset.changesetDir)) + 1, changesetNum + 1):
			currChangeset = Changeset(path.join(self.branchDir, str(changesetID)))
			#copia di tutti i file e sottocartelle contenute nella cartella sourceDir dentro la cartella destDir
			dir_uti.copy_tree(currChangeset.changesetDir, destDir)

		os.remove(path.join(destDir, "changeset.txt"))