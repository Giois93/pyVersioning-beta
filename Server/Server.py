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

import os.path as path
import shutil
import distutils.dir_util as dir_uti
from MyVersion import MyVersion

###
#installazione cartella root
"""
print("Digitare la cartella di installazione:")
root = str(input())
"""
root = "C:\my"
if(path.exists(root)):
	#shutil.rmtree(root)
	dir_uti.remove_tree(root)
my = MyVersion(root)

####

#creazione nuovo repository
"""
print("Digitare la cartella di origine:")
sourceDir = str(input())
"""
sourceDir = "C:\proj"
repo = my.addRepo(sourceDir)

trunk = repo.getTrunk()
try:
	trunk2 = my.addRepo(sourceDir).getTrunk()
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
trunk.addChangeset("C:\proj_edit1")


####
#getLatestVersion
tmpDir = "C:\my_tmp"
if(path.exists(tmpDir)):
	#shutil.rmtree(tmpDir)
	dir_uti.remove_tree(tmpDir)
trunk.getLatestVersion(tmpDir)



###################################
"""QUESTA DOVRA' ESSERE LA CLASSE CHE SI INTERFACCIA DIRETTAMENTE AL CLIENT"""

#copia la cartella del repository nella cartella di destinazione
def mapRepository(repoName, destDir):
	dir_uti.copy_tree(my.getRepo(repoName).repoDir, destDir)


#copia la cartella del branch nella cartella di destinazione
def mapBranch(repoName, branchName, destDir):
	#prendo la cartella del repository e al suo interno quella del branch quindi copio la cartella del branch nella cartella di destinazione
	dir_uti.copy_tree(path.join(my.getRepo(repoName).repoDir, branchName), destDir)
	return


#ritorna la lista di repository sul server
def showRepos():
	return my.getRepoList()


#ritorna la lista di branch nel repository "repoName"
def showBranches(repoName):
	return my.getRepo(repoName).getBranchList()