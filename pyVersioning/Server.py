import os
import os.path as path
import shutil
import rpyc
import uti
from consts import *
from rpyc.utils.server import ThreadedServer
from Repository import Repository

class Server(rpyc.Service):

	#attributi
	root = "C:\pyV\pyVServer"

	### Client-Server ###

	def on_connect(self):
		print("\nClient connesso.")


	def on_disconnect(self):
		print("\nClient disconnesso.")


	### metodi di interfaccia Client-Server rpyc ###
	class exposed_File:
		filePath = ""
		file = ""

		def exposed_open(self, filePath, mode="r"):
			self.filePath = filePath
			self.file = open(filePath, mode, errors="ignore")

		def exposed_write(self, stream):
			return self.file.write(stream)

		# noinspection PyUnusedLocal
		def exposed_read(self, stream):
			return self.file.read()

		def exposed_close(self):
			return self.file.close() 

		def exposed_getmtime(self):
			return path.getmtime(self.filePath)


	def exposed_findFile(self, repoName, branchName, fileRelPath, startChangeset=None):
		return self.findFile(repoName, branchName, fileRelPath, startChangeset)
	

	def exposed_existsRepo(self, repoName):
		return self.existsRepo(repoName)


	def exposed_existsBranch(self, repoName, branchName):
		return self.getRepo(repoName).existsBranch(branchName)


	def exposed_getRepo(self, repoName):
		return self.getRepo(repoName)


	def exposed_addRepo(self, repoName):
		"""crea un nuovo repository, il trunk e il changeset 0, ritorna la directory del changeset 0"""

		self.addRepo(repoName)
		return self.getRepo(repoName).getBranch(TRUNK).getChangeset(0).changesetDir

	
	def exposed_removeRepo(self, repoName):
		self.removeRepo(repoName)


	def exposed_addBranch(self, repoName, branchName):
		"""crea un nuovo branch"""

		self.getRepo(repoName).addBranch(branchName)


	def exposed_removeBranch(self, repoName, branchName):
		"""rimuove il branch"""
		
		self.getRepo(repoName).removeBranch(branchName)


	def exposed_addChangeset(self, repoName, branchName, comment):
		"""aggiunge un changeset al branch "branchName" """

		return self.getRepo(repoName).getBranch(branchName).addChangeset(comment).changesetDir
		

	def exposed_existsChangeset(self, repoName, branchName, changesetNum):
		"""ritorna True se esiste il changeset "changesetNum" nel branch "branchName" """

		try:
			self.getRepo(repoName).getBranch(branchName).getChangeset(changesetNum)
			return True
		except:
			return False

	# noinspection PyMethodMayBeStatic
	def exposed_listDir(self, dirPath):
		return uti.listDir(dirPath)


	def exposed_listBranch(self, repoName, branchName):
		"""ritorna tutti i file e sottocartelle del branch selezionato"""
		
		#creo una versione completa in una cartella temporanea
		tmpDir = self.getRepo(repoName).getBranch(branchName).getLatestVersion()

		#memorizzo una lista dei file nella versione
		filesList = self.exposed_listDir(tmpDir)

		#rimuovo la cartella temporanea
		shutil.rmtree(tmpDir)

		#formatto i path dei file per la stampa
		return [elem.replace(tmpDir,"") for elem in filesList]
		

	def exposed_showRepos(self):
		"""ritorna la lista di repositories sul server"""

		return self.getRepoList()


	def exposed_showBranches(self, repoName):
		"""ritorna la lista di branch nel repository "repoName" """

		return self.getRepo(repoName).getBranchList()


	def exposed_showChangesets(self, repoName, branchName):
		"""ritorna la lista di changeset nel branch "branchName" con i file modificati"""
		
		return self.getRepo(repoName).getBranch(branchName).getChangesetList()


	def exposed_getLatestVersion(self, repoName, branchName):
		"""scarica l'ultima versione del branch "branchName" in una cartella temporanea """
		branch = self.getRepo(repoName).getBranch(branchName)

		return branch.getLatestVersion(), branch.getLastChangesetNum()


	def exposed_getSpecificVersion(self, repoName, branchName, changesetNum):
		"""scarica la versiona aggiornata al changeset "changesetNum" del branch "branchName" in una cartella temporanea """

		return self.getRepo(repoName).getBranch(branchName).getSpecificVersion(changesetNum)
		

	def exposed_getLastChangeset(self, repoName, branchName):
		"""ritorna l'ultimo changeset del branch"""
		return self.getRepo(repoName).getBranch(branchName).getLastChangesetNum()


	def getRepoList(self):
		"""ritorna la lista di repository presenti"""

		#prendo il contenuto della root
		#seleziono solo le cartelle (i repository)
		return [name for name in os.listdir(self.root) 
						if path.isdir(path.join(self.root, name))]


	def existsRepo(self, repoName):
		"""ritorna True se il repository è presente sul disco, False altrimenti"""

		if (path.isdir(path.join(self.root, repoName))):
			return True

		return False

	def getRepo(self, repoName):
		"""ritorna il repository "repoName", se non esiste solleva un'eccezione"""
		
		if (self.existsRepo(repoName)):
			return Repository(path.join(self.root, repoName))

		raise Exception("Il repository non esiste.")

	def addRepo(self, repoName):
		"""viene creato un nuovo repository, se il repository esiste già viene sollevata un'eccezione"""

		#creo un oggetto repository
		repo = Repository(path.join(self.root, repoName))
		if (path.isdir(repo.repoDir)):
			raise Exception

		os.makedirs(repo.repoDir)

		#creo il trunk - se già presente sollevo un'eccezione
		repo.addBranch(TRUNK, isTrunk=True)


	def removeRepo(self, repoName):
		"""rimuove un repository"""

		if (self.existsRepo(repoName)):
			shutil.rmtree(path.join(self.root, repoName))


	def findFile(self, repoName, branchName, fileRelPath, startChangeset=None):
		"""prende in input il path relativo di un file e restituisce il path del file corrispondente sul server"""
		
		#prendo il branch corrente
		branch = self.getRepo(repoName).getBranch(branchName)
		
		#se non diversamente specificato, la ricerca parte dall'ultimo changeset
		if (startChangeset is None):
			startChangeset = branch.getLastChangesetNum()

		#scorro tutti i changeset presenti nella cartella del branch a partire da quello specificato
		for changesetID in range(startChangeset, -1, -1):
			changeset = branch.getChangeset(changesetID)

			try:
				#prendo il changeset precedente (più recente) e verifico se è un changeset di backup
				prevChangeset = branch.getChangeset(changesetID + 1) 

				#se il changeset precedente era un changeset di backup e non ho ancora trovato il file
				#vuol dire che il file non è presente sul server
				if (prevChangeset.isBackup()):
					raise Exception("File non trovato")
			except:
				pass

			#ricavo il path del file sul server
			serverFile = path.join(changeset.changesetDir, fileRelPath)
				
			#se il file esiste in questo branch interrompo la ricerca
			if (path.isfile(serverFile)):
				return serverFile


### Main ###
if __name__ == "__main__":
	print("Benvenuto su pyVersioning (Server)")
	
	#creo la cartella di installazione se non presente
	root = "C:\pyV\pyVServer"
	if (path.isdir(root) == False):
		os.makedirs(root)

	#avvio il servizio rpyc
	print("Avvio servizio in corso...")
	server = ThreadedServer(Server, port = 18812)
	print("Server attivo.")	
	server.start()