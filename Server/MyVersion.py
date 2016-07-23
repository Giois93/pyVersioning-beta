import os
import os.path as path
import distutils.dir_util as dir_uti
from Repository import Repository


class MyVersion:
	
	myRoot = ""	#cartella di default dei repository creati


	def __init__(self, root):
		self.myRoot = root


	#ritorna True se il repository è presente sul disco, False altrimenti
	def existsRepo(self, repoName):
		if(path.isdir(path.join(self.myRoot, repoName))):
			return True;

		return False;


	#ritorna il repository "repoName", se non esiste solleva un'eccezione
	def getRepo(self, repoName):
		if(self.existsRepo(repoName)):
			return Repository(repoName)

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
		if(repoName == None):
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
		if(self.existsRepo(repoName)):
			dir_uti.remove_tree(path.join(self.myRoot, repoName))
