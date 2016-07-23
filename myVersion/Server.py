#creazione repo OK
#creazione repo esistente OK
#creazione più repo OK
#creazione di repo da cartelle e cartelle con sottcartelle OK
#creazione branch OK
#creazione branch esistente OK
#creazione nuovo changeset OK (add OK - edit OK)
#implementare la getlatestversion OK
#creare backup con getlatestversion OK
"""Server v1.0.0
- creazione nuovo repo
- creazione repo esistente
- creazione di più repo
- creazione di repo da sorgenti con cartelle e sottocartelle
- creazione trunk
- creazione nuovo branch
- creazione branch esistente
- creazione nuovo changeset da cartella esterna con soli file modificati
	+ file aggiuntivi
	+ file modificati
- implementazione della GetLatestVersion, copia di tutti i changeset fino a quello di backup
"""

"""TODO:
- rimozione repo/branch
- creazione changeset di backup
- gestione file rimossi (si potrebbero semplicemente scrivere nel file della cartella del commit - oppure aggiungere un estensione alla fine e quando si fa il commit rimuoverli tutti)
"""

#######
import os
import os.path as path
#import shutil
import distutils.dir_util as dir_uti
from Repository import Repository


###################################

"""QUESTA DOVRA' ESSERE LA CLASSE CHE SI INTERFACCIA DIRETTAMENTE AL CLIENT"""


#copia la cartella del repository nella cartella di destinazione
def mapRepository(repoName, destDir):
	try:
		getRepo(repoName)
		os.makedirs(destDir)
	except:
		raise


#copia la cartella del branch nella cartella di destinazione
def mapBranch(repoName, branchName, destDir):
	#prendo la cartella del repository e al suo interno quella del branch 
	#quindi prendo la LatestVersion del branch e la copio nella cartella di destinazione
	try:	
		getRepo(repoName).getBranch(branchName).getLatestVersion(destDir)
	except:
		raise


#ritorna la lista di repository sul server
def showRepos():
	return getRepoList()


#ritorna la lista di branch nel repository "repoName"
def showBranches(repoName):
	return getRepo(repoName).getBranchList()


#ritorna True se il repository è presente sul disco, False altrimenti
def existsRepo(repoName):
	if(path.isdir(path.join(myRoot, repoName))):
		return True;

	return False;


#ritorna il repository "repoName", se non esiste solleva un'eccezione
def getRepo(repoName):
	if(existsRepo(repoName)):
		return Repository(path.join(myRoot, repoName))

	raise Exception("Il repository non esiste.");


#ritorna la lista di repository presenti
def getRepoList():
	#prendo il contenuto della root
	#seleziono solo le cartelle (i repository)
	return [name for name in os.listdir(myRoot) 
					if path.isdir(path.join(myRoot, name))]
		 

#se il repository esiste già viene ritornato e viene sollevata un'eccezione, 
#altrimenti viene creato un nuovo repository copiando il contenuto della sourceDir
def addRepo(sourceDir, repoName = None):
	#se non viene specificato, il nome del repository viene impostato 
	#a quello della sourceDir
	if(repoName == None):
		repoName = path.basename(sourceDir)

	#creo un oggetto repository
	repo = Repository(path.join(myRoot, repoName))

	#creo un repository sul disco
	#se già presente sollevo un'eccezione
	try:
		repo.createNew(sourceDir)
	except:
		raise 

	return repo

#rimuove un repository
def removeRepo(repoName):
	if(existsRepo(repoName)):
		dir_uti.remove_tree(path.join(myRoot, repoName))


###############################

### MAIN ###

myRoot = "C:/Users/Gioele/Desktop/myServer"	#cartella di default dei repository creati
"""
if(path.exists(myRoot)):
	#shutil.rmtree(myRoot)
	dir_uti.remove_tree(myRoot)
	

####

#creazione nuovo repository

sourceDir = "C:/Users/Gioele/Desktop/proj"
repo = addRepo(sourceDir)

trunk = repo.getTrunk()
try:
	trunk2 = addRepo(sourceDir).getTrunk()
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
trunk.addChangeset("C:/Users/Gioele/Desktop/proj_edit1")


####
#getLatestVersion
tmpDir = "C:/Users/Gioele/Desktop/my_tmp"
if(path.exists(tmpDir)):
	#shutil.rmtree(tmpDir)
	dir_uti.remove_tree(tmpDir)
trunk.getLatestVersion(tmpDir)

"""