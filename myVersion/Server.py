import os
import os.path as path
import shutil
import rpyc
import uti
from uti import TMP_DIR
from rpyc.utils.server import ThreadedServer
from Repository import Repository


###################################

class Server(rpyc.Service):

	#attributi
	root = "C:\pyV\pyVServer"

	### Client-Server ###

	def on_connect(self):
		print("\nClient connesso.")


	def on_disconnect(self):
		print("\nClient disconnesso.")


	### metodi di interfaccia Client-Server rpyc ###
	class exposed_File():

		def exposed_open(self, filePath, mode="r"):
			self.filePath = filePath
			self.file = open(filePath, mode)

		def exposed_write(self, bytes):
			return self.file.write(bytes)

		def exposed_read(self, bytes):
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


	def exposed_addRepo(self, sourceDir, repoName = None):
		self.addRepo(sourceDir, repoName)

	
	def exposed_removeRepo(self, repoName):
		self.removeRepo(repoName)


	def exposed_existsBranch(self, repoName, branchName):
		return self.getRepo(repoName).existsBranch(branchName)

	
	def exposed_addBranch(self, repoName, branchName):
		"""crea un nuovo branch"""

		self.getRepo(repoName).addBranch(branchName)


	def exposed_removeBranch(self, repoName, branchName):
		"""rimuove il branch"""
		
		self.getRepo(repoName).removeBranch(branchName)


	def exposed_mapBranch(self, repoName, branchName, destDir):
		self.mapBranch(repoName, branchName, destDir)


	def exposed_addChangeset(self, repoName, branchName, sourceDir, comment):
		"""aggiunge un changeset copiandoci il contenuto della sourceDir"""

		return self.getRepo(repoName).getBranch(branchName).addChangeset(sourceDir, comment)
		

	def exposed_existsChangeset(self, repoName, branchName, changesetNum):
		"""ritorna True se esiste il changeset "changesetNum" nel branch "branchName" """

		try:
			self.getRepo(repoName).getBranch(branchName).getChangeset(changesetNum)
			return True
		except:
			return False


	def exposed_listDir(self, dir):

		#scarico l'ultima versione in una cartella temporanea
		list = uti.listDir(dir)
		
		return list


	def exposed_listBranch(self, repoName, branchName):
		"""ritorna tutti i file e sottocartelle del branch selezionato"""

		branch = self.getRepo(repoName).getBranch(branchName)
		tmpDir = path.join(branch.branchDir, TMP_DIR)
		if (path.isdir(tmpDir)):
			shutil.rmtree(tmpDir)
		os.makedirs(tmpDir)

		branch.getLatestVersion(tmpDir)

		list = self.exposed_listDir(tmpDir)
		#rimuovo la cartella temporanea
		shutil.rmtree(tmpDir)

		for elem in list:
			elem.replace(tmpDir, "")

		return list


	def exposed_showRepos(self):
		"""ritorna la lista di repository sul server"""

		return self.getRepoList()


	def exposed_showBranches(self, repoName):
		"""ritorna la lista di branch nel repository "repoName" """

		return self.getRepo(repoName).getBranchList()


	def exposed_showChangesets(self, repoName, branchName):
		"""ritorna la lista di changeset nel branch "branchName" """
		
		return self.getRepo(repoName).getBranch(branchName).getChangesetList()


	def exposed_getLatestVersion(self, repoName, branchName):
		"""scarica l'ultima versione del branch "branchName" nella cartella in una cartella temporanea """

		branch = self.getRepo(repoName).getBranch(branchName)
		destDir = path.join(branch.branchDir, TMP_DIR)
		if (path.isdir(destDir)):
			shutil.rmtree(destDir)

		lastChangesetNum = self.getRepo(repoName).getBranch(branchName).getLatestVersion(destDir)

		return (destDir, lastChangesetNum)


	def exposed_getSpecificVersion(self, repoName, branchName, changesetNum):
		"""scarica la versiona aggiornata al changeset "changesetNum" del branch "branchName" in una cartella temporanea """

		branch = self.getRepo(repoName).getBranch(branchName)
		destDir = path.join(branch.branchDir, TMP_DIR)
		if (path.isdir(destDir)):
			shutil.rmtree(destDir)
		
		self.getRepo(repoName).getBranch(branchName).getSpecificVersion(changesetNum, destDir), 
		
		return destDir


	def getRepoList(self):
		"""ritorna la lista di repository presenti"""

		#prendo il contenuto della root
		#seleziono solo le cartelle (i repository)
		return [name for name in os.listdir(self.root) 
						if path.isdir(path.join(self.root, name))]


	def existsRepo(self, repoName):
		"""ritorna True se il repository è presente sul disco, False altrimenti"""

		if (path.isdir(path.join(self.root, repoName))):
			return True;

		return False;


	def getRepo(self, repoName):
		"""ritorna il repository "repoName", se non esiste solleva un'eccezione"""
		
		if (self.existsRepo(repoName)):
			return Repository(path.join(self.root, repoName))

		raise Exception("Il repository non esiste.");



	def addRepo(self, sourceDir, repoName = None):
		"""viene creato un nuovo repository copiando il contenuto della sourceDir, 
		se il repository esiste già viene sollevata un'eccezione"""

		#se non viene specificato, il nome del repository viene impostato 
		#a quello della sourceDir
		if (repoName == None):
			repoName = path.basename(sourceDir)

		#creo un oggetto repository
		repo = Repository(path.join(self.root, repoName))

		#creo un repository sul disco
		#se già presente sollevo un'eccezione
		try:
			repo.createNew(sourceDir)
		except:
			raise 

		return repo


	def removeRepo(self, repoName):
		"""rimuove un repository"""

		if (self.existsRepo(repoName)):
			shutil.rmtree(path.join(self.root, repoName))


	def mapBranch(self, repoName, branchName, destDir):
		"""copia la cartella del branch nella cartella di destinazione"""

		#prendo la cartella del repository e al suo interno quella del branch 
		#quindi prendo la LatestVersion del branch e la copio nella cartella di destinazione
		try:	
			self.getRepo(repoName).getBranch(branchName).getLatestVersion(destDir)
		except:
			raise


	def findFile(self, repoName, branchName, fileRelPath, startChangeset=None):
		"""prende in input il path relativo di un file e restituisce il path del file corrispondente sul server"""
		
		#prendo il branch corrente
		branch = self.getRepo(repoName).getBranch(branchName)
		
		#se non diversamente specificato, la ricerca parte dall'ultimo changeset
		if (startChangeset == None):
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
				break

		return serverFile


### Main ###
if __name__ == "__main__":
	print("Benvenuto su pyVersioning (Server) - Beta")
	print("Avvio servizio in corso...")
	server = ThreadedServer(Server, port = 18812)
	print("Server attivo.")	
	server.start()