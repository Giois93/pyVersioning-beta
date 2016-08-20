import os 
import os.path as path
import shutil
from Branch import Branch

class Repository:
	    
	repoName = ""	#nome del repository
	repoDir = ""	#path del repository
	trunkDir = ""	#path del trunk


	def __init__(self, repoDir):
		self.repoName = path.basename(repoDir)
		self.repoDir = repoDir
		self.trunkDir = path.join(self.repoDir, "trunk")


	def createNew(self, sourceDir):
		"""crea un nuovo repository sul disco e crea il ramo trunk
		se esiste già solleva un'eccezione"""

		if (path.isdir(self.repoDir)):
			raise Exception

		self.addTrunk(sourceDir)


	def existsBranch(self, branchName):
		"""ritorna True se il branch è presente sul disco, False altrimenti"""

		if (path.isdir(path.join(self.repoDir, branchName))):
			return True;

		return False;


	def getBranch(self, branchName):
		"""ritorna il Branch "branchName", se non esiste solleva un'eccezione"""

		if (self.existsBranch(branchName)):
			return Branch(path.join(self.repoDir, branchName))

		raise Exception("Il branch non esiste.");


	def getTrunk(self):
		"""ritorna il trunk (il nome della cartella è fisso a "trunk")"""

		return self.getBranch("trunk")


	def getBranchList(self):
		"""ritorna la lista di branch presenti"""

		#prendo il contenuto della root
		#seleziono solo le cartelle (i branch)
		return [name for name in os.listdir(self.repoDir) 
						if path.isdir(path.join(self.repoDir, name))]



	def addTrunk(self, sourceDir):
		"""crea un nuovo branch copiando il contenuto della sourceDir
		se il branch esiste già viene sollevata un'eccezione"""

		#creo un'oggetto Branch per il ramo trunk
		branch = Branch(self.trunkDir)
		
		#creo un branch sul disco
		#se già presente sollevo un'eccezione
		try:
			branch.createNew(sourceDir)
		except:
			raise 

		return branch



	def addBranch(self, branchName):
		"""crea un nuovo branch copiando il contenuto del trunk
		se il branch esiste già viene sollevata un'eccezione"""

		#creo il percorso del nuovo branch
		branchDir = self.trunkDir.replace("trunk", branchName)
		#creo il branch
		branch = Branch(branchDir)
		
		try:
			#prendo il trunk
			trunk = Branch(self.trunkDir)
			#creo il percorso di una cartella temporanea
			tmpDir = path.join(self.repoDir, "tmp")
			#ottengo la LatestVersion e la copio nella cartella temporanea
			trunk.getLatestVersion(tmpDir)
			#creo il branch sul disco e ci copio il contenuto della cartella temporanea
			branch.createNew(tmpDir, trunk.getLastChangesetNum())
			#rimuovo la cartella temporanea
			shutil.rmtree(tmpDir)
		except:
			raise

		return branch


	def removeBranch(self, branchName):
		"""rimuove il branch "branchName" """

		if (self.existsBranch(branchName)):
			if (branchName == "trunk"):
				raise Exception("Impossibile eliminare il ramo \"trunk\"")
			shutil.rmtree(path.join(self.repoDir, branchName))