import os
import os.path as path
import time
import datetime
import shutil
import filecmp
import socket
import rpyc
import inspect
import uti

from uti import LOCAL_VERSION_FILE
from uti import CHANGESET_FILE
from uti import LAST_RUN_FILE
from uti import TMP_DIR
from uti import TO_COMMIT_DIR
from uti import TRUNK
from uti import EDIT
from uti import OLD
from uti import ADD
from uti import REMOVED


class Client:
	
	root = ""
	currPath = ""
	currRepo = ""
	currBranch = ""
	server = None

	def __init__(self, connection):

		#setto il path della cartella root
		self.root = "C:\pyV\pyVclient"
		self.setCurrPath(self.root)

		#setto il riferimento alla connesione con il server
		self.server = connection.root
		#chiedo all'utente se desidera impostare l'ultimo percorso usato
		if (uti.askQuestion("Impostare l'ultimo percorso aperto?")):
			#setto il repository se memorizzato nel file
			self.setRepo(uti.readFileByTag("last_repo", self.getLastRunFile())[0])

			#setto il branch se memorizzato nel file
			self.setBranch(uti.readFileByTag("last_branch", self.getLastRunFile())[0])
			self.printCurrPath()



	def copyDirToClient(self, dirFrom, dirTo):
		"""copia la cartella "dirFrom" nella cartella "dirTo" """
		
		#sovrascrivo la cartella
		if (path.isdir(dirTo)):
			shutil.rmtree(dirTo)
		os.makedirs(dirTo)

		#copio tutti i file contenuti
		for file in self.server.listDir(dirFrom):
			self.copyFileToClient(file, file.replace(dirFrom, dirTo))


	def copyFileToClient(self, fileFrom, fileTo):
		"""copia il file "fileFrom" del server nel path "fileTo" """

		remoteFile = self.server.File()
		remoteFile.open(fileFrom)

		#copio il file del server nella cartella temporanea
		localFile = open(fileTo, "w")

		shutil.copyfileobj(remoteFile, localFile)

		remoteFile.close()
		localFile.close()

		#copio la data di ultima modifica dal file del server
		editTime = remoteFile.getmtime()
		os.utime(fileTo, (int(editTime), int(editTime)))


	def copyDirToServer(self, dirFrom, dirTo):
		"""copia la cartella "dirFrom" nella cartella "dirTo" """
		
		#controllo che la cartella dirFrom esista
		if (path.isdir(dirFrom) == False):
			raise Exception
		
		#copio tutti i file contenuti
		for file in uti.listDir(dirFrom):
			self.copyFileToServer(file, file.replace(dirFrom, dirTo))


	def copyFileToServer(self, fileFrom, fileTo):
		"""copia il file "fileFrom" del client nel path "fileTo" sul server"""

		localFile = open(fileFrom, errors="ignore")

		remoteFile = self.server.File()
		remoteFile.open(fileTo, "w")

		shutil.copyfileobj(localFile, remoteFile)

		remoteFile.close()
		localFile.close() 


	def runMenu(self):
		"""esegue i comandi dell'utente fino al comando "exit" """

		#eseguo i comandi dell'utente
		while True:
			print("> ", end="")
			userInput = input()
			self.menu(userInput)
		
			#il programma termina con il comando "exit"
			if (userInput == "exit"):
				break


	def menu(self, userInput):
		"""esegue il comando "userInput" """

		#costruisco una lista di comando e argomenti
		commandList = userInput.split()
		commandList.reverse()

		#eseguo il comando
		try:
			try:
				command = commandList.pop()
			except:
				raise Exception("Valore non ammesso")

			if (command == "exit"): 
				self.checkCommand(commandList)
				#memorizzo gli ultimi repo/branch settati
				uti.writeFileByTag("last_repo", self.getCurrRepo(), self.getLastRunFile())
				uti.writeFileByTag("last_branch", self.getCurrBranch(), self.getLastRunFile())
				print("Programma terminato.", end="\n\n")
			
			elif (command == "clear"):
				self.checkCommand(commandList)
				os.system("cls")

			elif (command == "opendir"):
				self.checkCommand(commandList, paramNum=0)
				os.system("explorer {}".format(self.getCurrPath()))
				print()

			elif (command == "currdir"):
				self.checkCommand(commandList, paramNum=0)
				self.printCurrPath()

			elif (command == "listdir"):
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.listDir()

			elif (command == "createrepo"):
				self.checkCommand(commandList, paramNum=1)
				self.createRepo(commandList.pop()) 
				
			elif (command == "createbranch"):
				self.checkCommand(commandList, paramNum=1, checkRepo=True)
				self.createBranch(commandList.pop()) 

			elif (command == "removerepo"):
				self.checkCommand(commandList, paramNum=1)
				self.removeRepo(commandList.pop()) 
				
			elif (command == "removebranch"):
				self.checkCommand(commandList, paramNum=1, checkRepo=True)
				self.removeBranch(commandList.pop()) 

			elif (command == "repolist"): 
				self.checkCommand(commandList, paramNum=0)
				self.showRepos() 
			
			elif (command == "branchlist"): 
				self.checkCommand(commandList, paramNum=0, checkRepo=True)
				self.showBranches()

			elif (command == "maprepo"): 
				self.checkCommand(commandList, paramNum=1)
				self.mapRepo(commandList.pop()) 

			elif (command == "mapbranch"): 
				self.checkCommand(commandList, paramNum=1, checkRepo=True)
				self.mapBranch(commandList.pop())

			elif (command == "droprepo"): 
				self.checkCommand(commandList, paramNum=1)
				self.removeRepoMap(commandList.pop())

			elif (command == "dropbranch"):
				self.checkCommand(commandList, paramNum=1, checkRepo=True)
				self.removeBranchMap(commandList.pop())

			elif (command == "setrepo"):
				self.checkCommand(commandList, paramNum=1)
				self.setRepo(commandList.pop())
				self.printCurrPath()

			elif (command == "setbranch"): 
				self.checkCommand(commandList, paramNum=1, checkRepo=True)
				branchName = commandList.pop()
				self.setBranch(branchName)
				self.printCurrPath()

			elif (command == "history"): 
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.showHistory()

			elif (command == "getlatest"): 
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.getLatestVersion() 

			elif (command == "getspecific"):
				self.checkCommand(commandList, paramNum=1, checkRepo=True, checkBranch=True)
				self.getSpecificVersion(int(commandList.pop()))

			elif (command == "rollback"):
				self.checkCommand(commandList, paramNum=1, checkRepo=True, checkBranch=True)
				self.getSpecificVersion(int(commandList.pop()))
				self.commitAll()

			elif (command == "pending"): 
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.printPendingChanges()
				
			elif (command == "excludeextension"): 
				self.checkCommand(commandList, paramNum=1, checkRepo=True, checkBranch=True)
				self.excludeExtension(commandList.pop())
				self.printPendingChanges()
				
			elif (command == "excludefile"): 
				self.checkCommand(commandList, checkRepo=True, checkBranch=True)
				commandList.reverse()
				self.excludeFile(" ".join(commandList))
				self.printPendingChanges()

			elif (command == "includeextension"):
				self.checkCommand(commandList, paramNum=1, checkRepo=True, checkBranch=True)
				self.includeExtension(commandList.pop())
				self.printPendingChanges()

			elif (command == "includeallextensions"):
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.includeAllExtension()
				self.printPendingChanges()

			elif (command == "includefile"):
				self.checkCommand(commandList, checkRepo=True, checkBranch=True)
				commandList.reverse()
				self.includeFile(" ".join(commandList))
				self.printPendingChanges()

			elif (command == "includeallfiles"):
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.includeAllFile()
				self.printPendingChanges()

			elif (command == "includeall"):
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.includeAllExtension()
				self.includeAllFile()
				self.printPendingChanges()

			elif (command == "printexcluded"):
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.printExcluded()

			elif (command == "commit"): 
				self.checkCommand(commandList, checkRepo=True, checkBranch=True)
				commandList.reverse()
				self.commitOne(" ".join(commandList))

			elif (command == "commitall"): 
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.commitAll()

			elif (command == "undo"): 
				self.checkCommand(commandList, checkRepo=True, checkBranch=True)
				try:
					commandList.reverse()
					self.undoFile(" ".join(commandList))
				except:
					self.printPendingChanges()

			elif (command == "undoall"): 
				self.checkCommand(commandList, paramNum=0, checkRepo=True, checkBranch=True)
				self.undoAll()
			
			elif (command == "compare"):
				self.checkCommand(commandList, checkRepo=True, checkBranch=True)
				try:
					commandList.reverse()
					self.compare(" ".join(commandList))
				except Exception as ex:
					print(ex, end="\n\n")
					self.printPendingChanges()
			
			elif (command == "winmerge"):
				self.checkCommand(commandList, checkRepo=True, checkBranch=True)
				try:
					commandList.reverse()
					self.merge(" ".join(commandList))
				except Exception as ex:
					print(ex, end="\n\n")
					self.printPendingChanges()
				print()

			elif (command == "help"): 
				self.checkCommand(commandList)
				self.printHelp()

			else: 
				print("Valore non ammesso", end="\n\n")

		except Exception as ex:
			print(ex, end="\n\n")


	def checkCommand(self, commandList, paramNum=None, checkRepo=False, checkBranch=False):
		"""controlla che i parametri e il path corrente siano compatibili con il comando"""

		if ((paramNum != None) & (len(commandList) != paramNum)):
			raise Exception("Parametri errati")
		elif ((checkRepo) & (not self.getCurrRepo())):
			raise Exception("Nessun repository settato")
		elif ((checkBranch) & (not self.getCurrBranch())):
			raise Exception("Nessun branch settato")


	def existsRepo(self, repoName):
		"""ritorna True se esiste il repository "repoName" """

		#ottengo la cartella del repository
		repoDir = path.join(self.root, repoName)
		#verifico che la cartella esista
		return path.isdir(repoDir)
		

	def existsBranch(self, branchName):
		"""ritorna True se esiste il branch "branchName" """

		#ottengo la cartella del branch
		branchDir = path.join(self.root, self.getCurrRepo(), branchName)
		#verifico che la cartella esista
		return path.isdir(branchDir)


	def printCurrPath(self):
		"""stampa il path corrente"""

		print("> {}".format(uti.getPathForPrint(self.getCurrPath())), end="\n\n")


	def listDir(self):
		"""stampa tutti i file e sottocartelle del branch selezionato"""

		list = self.server.listBranch(self.getCurrRepo(), self.getCurrBranch())
		for elem in list:
			print(uti.getPathForPrint(elem))

		print()


	def createRepo(self, repoName):
		"""crea un nuovo repository sul server"""

		print("Inserire il path della cartella da caricare sul server:")
		sourceDir = input()
		if (path.isdir(sourceDir) == False):
			raise Exception("Percorso errato.")

		#creo repository e trunk
		destDir = self.server.addRepo(repoName)
		self.copyDirToServer(sourceDir, destDir)
		print("Repository {} creato con successo.".format(repoName), end="\n\n")
		self.mapRepo(repoName)
		self.mapBranch(TRUNK)

	
	def createBranch(self, branchName):
		"""crea un nuovo branch sul server"""

		self.server.addBranch(self.getCurrRepo(), branchName)
		print("Branch {} creato con successo.".format(branchName), end="\n\n")	
		self.mapBranch(branchName)


	def removeRepo(self, repoName):
		"""rimuove il repository dal server"""

		#verifico che la cartella esista
		if (self.server.existsRepo(repoName) == False):
			raise Exception("Repository {} non presente".format(repoName))
		else:
			try:
				if (uti.askQuestion("Questa operazione rimuoverà permanentemente il repository {} dal server. Continuare?".format(repoName))):
					self.server.removeRepo(repoName)
					print("Il repository {} è stato rimosso dal server".format(repoName), end="\n\n")

					if (self.existsRepo(repoName)):
						if (uti.askQuestion("Eliminare anche la copia locale?")):
							self.removeRepoMap(repoName)
			except:
				raise Exception("Impossibile effettuare l'operazione.")


	def removeBranch(self, branchName):
		"""rimuove il branch dal server"""

		if (branchName == TRUNK):
			raise Exception("Impossibile rimuovere il ramo principale.")

		#verifico che la cartella esista
		if (self.server.existsBranch(self.getCurrRepo(), branchName) == False):
			raise Exception("Branch {} non presente".format(branchName))
		else:
			try:
				uti.askQuestion("Questa operazione rimuoverà permanentemente il branch {} dal server. Continuare?".format(branchName))
				self.server.removeBranch(self.getCurrRepo(), branchName)

				print("Il branch {} è stato rimosso dal server".format(branchName), end="\n\n")
				if (self.existsBranch(branchName)):
					if (uti.askQuestion("Eliminare anche la copia locale?")):
						self.removeBranchMap(branchName)
			except:
				raise Exception("Impossibile effettuare l'operazione.")


	def showRepos(self):
		"""mostra la lista dei repository presenti sul server"""

		repolist = self.server.showRepos()
		if (len(repolist) == 0):
			print("\nNessun repository presente sul server di pyVersioning")
		else:
			print("\nRepositories sul server di pyVersioning:")

		for repoName in repolist:
			#verifico che la cartella esista in locale
			if (self.existsRepo(repoName)):
				print("- {} ({})".format(repoName, "mapped"))
			else:
				print("- {}".format(repoName))
		print()


	def showBranches(self):
		"""mostra la lista dei branch presenti sul server"""

		branchList = self.server.showBranches(self.getCurrRepo())
		if (len(branchList) == 0):
			print("\nNessun Branch presente sul repository {}".format(self.getCurrRepo()))
		else:
			print("\nBranches sul repository {}:".format(self.getCurrRepo()))

		for branchName in branchList:
			#verifico se la cartella esiste in locale
			if (self.existsBranch(branchName)):
				print("- {} ({}) - changeset originale: {}".format(branchName, "mapped", branchList[branchName]))
			else:
				print("- {} - changeset originale: {}".format(branchName, branchList[branchName]))
		print()


	def showHistory(self):
		"""mostra la lista dei changeset presenti nel branch corrente"""

		print("\nChangeset del branch {}:".format(self.getCurrBranch()))
		for changeSet in self.server.showChangesets(self.getCurrRepo(), self.getCurrBranch()):
			print("- {}".format(changeSet))


	def mapRepo(self, repoName):
		"""mappa il repository nella cartella del client"""

		#se il repository esiste sul server, creo una cartella sul client
		#altrimenti viene generata un'eccezione
		if (self.server.existsRepo(repoName) == False):
			raise Exception("Repository {} non presente".format(repoName))
		else:
			#ottengo il path del repository
			clientDir = path.join(self.root, repoName)

			#chiedo all'utente se sovrascrivere la cartella
			if (uti.askAndRemoveDir(clientDir, askOverride=True)):
				#mappo il repository nella cartella del client
			
					os.makedirs(clientDir)
					print("Repository mappato in:", clientDir, end = "\n\n")
				
					#setto anche il repository mappato come repository corrente di default
					self.setRepo(repoName)



	def mapBranch(self, branchName):
		"""mappa il branch nella cartella del client"""

		#se il branch esiste sul server, creo una cartella sul client
		#altrimenti viene generata un'eccezione
		if (self.server.existsBranch(self.getCurrRepo(), branchName) == False):
			raise Exception("Branch {} non presente".format(branchName))
		else:
			#ottengo il path del branch
			clientDir = path.join(self.root, self.getCurrRepo(), branchName)

			#chiedo all'utente se sovrascrivere la cartella
			if (uti.askAndRemoveDir(clientDir, askOverride=True)):
				#mappo il branch nella cartella del client
				branchDir = path.join(self.root, self.getCurrRepo(), branchName)
				os.makedirs(branchDir)
				
				#setto il branch mappato come branch corrente di default
				self.setBranch(branchName)

				print("Branch mappato in:", clientDir, end = "\n\n")
				
				if (uti.askQuestion("Scaricare l'ultima versione?")):
					self.getLatestVersion()


	def removeRepoMap(self, repoName):
		"""rimuove la cartella del repo sul client"""

		if (self.existsRepo(repoName)):
			repodir = path.join(self.root, repoName)
			if (uti.askAndRemoveDir(repodir)):
				if (self.getCurrRepo() == repoName):
					self.setCurrBranch("")
					self.setCurrRepo("")
					self.printCurrPath()
		else:
			raise Exception("Repository {} non presente".format(repoName))


	def removeBranchMap(self, branchName):
		"""rimuove la cartella del branch sul client"""

		if (self.existsBranch(branchName)):
			branchdir = path.join(self.root, self.getCurrRepo(), branchName)
			if (uti.askAndRemoveDir(branchdir)):
				if (self.getCurrBranch() == branchName):
					self.setCurrBranch("")
					self.printCurrPath()
		else:
			raise Exception("Branch {} non presente".format(branchName))


	def setRepo(self, repoName):
		"""setta il repository corrente"""

		#verifico che il repository locale esista
		if (self.existsRepo(repoName)):
			#aggiorno il repository corrente
			self.setCurrRepo(repoName)
			self.setCurrBranch("")
		else:
			#verifico se esiste sul server
			if (self.server.existsRepo(repoName)):
				print("Il repository {} non è stato mappato".format(repoName))
				if (uti.askQuestion("Effettuare il map del repository?")):
					self.mapRepo(repoName)
			else:
				print("Il repository {} non esiste".format(repoName))
		

	def setBranch(self, branchName):
		"""setta il branch corrente"""

		#verifico che il branch locale esista
		if (self.existsBranch(branchName)):
			
			#aggiorno il branch corrente
			self.setCurrBranch(branchName)
		else:
			if (self.server.existsBranch(self.getCurrRepo(), branchName)):
				print("Il branch {} non è stato mappato".format(branchName))
				if (uti.askQuestion("Effettuare il map del branch?")):
					self.mapBranch(branchName)
			else:	
				print("Il branch {} non esiste".format(branchName))
			

	def getLatestVersion(self):
		"""scarica l'ultima versione e la copia nella cartella del branch"""

		#prendo la latestVersion da Repository e Branch corrente
		serverDir, lastChangesetNum = self.server.getLatestVersion(self.getCurrRepo(), self.getCurrBranch())
		self.copyDirToClient(serverDir, self.getCurrPath())

		uti.writeFileByTag("last_changeset", lastChangesetNum, self.getLocalVersionFile())
		print("Versione locale aggiornata con successo", end="\n\n")
	
	
	def getSpecificVersion(self, changesetNum):
		"""scarica una versione specifica e la copia nella cartella del branch"""

		if (self.server.existsChangeset(self.getCurrRepo(), self.getCurrBranch(), changesetNum) == False):
			raise Exception("Changeset non presente")

		#prendo la versione specifica da Repository e Branch corrente con il numero di changeset passato
		serverDir = self.server.getSpecificVersion(self.getCurrRepo(), self.getCurrBranch(), changesetNum)
		self.copyDirToClient(serverDir, self.getCurrPath())

		uti.writeFileByTag("last_changeset", changesetNum, self.getLocalVersionFile())
		print("Versione locale aggiornata con successo", end="\n\n")


	def printPendingChanges(self):
		"""stampa una lista dei file modificati in locale con data di ultima modifica"""

		#scorro tutti i file nella lista dei pending
		pendingList = self.getPendingChanges()
		if (len(pendingList) == 0):
			raise Exception("Nessun file in modifica.")
		else:
			print("Lista dei file in modifica:")
			for file in pendingList:
				if (pendingList[file] == EDIT) | (pendingList[file] == OLD):
					#prendo la data di ultima modifica del file
					localFileDate = datetime.datetime.fromtimestamp(path.getmtime(file)).strftime("%Y-%m-%d %H:%M:%S")
					#prendo la data di ultima modifica del file sul server
					serverFile = self.getServerFile(file)
					serverFileDate = datetime.datetime.fromtimestamp(path.getmtime(serverFile)).strftime("%Y-%m-%d %H:%M:%S")
					
					#stampo file e data ultima modifica
					print("{} ({}) - locale: {} - server: {}".format(file.replace(self.getCurrPath(), ""), pendingList[file], localFileDate, serverFileDate))

				elif (pendingList[file] == ADD):
					#stampo file aggiunti in locale
					print("{} ({})".format(file.replace(self.getCurrPath(), ""), pendingList[file]))

				elif (pendingList[file] == REMOVED):
					#stampo file rimossi in locale
					print("{} ({})".format(file.replace(self.getCurrPath(), ""), pendingList[file]))

			print()

	
	def getPendingChanges(self):
		"""ritorna una lista dei file modificati in locale"""

		#scarico una latestVersion in una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), TMP_DIR)

		serverDir, lastChangesetNum = self.server.getLatestVersion(self.getCurrRepo(), self.getCurrBranch())
		self.copyDirToClient(serverDir, tmpDir)

		#scorro tutti i file della cartella locale
		pendings = {}
		for dirPath, dirNames, files in os.walk(self.getCurrPath()):
			if (TMP_DIR in dirNames):
				dirNames.remove(TMP_DIR)

			for fileName in files:
				
				if (fileName == LOCAL_VERSION_FILE):
					continue

				localFile = path.join(dirPath, fileName)
				try:
					#verifico se il file è fra quelli da escludere
					if (self.isExcluded(localFile)):
						continue

					#cerco sul server il file corrispondente al localFile 
					#(cerco sempre a partire dall'ultima versione così da segnalare anche file vecchi)
					serverFile = self.getServerFile(localFile)
				
					#se il file locale è stato modificato va aggiunto ai pending
					if (int(path.getmtime(localFile)) > int(path.getmtime(serverFile))):
						if (filecmp.cmp(localFile, serverFile) == False):
							pendings[localFile] = EDIT
					elif(int(path.getmtime(localFile)) < int(path.getmtime(serverFile))):
						if (filecmp.cmp(localFile, serverFile) == False):
							pendings[localFile] = OLD

				except:		
					#se il file non viene trovato nel server vuol dire che è stato aggiunto in locale
					pendings[localFile] = ADD

		#scorro tutti i file del server
		for dirPath, dirNames, files in os.walk(tmpDir):
			for fileName in files:
				serverFile = path.join(dirPath, fileName)
				localFile = serverFile.replace(tmpDir, self.getCurrPath())
				#verifico se il file è fra quelli da escludere
				if (self.isExcluded(localFile)):
					continue

				#i file presenti nel server e non nella versione locale sono stati rimossi
				if (path.isfile(localFile) == False):
					pendings[localFile] = REMOVED

		#ritorno la lista dei pendig
		return pendings


	def isExcluded(self, file):
		"""ritorna True se il file è da escludere dai pending"""

		fileName, fileExtension = path.splitext(file)

		#leggo le estensioni escluse
		try:
			excludedExt = uti.readFileByTag("ext_ignore", self.getLocalVersionFile())
		except:
			excludedExt = ()

		#se l'estensione del file è fra quelle da escludere ritorno True
		for ext in excludedExt:
			if (fileExtension == ext):
				return True

		#leggo la lista dei file da escludere
		try:
			excludedFiles = uti.readFileByTag("file_ignore", self.getLocalVersionFile())
		except:
			excludedFiles = ()

		#se il file è fra quellei da escludere ritorno True
		for exludedFile in excludedFiles:
			if (file == exludedFile):
				return True

		return False
	

	def excludeExtension(self, ext):
		"""aggiunge l'estensione "ext" alla lista delle estensioni da escludere """

		uti.writeFileByTag("ext_ignore", ".{}".format(ext), self.getLocalVersionFile())
		print("Estensione *.{} esclusa.".format(ext), end="\n\n")


	def includeExtension(self, ext):
		"""rimuove l'esclusione sull'estensione "ext" """

		uti.removeByTagAndVal("ext_ignore", ".{}".format(ext), self.getLocalVersionFile())
		print("Estensione *.{} inclusa.".format(ext), end="\n\n")


	def includeAllExtension(self):
		"""rimuove tutte le esclusioni su estensioni"""

		uti.removeByTag("ext_ignore", self.getLocalVersionFile())
		print("Tutte le estensioni sono state incluse.", end="\n\n")


	def excludeFile(self, fileName):
		"""aggiunge il file alla lista dei file da escludere"""

		file = self.findFileInPendings(fileName)
		uti.writeFileByTag("file_ignore", file, self.getLocalVersionFile())
		print("File {} escluso.".format(fileName), end="\n\n")


	def includeFile(self, fileName):
		"""rimuove l'esclusione sul file """
		
		#file = self.findFileInPendings(fileName)
		uti.removeByTagAndVal("file_ignore", fileName, self.getLocalVersionFile())
		print("File {} incluso".format(fileName), end="\n\n")


	def includeAllFile(self):
		"""rimuove tutte le esclusioni su files"""

		uti.removeByTag("file_ignore", self.getLocalVersionFile())
		print("Tutti i file sono stati inclusi.", end="\n\n")

	
	def printExcluded(self):
		"""stampa a video tutte le estensioni e file esclusi"""
		excludedExt = uti.readFileByTag("ext_ignore", self.getLocalVersionFile())
		excludedFiles = uti.readFileByTag("file_ignore", self.getLocalVersionFile())

		if ((len(excludedExt) == 0) & (len(excludedFiles) == 0)):
			raise Exception("Nessun file o estensione esclusi")

		for ext in excludedExt:
			print("*{}".format(ext))

		for file in	excludedFiles:
			print(file.replace(self.getCurrPath(), ""))
		print()


	def commitOne(self, fileName):
		"""crea un nuovo changeset con le modifiche del solo file "fileName" """

		#creo una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), TO_COMMIT_DIR)
		
		#prendo il file corrente dai pending
		try:
			file = self.findFileInPendings(fileName)
			tag = self.getPendingChanges()[file]
		except:
			raise
		
		#aggiunto i file da committare nella cartella temporanea
		self.addForCommit(file, tag, tmpDir)
		
		#effettuo il commit
		print("Inserire un commento: ")
		comment = input()
		self.doCommit(tmpDir, comment)
		print("File {} aggiornato con successo.".format(fileName), end="\n\n")


	def commitAll(self):
		"""crea un nuovo changeset con le modifiche dei file in pending"""

		#creo una cartella temporanea
		tmpDir = path.join(self.getCurrPath(), TO_COMMIT_DIR)
		if (path.isdir(tmpDir)):
			shutil.rmtree(tmpDir)
		os.makedirs(tmpDir)

		#scorro tutti i file nella lista dei pending
		pendingList = self.getPendingChanges()
		if (len(pendingList) == 0):
			raise Exception("Nessun file in modifica.")

		#aggiungo ai pending tutti i file diversi dalla versione del server
		for file in pendingList:
			self.addForCommit(file, pendingList[file], tmpDir)

		#effettuo il commit
		print("Inserire un commento: ")
		comment = input()
		self.doCommit(tmpDir, comment)

		print("Modifiche inviate con successo.", end="\n\n")

		#chiedo all'utente se desidera anche aggiornare la versione locale
		if (uti.askQuestion("Scaricare ultima versione?")):
			self.getLatestVersion()


	def addForCommit(self, file, tag, tmpDir):
		"""aggiunge un file alla cartella temporanea dei file da committare"""

		if (tag != REMOVED):
			#copio il file nella cartella temporanea (creo le cartelle se non presenti)
			#prendo il path del file da copiare
			tmpFileDir = path.dirname(file.replace(self.getCurrPath(), tmpDir))
			#se non esiste creo il percorso
			if (path.isdir(tmpFileDir) == False):
				os.makedirs(tmpFileDir)

			#copio il file
			shutil.copy2(file, tmpFileDir)

		#inserisco il tag nel file changeset.txt
		uti.writeFileByTag(tag, file.replace("{}\\".format(self.getCurrPath()), ""), path.join(tmpDir, "changeset.txt"))


	def doCommit(self, sourceDir, comment):
		"""effettua il commit dei file contenuti in "sourceDir" su un nuovo changeset"""

		#creo un nuovo changeset in cui copiare la cartella temporanea
		changesetDir = self.server.addChangeset(self.getCurrRepo(), self.getCurrBranch(), comment)
		self.copyDirToServer(sourceDir, changesetDir)

		#rimuovo la cartella temporanea
		if (path.isdir(sourceDir)):
			shutil.rmtree(sourceDir)
		
		uti.writeFileByTag("last_changeset", self.server.getLastChangeset(self.getCurrRepo(), self.getCurrBranch()), self.getLocalVersionFile())


	def undoFile(self, file):
		"""annulla le modifiche sul file e riporta la versione a quella originale"""

		try:
			#prendo il file corrispondente dal server e lo sovrascrivo al file locale
			filePath = self.findFileInPendings(file)
			try:
				originalChangeset = int(uti.readFileByTag("last_changeset", self.getLocalVersionFile())[0])
				serverFile = self.getServerFile(filePath)

				if (uti.askQuestion("Questo comando annullerà le modifiche sul file {}, sei sicuro?".format(file))):
					shutil.copy2(serverFile, path.dirname(filePath))
			except:
				#se il file non è presente sul server era in add sul client, quindi va semplicemente rimosso
				os.remove(file)
			print("Modifiche annullate.", end="\n\n")
		except:
			raise Exception("File non presente in pending.")


	def undoAll(self):
		"""annulla tutte le modifiche e riporta la versione a quella originale"""

		if (uti.askQuestion("Questo comando cancellerà tutti i pending, sei sicuro?")):
			print("Modifiche annullate.", end="\n\n")
			self.getSpecificVersion(int(uti.readFileByTag("last_changeset", self.getLocalVersionFile())[0]))
		

	def compare(self, localFile):
		"""effettua il diff del file in pending con il file sul server"""

		try:
			pendingFile = self.findFileInPendings(localFile)
		except:
			raise Exception("File non presente in pending")

		if (path.isfile(pendingFile) == False):
			raise Exception("File non presente sul client")

		serverFile = self.getServerFile(pendingFile)
		if (path.isfile(serverFile) == False):
			raise Exception("File non presente sul server")

		print ("".join(uti.diff(serverFile, pendingFile)))
		

	def merge(self, localFile):
		"""effettua il diff del file in pending con il file sul server con winmerge"""

		try:
			pendingFile = self.findFileInPendings(localFile)
		except:
			raise Exception("File non presente in pending")

		if (path.isfile(pendingFile) == False):
			raise Exception("File non presente sul client")

		serverFile = self.getServerFile(pendingFile)
		if (path.isfile(serverFile) == False):
			raise Exception("File non presente sul server")

		#lancio winmerge
		exePath = path.dirname(inspect.getsourcefile(lambda:0))
		winmergepath = path.join(exePath, "WinMerge", "WinMergePortable.exe")

		os.system("{} {} {}".format(winmergepath, pendingFile, serverFile))


	def printHelp(self):
		"""stampa una lista di comandi con descrizione"""
		print("\n> exit - chiude il programma",
			  "> repolist - stampa la lista dei repositories presenti sul server",
			  "> branchlist - stampa una lista dei branchs presenti sul repository corrente sul server",
			  "> createrepo [repoName] - crea il repository \"repoName\" nel server",
			  "> createbranch [branchName] - crea il branch \"branchName\" nel server",
			  "> removerepo [repoName] - rimuove il repository \"repoName\" dal server",
			  "> removebranch [branchName] - rimuove il branch \"branchName\" dal server",
			  "> maprepo [repoName] - mappa il repository \"repoName\" nella macchina locale",
			  "> mapbranch [branchName] - mappa il branch \"branchName\" nella macchina locale",
			  "> droprepo [repoName] - elimina il repository \"repoName\" dalla macchina locale",
			  "> dropbranch [branchName] - elimina il branch \"branchName\" dalla macchina locale",
			  "> setrepo [repoName] - imposta il repository \"repoName\" come repository corrente",
			  "> setbranch [branchName] - imposta il branch \"branchName\" come branch corrente",
			  "> currdir - stampa il percorso di esecuzione corrente",
			  "> listdir - stampa una lista di file e sottocartelle per il progetto selezionato",
			  "> history - stampa la lista dei changeset del branch corrente",
			  "> getlatest - scarica la versione più recente del branch corrente",
			  "> getspecific [changeset] - scarica la versione specificata in \"changeset\" del branch corrente",
			  "> pending - stampa una lista dei file modificati in locale",
			  "> excludeextension [ext] - esclude tutti i file .[ext] dai file in modifica",
			  "> excludefile [file] - esclude il file \"file\" dai file in modifica", 
			  "> includeextension [ext] - include l'estensione se precedentemente esclusa",
			  "> includeallextensions - include tutte le estensioni precedentemente escluse",
			  "> includefile [file] - include il file se precedentemente escluso",
			  "> includeallfiles - include tutti i file precedentemente esclusi",
			  "> includeall - include tutti i file e estensioni precedentemente esclusi",
			  "> printexcluded - stampa la lista di estensioni file esclusi",
			  "> commit [file] - effettua il commit del file \"file\" associando il commento \"comment\"",
			  "> commitall - effettua il commit di tutti i file in pending associando il commento \"comment\"",
			  "> undo [file] - annulla le modifiche sul file \"file\"",
			  "> undoall - annulla le modifiche su tutti i file in pending e scarica l'ultima versione",
			  "> compare [file] - effettua un confronto fra il file \"file\" e la versione del server",
			  "> winmerge [file] - effettua un confronto fra il file \"file\" e la versione del server con winmerge",
			  "> opendir - apre la cartella corrente",
			  "> clear - pulisce il terminale",
			  "> help - stampa la guida", sep="\n", end="\n\n")


	def setCurrPath(self, path):
		"""setta il path di esecuzione"""

		self.currPath = path


	def setCurrRepo(self, repoName):
		"""setta il repository selezionato"""

		self.currRepo = repoName
		self.setCurrPath(path.join(self.root, repoName))


	def setCurrBranch(self, branchName):
		"""setta il branch selezionato"""

		self.currBranch = branchName
		self.setCurrPath(path.join(self.root, self.getCurrRepo(), branchName))


	def getCurrPath(self):
		"""ritorna il path di esecuzione"""

		return self.currPath


	def getCurrRepo(self):
		"""ritorna il repository selezionato"""

		return self.currRepo


	def getCurrBranch(self):
		"""ritorna il branch selezionato"""

		return self.currBranch


	def getLocalVersionFile(self):
		"""ritorna il file dei pending nel branch corrente"""

		return path.join(self.getCurrPath(), LOCAL_VERSION_FILE)

	
	def getLastRunFile(self):
		"""ritorna il file dell'ultimo run"""

		return path.join(self.root, LAST_RUN_FILE)


	"""NOTA: non ammette 2 file con lo stesso nome"""
	def findFileInPendings(self, fileName):
		"""cerca il file "fileName" frai pending"""
		
		for pendingFile in self.getPendingChanges():
			if (path.basename(pendingFile) == fileName):
				return pendingFile

		raise Exception("File non trovato in pending")


	def getServerFile(self, localFile):
		"""prende il file della versione locale e restituisce il file del server contenuto nella cartella temporanea"""

		tmpDir = path.join(self.getCurrPath(), TMP_DIR)
		return localFile.replace(self.getCurrPath(), tmpDir)


### Main ###

try:
	#connetto client e server
	print("Benvenuto in pyVersioning - Beta")
	
	#prendo l'indirizzo del server
	while (True):
		print("Digitare l'ip del server (\"localhost\" per un server locale):")
		host = input()
		if (host == "localhost"):
			break

		try:
			socket.inet_aton(host)
			break
		except socket.error as er:
			print("IP non valido", end="\n\n")

	#stabilisco la connessione
	print("Connessione al server...", sep="\n")
	connection = rpyc.connect(host, 18812)
	print("Connessione stabilita.", end="\n\n")
	
	#lancio il client
	Client(connection).runMenu()
	
	#chiudo la connesione
	connection.close()

except Exception as ex:
	print("Si è verificato un errore: {}.".format(ex), "Il programma verrà terminato.", sep="\n", end="\n\n")