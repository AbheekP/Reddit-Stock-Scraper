import loginWindow
import apiModules
import mainWindow

loginWindow.loginSubmitFunction = apiModules.authenticateRedditAPI
loginWindow.start()
headers = loginWindow.headers

if(headers == None):
    exit()
else:
    mainWindow.start(headers)

