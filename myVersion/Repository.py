import os 
import os.path as path
import shutil
import distutils.dir_util as dir_uti
import uti
from uti import TMP_DIR
from uti import TRUNK
from Branch import Branch

class Repository:
	    
	repoName = ""	#nome del repository
	repoDir = ""	#path del repository


	def __init__(self, repoDir):
		self.repoName = path.basename(repoDir)
		self.repoDir = repoDir


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


	def getBranchList(self):
		"""ritorna la lista di branch presenti"""

		#prendo il contenuto della root
		#seleziono solo le cartelle (i branch)
		return [name for name in os.listdir(self.repoDir) 
						if path.isdir(path.join(self.repoDir, name))]


	def addBranch(self, branchName, isTrunk=False):
		"""crea un nuovo branch copiando il contenuto del trunk
		se il branch esiste già viene sollevata un'eccezione"""

		#creo il percorso del nuovo branch
		#creo il branch
		branch = Branch(path.join(self.repoDir, branchName))
		if (path.isdir(branch.branchDir)):
			raise Exception

		os.makedirs(branch.branchDir)

		#se sto creando il trunk, creo il primo changeset vuoto, il chiamante deve riempirlo
		if (isTrunk):
			changeset = branch.addChangeset("branch created")

		#se sto creando un branch, copio l'ultima versione del trunk
		else:
			try:
				#prendo il trunk
				trunk = Branch(path.join(self.repoDir, TRUNK))
				#ottengo la LatestVersion e la copio nella cartella temporanea
				tmpDir = trunk.getLatestVersion()
				#creo il branch sul disco e ci copio il contenuto della cartella temporanea
				changeset = branch.addChangeset("branch created", trunk.getLastChangesetNum()) 
				dir_uti.copy_tree(tmpDir, changeset.changesetDir)
			except:
				raise

		#setto il primo changeset come changeset di backup
		uti.writeFileByTag("is_backup", 1, changeset.changesetTxt)


	def removeBranch(self, branchName):
		"""rimuove il branch "branchName" """

		if (self.existsBranch(branchName)):
			if (branchName == TRUNK):
				raise Exception("Impossibile eliminare il ramo \"trunk\"")
			shutil.rmtree(path.join(self.repoDir, branchName))