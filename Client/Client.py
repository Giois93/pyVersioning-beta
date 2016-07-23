"""TODO
Client v0.1.0
- cartella root
- lista dei repo
- lista dei branch
- map di un repository
- map di un branch
- rimozione map di un repository
- rimozione map di un branch
- getlatest
- checkout di file (segnare nel file .txt i file checkati out)
- checkin (copia dei file in pending nella cartella pending_changes temporanea nel branch)
- undo (rimozione di record dal file)
- compare (richiede una copia temporanea del file dal server)
- takeServerVersion
- takeLocalVersion

"""

import os
import os.path as path
import distutils.dir_util as dir_uti
import Server
import uti

#il client non deve gestire repository o branch, forse non servono le classi corrispondenti?
#però deve potere selezionare quale branch usare (basta selezionare la cartella?)

root = "D:\my"
#if(path.exists(root)):
#	dir_uti.remove_tree(root)
#my = MyVersion(root)

#mostra la lista dei repository presenti sul server
def showRepos():
	print("List of repositories on MyVersion server")
	print(Server.showRepos())
	#for repoDir in Server.showRepos():
	#	print(repoDir)


#mostra la lista dei branch presenti sul server
def showBranches(repoName):
	print("List of branches on Repository: {}", repoName)
	print(Server.showBranches(repoName))
	#for branchDir in Server.showBranches():
	#	print(branchDir)


#mappa il repository nella cartella del client
def mapRepository(repoName):

	#ottengo il path del repository
	clientDir = path.join(root, repoName)

	#chiedo all'utente se sovrascrivere la cartella
	if(uti.askAndRemoveDir(clientDir, True)):
		#mappo il repository nella cartella del client
		Server.mapRepository(repoName, clientDir)


#mappa il branch nella cartella del client
def mapBranch(repoName, branchName):

	#ottengo il path del branch
	clientDir = path.join(root, repoName, branchName)

	#chiedo all'utente se sovrascrivere la cartella
	if(uti.askAndRemoveDir(clientDir, True)):
		#mappo il branch nella cartella del client
		Server.mapBranch(repoName, branchName, clientDir)


#rimuove la cartella del repo sul client
def removeRepositoryMap(repoName):
	uti.askAndRemoveDir(path.join(root, repoName))


#rimuove la cartella del branch sul client
def removeBranchMap(repoName, branchName):
	uti.askAndRemoveDir(path.join(root, repoName, branchName))


#######################
"""OLD

def menu(userInput):

	#prendo l'input dell'utente ed eseguo l'azione corrispondente, default: -1
	menu =	{	-1: print("Valore non ammesso"),
				0 : print("Programma terminato"),
				1 : showRepos(),
				2 : showBranches(),
				3 : mapRepository(uti.askRepoName()),
				4 : mapBranch(uti.askRepoName(), uti.askBranchName()),
				5 : removeRepositoryMap(path.join(root, uti.askRepoName())),
				6 : removeBranchMap(path.join(root, uti.askRepoName(), uti.askBranchName()))
			}.get(userInput, -1)

	return userInput


########### MAIN #############
#chiedo all'utente cosa fare
print("Benvenuto su MyVersion")

while True:
	print("Digitare:")
	print("0. Uscire")
	print("1. Lista dei repository")
	print("2. Lista dei branch")
	print("3. Mappare un repository")
	print("4. Mappare un branch")
	print("5. Rimuovere un repository")
	print("6. Rimuovere un branch")

	#esego il comando richiesto, altrimenti termino il ciclo
	if(menu(int(input())) == 0):
		break

"""
######
"""NEW"""

def menuMyVersion():
	while True:
		print("> ", end="")
		userInput = input()
		menu(userInput)

		if(userInput == 0):
			break


def menu(userInput):
	#costruisco una lista di comando e argomenti
	commandList = userInput.split().reverse()

	#eseguo l'azione corrispondente al comando, default: "None"
	menu =	{	"none"			: print("Valore non ammesso"),
				"exit"			: print("Programma terminato"),
				"repolist"		: showRepos(),
				"branchlist"	: showBranches(),
				"maprepo"		: mapRepository(commandList.pop()),
				"mapbranch"		: mapBranch(commandList.pop(), commandList.pop()),
				"delrepo"		: removeRepositoryMap(commandList.pop()),
				"delbranch"		: removeBranchMap(commandList.pop(), commandList.pop()),
			}.get(commandList.pop(), -1)
	
	"""COMANDI:
	> exit
	> repolist
	> branchlist
	> maprepo [repoName]
	> mapbranch [repoName] [branchName]
	> delrepo [repoName]
	> delbranch [repoName] [branchName]
	"""


"""QUESTA DOVRA' ESSERE LA CLASSE CHE SI INTERFACCIA DIRETTAMENTE AL SERVER"""
#TODO: comunicazione con il server e ftp