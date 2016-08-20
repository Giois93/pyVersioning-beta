import os
import os.path as path
import shutil
import rpyc
from rpyc.utils.server import ThreadedServer
from Repository import Repository


###################################

class Server(rpyc.Service):

	myRoot = "C:\my\myServer"

	#def __init__(self):
	#	self.myRoot = "C:\my\myServer"	#cartella di default dei repository creati

	### esempi rpyc ###
	####
	def exposed_echo(self, text): # this is an exposed method
		return text

	def echo(self, text): # this is an not exposed method
		return text

	def on_connect(self):
        # code that runs when a connection is created
        # (to init the serivce, if needed)
		pass

	def on_disconnect(self):
        # code that runs when the connection has already closed
        # (to finalize the service, if needed)
		pass

	####




	#copia la cartella del branch nella cartella di destinazione
	def mapBranch(self, repoName, branchName, destDir):
		#prendo la cartella del repository e al suo interno quella del branch 
		#quindi prendo la LatestVersion del branch e la copio nella cartella di destinazione
		try:	
			self.getRepo(repoName).getBranch(branchName).getLatestVersion(destDir)
		except:
			raise


	#ritorna la lista di repository sul server
	def showRepos(self):
		return self.getRepoList()


	#ritorna la lista di branch nel repository "repoName"
	def showBranches(self, repoName):
		return self.getRepo(repoName).getBranchList()


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


	#ritorna la lista di repository presenti
	def getRepoList(self):
		#prendo il contenuto della root
		#seleziono solo le cartelle (i repository)
		return [name for name in os.listdir(self.myRoot) 
						if path.isdir(path.join(self.myRoot, name))]
		 

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


	"""
	#funzione di test per il server standalone
	def runTest(self):

		if (path.exists(self.myRoot)):
			shutil.rmtree(self.myRoot)
		
		#creazione nuovo repository
		sourceDir = "C:\my\proj"
		repo = self.addRepo(sourceDir)

		trunk = repo.getTrunk()
		try:
			trunk2 = self.addRepo(sourceDir).getTrunk()
		except:
			pass

		#####
		#creazione changeset
		try:
			branch = repo.getBranch("branch1")
		except:
			branch = repo.addBranch("branch1")
			branch = repo.getBranch("branch1")
	

		#####
		#creazione changeset
		trunk.addChangeset("C:\my\proj_v2", "commento_1")


		#####
		#getLatestVersion
		tmpDir = "C:\my\my_tmp"
		if (path.exists(tmpDir)):
			shutil.rmtree(tmpDir)
		trunk.getLatestVersion(tmpDir)


		#####
		sourceDir = "C:\my\projB"
		self.addRepo(sourceDir, "progetto_2")
	"""


### Main ###
if __name__ == "__main__":
	server = ThreadedServer(Server, port = 18812)
	print("server started")	
	server.start()