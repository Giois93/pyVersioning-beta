"""TODO
Client v0.1.0
- cartella root
- lista dei repo
- lista dei branch
- map di un repository (deve limitarsi a creare la cartella)
- map di un branch (deve limitarsi a creare la cartella)
- rimozione map di un repository
- rimozione map di un branch
- settare/selezionare un repo (serve la classe Repository)
- settare/selezionare un branch (serve la classe Branch)
- getlatest (devo scaricare solo il backup non tutto il branch/repo)
- checkout di file (segnare nel file .txt i file checkati out)
- checkin (copia dei file in pending nella cartella pending_changes temporanea nel branch)
- undo (rimozione di record dal file)
- compare (richiede una copia temporanea del file dal server)
- takeServerVersion
- takeLocalVersion

"""

import os
import os.path as path
import time
import datetime
import shutil
import distutils.dir_util as dir_uti
import uti
from Server import Server

class Client:
	
	myRoot = ""
	currPath = ""
	currRepo = ""
	currBranch = ""
	server = None

	def __init__(self, server):
		self.myRoot = "C:/myClient"
		self.currPath = self.myRoot
		self.server = server

	#mostra la lista dei repository presenti sul server
	def showRepos(self):
		print("\nList of repositories on MyVersion server")
	
		for repo in self.server.showRepos():
			print("- " + repo)
		print()


	#mostra la lista dei branch presenti sul server
	def showBranches(self):
		print("\nList of branches on repository " + self.getCurrRepo() + " : ")
		for branch in self.server.showBranches(self.getCurrRepo()):
			print("- " + branch)
		print()


	#mostra la lista dei changeset presenti in questo branch
	def viewHistory(self):
		print("\nList of changeset on branch " + self.getCurrBranch() + " : ")
		for changeSet in self.getCurrBranchOnServer().getChangesetList():
			print("- " + branch)
		print()


	#mappa il repository nella cartella del client
	def mapRepository(self, repoName):

		#ottengo il path del repository
		clientDir = path.join(self.myRoot, repoName)

		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(clientDir, True)):
			#mappo il repository nella cartella del client
			try:
				#se il repository esiste sul server, creo una cartella sul client
				#altrimenti viene generata un'eccezione
				self.server.getRepo(repoName)
				os.makedirs(clientDir)
				print("Repository mappato in:", clientDir, end = "\n\n")
				
				#setto anche il repository mappato come repository corrente di default
				self.setRepo(repoName)
			except:
				print("Impossibile completare l'operazione", end = "\n\n")


	#mappa il branch nella cartella del client
	def mapBranch(self, branchName):

		#ottengo il path del branch
		clientDir = path.join(self.myRoot, self.getCurrRepo(), branchName)

		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(clientDir, True)):
			#mappo il branch nella cartella del client
			try:
				#se il branch esiste sul server, creo il branch sul client
				#altrimenti viene generata un'eccezione
				#scarico anche la LatestVersion di default
				self.server.mapBranch(self.getCurrRepo(), branchName, clientDir)
				print("Branch mappato in: ", clientDir, end = "\n\n")
				
				#setto anche il branch mappato come branch corrente di default
				self.setBranch(branchName)
			except:
				print("Impossibile completare l'operazione", end = "\n\n")


	#rimuove la cartella del repo sul client
	def removeRepositoryMap(self, repoName):
		uti.askAndRemoveDir(path.join(self.myRoot, repoName))


	#rimuove la cartella del branch sul client
	def removeBranchMap(self, branchName):
		uti.askAndRemoveDir(path.join(self.myRoot, self.getCurrRepo(), branchName))


	#setta il repository corrente
	def setRepo(self, repoName):
		try:
			#verifico se esiste il repository altrimenti viene generata un'eccezione
			self.server.getRepo(repoName)
			#aggiorno il repository corrente
			self.setCurrRepo(repoName)
			#aggiorno la cartella di esecuzione
			repoDir = path.join(self.myRoot, repoName)
			self.setCurrPath(repoDir)
			print("> " + self.getCurrPath() + " : ")
		except:
			print("Il repository", repoName, "non esiste o non è stato mappato") 


	#setta il branch corrente
	def setBranch(self, branchName):
		try:
			#verifico se esiste il branch altrimenti viene generata un'eccezione
			self.getCurrRepoOnServer().getBranch(branchName)
			#aggiorno il branch corrente
			self.setCurrBranch(branchName)
			#aggiorno la cartella di esecuzione
			branchDir = path.join(self.myRoot, self.getCurrRepo(), branchName)
			self.setCurrPath(branchDir)
			print(">", self.getCurrPath(), ": ")
		except:
			print("Il branch", branchName, "non esiste o non è stato mappato")


	#scarica l'ultima versione e la copia nella cartella del branch
	def getLatestVersion(self):
		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(self.getCurrPath())):
			#prendo la latestVersion da Repository e Branch corrente
			self.getCurrBranchOnServer().getLatestVersion(self.getCurrPath())

	
	#scarica una versione specifica (identificata dal numero di changeset) e la copia nella cartella del branch
	def getSpecificVersion(self, changesetNum):
		#chiedo all'utente se sovrascrivere la cartella
		if(uti.askAndRemoveDir(self.getCurrPath())):
			#prendo la versione specifica da Repository e Branch corrente con il numero di changeset passato
			self.getCurrBranchOnServer().getSpecificVersion(changesetNum, self.getCurrPath())


	#stampa una lista dei file modificati in locale con data di ultima modifica
	def printPendingChanges(self):
		#scorro tutti i file nella lista dei pending
		for file in self.getPendingChanges():
			#prendo la data di ultima modifica del file
			date = datetime.datetime.fromtimestamp(path.getmtime(file))
			#stampo file e data ultima modifica
			print(file,replace(self.getCurrPath(), ""), date)


	
	#ritorna una lista dei file modificati in locale
	def getPendingChanges(self):
		#prendo la cartella corrente dal client
		localRoot = self.getCurrPath()

		#prendo la cartella corrente dal server
		serverBranch = self.getCurrBranchOnServer().branchDir

		#scorro tutti i file della cartella
		for dirPath, dirNames, files in os.walk(localRoot):
			for fileName in files:
				localFile = path.join(dirPath, fileName)
				
				try:
					#cerco sul server il file corrispondente al localFile
					serverFile = self.findFileOnServer(localFile, serverBranch)
				
					#confronto le date di ultima modifica dei file
					#se il file locale è stato modificato va aggiunto ai pending
					if((path.getmtime(localFile)) > path.getmtime(serverFile)):
						self.addToPending(localFile)

				except:		
					#se il file non viene trovato nel server vuol dire che è stato aggiunto in locale
					if(found == False):
						self.addPendingFile(localFile, addedFile=True)
		
		#ritorno la lista dei pendig
		return self.getPendingList()


	#aggiunge il file alla lista dei pending
	def addPendingFile(self, file, addedFile=False):
		"""TODO"""
		return


	#rimuove il file alla lista dei pending
	def delPendingFile(self, file):
		"""TODO"""
		return


	#legge il file dei pending e ritorna una lista 
	def getPendingList():
		"""TODO"""
		return
		

	#crea un nuovo changeset con le modifiche dei file in pending
	def commit(self, filePath):
		
		#creo una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), "tmp")

		#scorro tutti i file in pending
		for file in getPendingChanges():
			#copio il file nella cartella temporanea (creo le cartelle se non presenti)
			#prendo il path del file da copiare
			tmpFileDir = path.dirname(file.replace(self.getCurrPath(), tmpDir))
			#se non esiste creo il percorso
			if(path.isdir(tmpFileDir) == False):
				os.makedirs(tmpFileDir)

			#copio il file (con metadati)
			shutil.copy2(file, tmpFileDir)
		
		#creo un nuovo changeset in cui copiare la cartella temporanea
		self.getCurrBranchOnServer().addChangeset(tmpDir)

		#rimuovo la cartella temporanea
		dir_uti.remove_tree(tmpDir)
		
		print("Commit effettuato.")

		#Chiedo all'utente se desidera anche aggiornare la versione locale
		while True:
			print("Scaricare ultima versione? (s/n): ")
			userInput = input()
			if(userInput == "s"):
				self.getLatestVersion()
				break
			elif(userInput == "n"):
				break

						
	#annulla le modifiche sul file e riporta la versione a quella del server
	def undoFile(self, file):
		while True:
			print("Questo comando annullerà le modifiche sul file", file, ", sei sicuro? (s/n) :")
			userInput = input()
			if(userInput == "s"):
				#prendo il file corrispondente dal server e lo sovrascrivo al file locale
				serverFile = self.findFileOnServer(file, self.getCurrBranchOnServer().branchDir)
				shutil.copy2(serverFile, path.dirname(file))
				break
			elif(userInput == "n"):
				break

	
	#annulla tutte le modifiche e riporta la versione a quella del server
	def undoAll(self):
		while True:
			print("Questo comando cancellerà tutti i pending, sei sicuro? (s/n) :")
			userInput = input()
			if(userInput == "s"):
				self.getLatestVersion()
				break
			elif(userInput == "n"):
				break


	#setta il path di esecuzione
	def setCurrPath(self, path):
		self.currPath = path


	#setta il repository selezionato
	def setCurrRepo(self, repoName):
		self.currRepo = repoName


	#setta il branch selezionato
	def setCurrBranch(self, branchName):
		self.currBranch = branchName


	#setta il path di esecuzione
	def getCurrPath(self):
		return self.currPath


	#ritorna il repository selezionato
	def getCurrRepo(self):
		return self.currRepo


	#ritorna il branch selezionato
	def getCurrBranch(self):
		return self.currBranch


	#ritorna il repository del server corrispondente a quello corrente
	def getCurrRepoOnServer(self):
		return self.server.getRepo(self.getCurrRepo())


	#ritorna il branch del server corrispondente a quello corrente
	def getCurrBranchOnServer(self):
		return self.server.getRepo(self.getCurrRepo()).getBranch(self.getCurrBranch())


	#ritorna il percorso del file sul server, il file viene cercato a partire da branchDir
	def findFileOnServer(self, localFile, branchDir):
		
		#scorro tutti i changeset presenti nella cartella del branch a partire dal più recente
		for changeset in os.listdir(branchDir).reverse():
					
			#prendo la cartella del changeset precedente
			prevChangesetDir = path.join(branchDir, int(changeset) - 1)

			#apro il file del changeset precedente
			prevChangesetTxt = path.join(prevChangesetDir, "changeset.txt")
					
			#se l'ultimo changeset era un backup devo interrompere la ricerca
			if(int(uti.readFileByTag("is_backup", prevChangesetTxt)) == 1):
				raise Exception("File non trovato")

			#ricavo la cartella del changeset corrente
			changesetDir = path.join(branchDir, changeset)

			#ricavo il path del file sul server
			serverFile = localFile.replace(localRoot, changesetDir)
				
			#se il file esiste in questo branch interrompo la ricerca
			if(path.isfile(serverFile)):
				break

		return serverFile

	###################################

	#esegue il comando "userInput"
	def menu(self, userInput):

		#costruisco una lista di comando e argomenti
		commandList = userInput.split()
		commandList.reverse()

		try:
			command = commandList.pop()
		
			#eseguo l'azione corrispondente al comando, default: "None"
			try:
				if	 (command == "exit")			: print("Programma terminato.", end="\n\n")
				elif (command == "repolist")		: self.showRepos()
				elif (command == "branchlist")		: self.showBranches()
				elif (command == "maprepo")			: self.mapRepository(commandList.pop()) 
				elif (command == "mapbranch")		: self.mapBranch(commandList.pop())
				elif (command == "delrepo")			: self.removeRepositoryMap(commandList.pop())
				elif (command == "delbranch")		: self.removeBranchMap(commandList.pop())
				elif (command == "setrepo")			: self.setRepo(commandList.pop())
				elif (command == "setbranch")		: self.setBranch(commandList.pop())
				elif (command == "viewhistory")		: self.viewHistory()
				elif (command == "getlatest")		: self.getLatestVersion()
				elif (command == "getspecific")		: self.getSpecificVersion(commandList.pop())
				elif (command == "pending")			: self.printPendingChanges()
				elif (command == "commit")			: self.commit()
				elif (command == "undo")			: self.undoFile(commandList.pop())
				elif (command == "undoAll")			: self.undoAll()
				else								: print("Valore non ammesso", end="\n\n")
			except:
				print("Errore: parametri mancanti", end="\n\n")
		except:
			pass

		"""COMANDI:
		> exit
		> repolist
		> branchlist [repoName]
		> maprepo [repoName]
		> mapbranch [branchName]
		> delrepo [repoName]
		> delbranch [branchName]
		> setrepo [repoName]
		> setbranch [branchName]
		> viewhistory
		> getlatest
		> getspecific
		> pending
		> commit
		> undo [file]
		> undoall
		
		"""


	#esegue i comandi dell'utente fino al comando "exit"
	def runMenu(self):
		#eseguo i comandi dell'utente
		while True:
			print("> ", end="")
			userInput = input()
			self.menu(userInput)
		
			#il programma termina con il comando "exit"
			if(userInput == "exit"):
				break


	"""QUESTA DOVRA' ESSERE LA CLASSE CHE SI INTERFACCIA DIRETTAMENTE AL SERVER"""
	#TODO: comunicazione con il server e ftp