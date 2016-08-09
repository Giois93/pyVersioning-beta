import os
import os.path as path
import shutil
from Repository import Repository


###################################

class Server:

	myRoot = ""

	def __init__(self):
		self.myRoot = "C:/myServer"	#cartella di default dei repository creati


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


	#funzione di test per il server standalone
	def runTest(self):

		if (path.exists(self.myRoot)):
			shutil.rmtree(self.myRoot)
		
		#creazione nuovo repository
		sourceDir = "C:\proj"
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
		trunk.addChangeset("C:\proj_edit1", "commento_1")


		####
		#getLatestVersion
		tmpDir = "C:\my_tmp"
		if (path.exists(tmpDir)):
			shutil.rmtree(tmpDir)
		trunk.getLatestVersion(tmpDir)
