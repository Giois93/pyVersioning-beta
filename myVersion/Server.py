import os
import os.path as path
import shutil
import rpyc
from rpyc.utils.server import ThreadedServer
from Repository import Repository


###################################

class Server(rpyc.Service):

	#attributi
	myRoot = "C:\my\myServer"

	### Client-Server ###

	def on_connect(self):
		print("\nClient connesso.")


	def on_disconnect(self):
		print("\nClient disconnesso.")


	#metodi di interfaccia
	def exposed_findFile(self, repoName, branchName, fileRelPath, startChangeset=None):
		return findFile(repoName, branchName, fileRelPath, startChangeset)
	

	def exposed_existsRepo(self, repoName):
		return self.existsRepo(repoName)


	def exposed_getRepo(self, repoName):
		return self.getRepo(repoName)


	def exposed_addRepo(self, sourceDir, repoName = None):
		self.addRepo(sourceDir, repoName)


	def exposed_removeRepo(self, repoName):
		self.removeRepo(repoName)


	def exposed_mapBranch(self, repoName, branchName, destDir):
		self.mapBranch(repoName, branchName, destDir)

	
	#ritorna la lista di repository sul server
	def exposed_showRepos(self):
		return self.getRepoList()


	#ritorna la lista di branch nel repository "repoName"
	def exposed_showBranches(self, repoName):
		return self.getRepo(repoName).getBranchList()


	#ritorna la lista di repository presenti
	def getRepoList(self):
		#prendo il contenuto della root
		#seleziono solo le cartelle (i repository)
		return [name for name in os.listdir(self.myRoot) 
						if path.isdir(path.join(self.myRoot, name))]


	#ritorna True se il repository è presente sul disco, False altrimenti
	def existsRepo(self, repoName):
		if (path.isdir(path.join(self.myRoot, repoName))):
			return True;

		return False;


	#ritorna il repository "repoName", se non esiste solleva un'eccezione
	def getRepo(self, repoName):
		if (self.existsRepo(repoName)):
			return Repository(path.join(self.myRoot, repoName))

		raise Exception("Il repository non esiste.");


	#se il repository esiste già viene ritornato e viene sollevata un'eccezione, 
	#altrimenti viene creato un nuovo repository copiando il contenuto della sourceDir
	def addRepo(self, sourceDir, repoName = None):
		#se non viene specificato, il nome del repository viene impostato 
		#a quello della sourceDir
		if (repoName == None):
			repoName = path.basename(sourceDir)

		#creo un oggetto repository
		repo = Repository(path.join(self.myRoot, repoName))

		#creo un repository sul disco
		#se già presente sollevo un'eccezione
		try:
			repo.createNew(sourceDir)
		except:
			raise 

		return repo


	#rimuove un repository
	def removeRepo(self, repoName):
		if (self.existsRepo(repoName)):
			shutil.rmtree(path.join(self.myRoot, repoName))


	#copia la cartella del branch nella cartella di destinazione
	def mapBranch(self, repoName, branchName, destDir):
		#prendo la cartella del repository e al suo interno quella del branch 
		#quindi prendo la LatestVersion del branch e la copio nella cartella di destinazione
		try:	
			self.getRepo(repoName).getBranch(branchName).getLatestVersion(destDir)
		except:
			raise


	#prende in input il path relativo di un file e restituisce il path del file corrispondente sul server
	def findFile(self, repoName, branchName, fileRelPath, startChangeset=None):
		
		#prendo il branch corrente
		branch = self.getRepo(repoName).getBranch(branchName)
		
		#se non diversamente specificato, la ricerca parte dall'ultimo changeset
		if (startChangeset == None):
			startChangeset = branch.getLastChangesetNum()

		#scorro tutti i changeset presenti nella cartella del branch a partire da quello specificato
		for changesetID in range(startChangeset, -1, -1):
			changeset = branch.getChangeset(changesetID)

			#prendo il changeset precedente (più recente) e verifico se è un changeset di backup
			prevChangeset = branch.getChangeset(changesetID + 1) 

			#se il changeset precedente era un changeset di backup e non ho ancora trovato il file
		    #vuol dire che il file non è presente sul server
			if (prevChangeset.isBackup()):
				raise Exception("File non trovato")

			#ricavo il path del file sul server
			serverFile = path.join(changeset.changesetDir, fileRelPath)
				
			#se il file esiste in questo branch interrompo la ricerca
			if (path.isfile(serverFile)):
				break

		return serverFile


### Main ###
if __name__ == "__main__":
	print("Benvenuto su MyVersion (Server)")
	print("Avvio servizio in corso...")
	server = ThreadedServer(Server, port = 18812)
	print("Server attivo.")	
	server.start()