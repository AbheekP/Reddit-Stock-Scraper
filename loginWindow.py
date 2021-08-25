from tkinter import *
from tkinter import ttk
import apiModules

loginSubmitFunction = None

# attemps username and password submission
def submit():
    try:
        global headers
        headers = apiModules.authenticateRedditAPI(username.get(), password.get())
        root.destroy()
    except KeyError:
        headers = None
        showIncorrectWindow()

# shows popup saying incorrect username or password
def showIncorrectWindow():
    def OKButtonFunction():
        incorrectWindow.destroy()
        usernameInput.delete(first=0, last=len(usernameInput.get()))
        passwordInput.delete(first=0, last=len(passwordInput.get()))
    
    incorrectWindow = Tk()
    incorrectLabel = Label(incorrectWindow, text="Incorrect username or password")
    incorrectLabel.grid(row=0, column=0, padx=10, pady=(5, 3))
    
    OKButton = Button(incorrectWindow, text="OK", command=OKButtonFunction, width=10)
    OKButton.grid(row=2, column=0, padx=10, pady=(0, 10))

# shows login window
def start():
    global root, username, password, usernameInput, passwordInput

    root = Tk()
    root.title("login window")
    root.geometry('+750+350')

    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=(N, S, E, W))

    outerBorderSpace = 10
    mainframe.grid_columnconfigure(0, minsize=outerBorderSpace)
    mainframe.grid_columnconfigure(5, minsize=outerBorderSpace)
    mainframe.grid_rowconfigure(0, minsize=outerBorderSpace)
    mainframe.grid_rowconfigure(5, minsize=outerBorderSpace)

    instructionLabel = Label(mainframe, text="Enter your Reddit username and password")
    instructionLabel.grid(column=2, row=1, columnspan=3)

    usernameLabel = Label(mainframe, text="Username:")
    usernameLabel.grid(column=1, row=2, sticky=(W, E))

    passwordLabel = Label(mainframe, text="Password:")
    passwordLabel.grid(column=1, row=3, sticky=(W, E))

    username = StringVar()
    usernameInput = Entry(mainframe, textvariable=username)
    usernameInput.grid(row=2, column=2, columnspan=3, sticky=(W, E))

    password = StringVar()
    passwordInput = Entry(mainframe, textvariable=password, show="*")
    passwordInput.grid(row=3, column=2, columnspan=3, sticky=(W, E))
    passwordInput.bind('<Return>', lambda event: submit())

    cancelButton = Button(mainframe, text="Cancel", command=exit)
    cancelButton.grid(row=4, column=3, sticky=(W, E))

    submitButton = Button(mainframe, text="Submit", command=submit)
    submitButton.grid(row=4, column=4, sticky=(W, E))

    root.mainloop()
