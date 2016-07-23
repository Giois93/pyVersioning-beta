import os 
import os.path as path
import distutils.dir_util as dir_uti
from Branch import Branch

class Repository:
	    
	repoName = ""	#nome del repository
	repoDir = ""	#path del repository
	trunkDir = ""	#path del trunk


	def __init__(self, repoDir):
		self.repoName = path.basename(repoDir)
		self.repoDir = repoDir


	#crea un nuovo repository sul disco e crea il ramo trunk
	#se esiste già solleva un'eccezione
	def createNew(self, sourceDir):
		if(path.isdir(self.repoDir)):
			raise Exception

		self.addTrunk(sourceDir)


	#ritorna True se il branch è presente sul disco, False altrimenti
	def existsBranch(self, branchName):
		if(path.isdir(path.join(self.repoDir, branchName))):
			return True;

		return False;


	#ritorna il Branch "branchName", se non esiste solleva un'eccezione
	def getBranch(self, branchName):
		if(self.existsBranch(branchName)):
			return Branch(path.join(self.repoDir, branchName))

		raise Exception("Il branch non esiste.");


	#ritorna il trunk (il nome della cartella è fisso a "trunk")
	def getTrunk(self):
		return self.getBranch("trunk")


	#ritorna la lista di branch presenti
	def getBranchList(self):
		#prendo il contenuto della root
		#seleziono solo le cartelle (i branch)
		return [name for name in os.listdir(self.repoDir) 
						if path.isdir(path.join(self.repoDir, name))]


	#crea un nuovo branch copiando il contenuto della sourceDir
	#se il branch esiste già viene sollevata un'eccezione
	def addTrunk(self, sourceDir):
		#creo un'oggetto Branch per il ramo trunk
		self.trunkDir = path.join(self.repoDir, "trunk")
		branch = Branch(self.trunkDir)
		
		#creo un branch sul disco
		#se già presente sollevo un'eccezione
		try:
			branch.createNew(sourceDir)
		except:
			raise 

		return branch


	#crea un nuovo branch copiando il contenuto del trunk
	#se il branch esiste già viene sollevata un'eccezione
	def addBranch(self, branchName):
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
			dir_uti.remove_tree(tmpDir)
		except:
			raise

		return branch

	#rimuove il branc "branchName"
	def removeBranch(self, branchName):
		if(self.existsBranch(branchName)):
			dir_uti.remove_tree(path.join(self.repoDir, branchName))