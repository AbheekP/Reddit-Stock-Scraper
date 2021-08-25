from tkinter import *
from tkinter import ttk
import reticker
import apiModules
from datetime import datetime
from datetime import date
import webbrowser
import reticker
import enchant
import stockSearchModules
import tkinter.messagebox

# Turns a datetime object into a better readable format
def getDateString(dateVar: datetime):
    dateTimeTuple = dateVar.timetuple()
    year, month, day, hour, minute = dateTimeTuple[0:5]
    
    if hour > 12:
        hour -= 12
        period = "pm"
    elif hour == 0:
        hour = 12
        period = "am"
    else:
        period = "am"

    if(minute < 10):
        minute = "0%s" % (minute)

    return "%s:%s%s %s/%s/%s" % (hour, minute, period, month, day, year)

# Returns the timedelta of the inputted time from today in a readable format
def getTimeFromTodayString(dateVar: datetime):
    today = datetime.today()
    delta = today - dateVar

    days = delta.days
    years = 0
    while(days / 365 > 1):
        days -= 365
        years += 1

    results = ""
    if(years > 0):
        results += "%d years and " % years
    results += "%d days ago" % (days)

    return results

# Extracts ticker symbols from 'title' and returns them in either a list or as a string
def getTickers(title, string: bool):
    
    tickerExtract = reticker.TickerExtractor()
    dictionary = enchant.Dict("en_US")

    tickers = tickerExtract.extract(title)

    removals = []
    for ticker in tickers:
        if dictionary.check(ticker):
            removals.append(ticker)
    
    for removal in removals:
        tickers.remove(removal)

    if not string:
        return tickers

    tickerString = ', '.join(tickers)
    return tickerString

# Searches through the inputted subreddit and returns an array of posts that includes various information about individual posts
# After searching, this information is shown on the GUI
def redditSearch(postFrame: Frame, subreddit, filter, timeframe, limit):
    
    postJson = apiModules.redditPostSearchExecution(subreddit, filter, timeframe, redditHeaders, limit).json()

    posts = []
    for post in postJson['data']['children']:
       
        user = apiModules.redditUserSearchExecution(post['data']['author'], redditHeaders).json()
        posts.append({
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'upvotes': post['data']['ups'],
            'downvotes': post['data']['downs'],
            'poster': user['data']['name'],
            'date': getDateString(datetime.fromtimestamp(post['data']['created'])),
            'post_id': post['data']['id'],
            'tickers_string': getTickers(post['data']['title'], True),
            'tickers_arr': getTickers(post['data']['title'], False),
            'poster_id': post['data']['author_fullname'],
            'poster_karma': user['data']['total_karma'],
            'poster_acc_creation_date': getTimeFromTodayString(datetime.fromtimestamp(user['data']['created']))
        })

    addRedditPostToFrame(postFrame, posts)

# Searches through stock databases and returns information about the stock based on the stock search type
# After searching, this information is shown on the GUI
def stockSearch(postFrame: Frame, symbol, stockSearchType, months: list, month, day, year):
    if(stockSearchType == 'Company Info'):
        data = stockSearchModules.getCompanyProfile(symbol)
    elif(stockSearchType == 'Current Quote'):
        data = stockSearchModules.getQuote(symbol)
    else:
        month = months.index(month) + 1
        data = stockSearchModules.getDifference(symbol, date(year=year, month=month, day=day))
        
    if(type(data) == str):  
        tkinter.messagebox.showinfo(message='Symbol does not exist OR date is out of range')
    else:
        addStockInfoToFrame(postFrame, data, list(data.keys()))

# Main start method
def start(headers):
    global redditHeaders
    redditHeaders = headers
    
    root = Tk()
    root.geometry('+250+150')

    mainframe = ttk.Frame(root)
    mainframe.grid(column=0, row=0, sticky=NSEW)

    # Search area for inputting search (Default to reddit search)
    searchLabel = Label(mainframe, text="Enter Subreddit:")
    searchLabel.grid(column=0, row=0, padx=5, pady=5, sticky=EW)

    search = StringVar()
    searchInput = Entry(mainframe, textvariable=search, width=175)
    searchInput.grid(column=1, row=0, padx=(0, 5), pady=5, sticky=(E, W))
    
    searchButton = Button(mainframe, text='Search', command=lambda: redditSearch(postFrame, search.get(), filter.get(), timeFrame.get(), int(postLimit.get()) - 1))
    searchButton.grid(row=0, column=2, padx=(0, 5), pady=5, sticky=EW)

    # Scrollable area for posts
    mainframe.grid_rowconfigure(1, minsize=700)
    scrollframe = Frame(mainframe, borderwidth=1, relief=SUNKEN)
    scrollframe.grid(column=0, row=1, columnspan=3, sticky=NSEW, padx=3, pady=3)

    global postCanvas
    postCanvas = Canvas(scrollframe, borderwidth=0)
    postFrame = Frame(postCanvas)
    vsb = Scrollbar(scrollframe, orient='vertical', command=postCanvas.yview)
    hsb = Scrollbar(scrollframe, orient='horizontal', command=postCanvas.xview)
    postCanvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    vsb.pack(side='right', fill='y')
    hsb.pack(side='bottom', fill='x')
    postCanvas.pack(side='left', fill='both', expand=True)
    postCanvas.create_window((4, 4), window=postFrame, anchor='nw')
    postFrame.bind('<Configure>', lambda event, canvas=postCanvas: canvas.configure(scrollregion=canvas.bbox("all")))

    ## widgets for other functionalities
    otherWidgetFrame = Frame(root)
    otherWidgetFrame.grid(column=1, row=0, sticky=NSEW, padx=5, pady=5)

    # changes various GUI elements for more reddit search functionality
    def searchRedditfunc():
        searchLabel.config(text="Enter Subreddit")
        searchButton.config(command=lambda: redditSearch(postFrame, search.get(), filter.get(), timeFrame.get(), int(postLimit.get()) - 1))
        searchInput.delete(0, len(search.get()))
        stockWidgets.grid_forget()
        redditWidgets.grid(column=0, row=1, sticky=NSEW, pady=(20, 0))

    # changes various GUI elements for more stock search functionality
    def searchStockfunc():
        searchLabel.config(text="Enter Symbol")
        searchButton.config(command=lambda: stockSearch(postFrame, search.get().upper(), stockSearchType.get(), months, month.get(), day.get(), year.get()))
        searchInput.delete(0, len(search.get()))
        redditWidgets.grid_forget()
        stockWidgets.grid(column=0, row=1, sticky=NSEW, pady=(20, 0))

    def searchTypeMenuFunction():
        if(searchType.get() == "Search Reddit"):
            searchRedditfunc()
        else:
            searchStockfunc()

    searchType = StringVar()
    searchType.set("Search Reddit")
    searchTypeMenu = OptionMenu(otherWidgetFrame, searchType, "Search Reddit", "Search Stock", command=lambda event: searchTypeMenuFunction())
    searchTypeMenu.grid(column=0, row=0, sticky=EW)

    # reddit widgets (Default)
    redditWidgets = Frame(otherWidgetFrame)
    redditWidgets.grid(column=0, row=1, sticky=NSEW, pady=(20, 0))

    limitLabel = Label(redditWidgets, text='Enter post limit (max 100)')
    limitLabel.grid(column=0, row=0, sticky=EW)

    postLimit = StringVar()
    postLimit.set('25')
    limitEntry = Entry(redditWidgets, textvariable=postLimit)
    limitEntry.grid(column=0, row=1, sticky=EW)

    filterLabel = Label(redditWidgets, text="Enter Filter")
    filterLabel.grid(column=0, row=2, sticky=EW, pady=(20, 0))

    filters = ['Hot', 'New', 'Rising', 'Top']
    filter = StringVar()
    filter.set(filters[0])

    def checkTopSelected():
        if(filter.get() == "Top"):
            timeFrameMenu.grid(column=0, row=4, sticky=EW)
        else:
            timeFrameMenu.grid_forget()

    filterMenu = OptionMenu(redditWidgets, filter, *filters, command=lambda event: checkTopSelected())
    filterMenu.grid(column=0, row=3, sticky=EW)

    timeFrame = StringVar()
    timeFrame.set("Hour")
    timeFrames = ['Hour', 'Day', 'Week', 'Month', 'Year', 'All Time']
    timeFrameMenu = OptionMenu(otherWidgetFrame, timeFrame, *timeFrames)

    # stock search widgets
    stockWidgets = Frame(otherWidgetFrame)
    
    stockSearchTypeLabel = Label(stockWidgets, text='Select Search Type')
    stockSearchTypeLabel.grid(column=0, row=0, sticky=EW, columnspan=2)

    def checkHistoricalSelected():
        if(stockSearchType.get() == 'Historical Data'):
            datePickerFrame.grid(column=0, row=2, sticky=NSEW, pady=(20, 0))
        else:
            datePickerFrame.grid_forget()

    stockSearchTypes = ['Company Info', 'Current Quote', 'Historical Data']
    stockSearchType = StringVar()
    stockSearchType.set(stockSearchTypes[0])
    stockSearchTypeMenu = OptionMenu(stockWidgets, stockSearchType, *stockSearchTypes, command=lambda event: checkHistoricalSelected())
    stockSearchTypeMenu.grid(column=0, row=1, sticky=NSEW, columnspan=2)

    # (for stock search) historical data date picker
    datePickerFrame  = Frame(stockWidgets)

    dateInstructions = Label(datePickerFrame, text='Enter date')
    dateInstructions.grid(column=0, row=0, sticky=NSEW, columnspan=2)

    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    month = StringVar()
    month.set(months[0])
    monthLabel = Label(datePickerFrame, text='Month')
    monthLabel.grid(column=0, row=1, sticky=NSEW, padx=3)
    monthInput = OptionMenu(datePickerFrame, month, *months)
    monthInput.grid(column=1, row=1, sticky=NSEW)

    days = []
    for i in range(31):
        days.append(i + 1)
    day = IntVar()
    day.set(days[0])
    dayLabel = Label(datePickerFrame, text='Day')
    dayLabel.grid(column=0, row=2, sticky=W, padx=3)
    dayInput = OptionMenu(datePickerFrame, day, *days)
    dayInput.grid(column=1, row=2, sticky=NSEW)

    years = []
    for i in range(22):
        years.append(2000 + i)
    year = IntVar()
    year.set(years[len(years) - 1])
    yearLabel = Label(datePickerFrame, text='Year')
    yearLabel.grid(column=0, row=3, sticky=W, padx=3)
    yearInput = OptionMenu(datePickerFrame, year, *years)
    yearInput.grid(column=1, row=3, sticky=NSEW)

    root.mainloop()

# shows reddit posts inside scroll frame in application
def addRedditPostToFrame(postFrame: Widget, posts):
    
    def openPost(postID: str, subreddit: str):
        webbrowser.open("https://www.reddit.com/r/%s/comments/%s" % (subreddit, postID), new=2)

    def openUser(username):
        webbrowser.open("https://www.reddit.com/user/%s" % (username), new=2)

    def stockSelection(stock):
        stockSearch(postFrame, stock, 'Current Quote', None, None, None, None)

    titleMaxWidth = 65
    buttonCount = 3

    entryFrame = Frame(postFrame)
    entryFrame.grid(row=0, column=0, sticky=NSEW, padx=1, pady=1)

    labels = ['Subreddit', 'Post Title', 'Symbols', 'Upvotes', 'Downvotes', 'Date', 'Poster', 'User Karma', 'Account Creation Date', 'Actions']
    # Labels for table
    for i in range(len(labels)):
        label = Label(entryFrame, text=labels[i], fg='white', bg='#454545', padx=2, pady=2)
        label.grid(row=0, column=i, padx=1, pady=1, sticky=NSEW)
        
        if(labels[i] == 'Actions'):
            label.grid(row=0, column=i, padx=1, pady=1, sticky=NSEW, columnspan=buttonCount)

    keys = ['subreddit', 'title', 'tickers_string', 'upvotes', 'downvotes', 'date', 'poster', 'poster_karma', 'poster_acc_creation_date']

    for i in range(len(posts)):
        
        for j in range(len(keys)):
            text = posts[i].get(keys[j])
            label = Label(entryFrame, text=text, bg="#6b6b6b", fg='white', padx=2, pady=2)
            label.grid(row=i+1, column=j, sticky=NSEW, padx=1, pady=2)

            if(keys[j] == 'title'):
                label.config(width=50)
                if(len(text) > titleMaxWidth):
                    label.config(text=text[:47] + "...")

        openPostButton = Button(entryFrame, text="Open Post", borderwidth=1, bg="#a3a3a3", fg='white', command=lambda i=i: openPost(posts[i].get('post_id'), posts[i].get('subreddit')))
        openPostButton.grid(row=i+1, column=len(keys), padx=1, pady=1, sticky=NSEW)

        openUserButton = Button(entryFrame, text="Open User", borderwidth=1, bg="#a3a3a3", fg='white', command=lambda i=i: openUser(posts[i].get('poster')))
        openUserButton.grid(row=i+1, column=len(keys)+1, padx=1, pady=1, sticky=NSEW)

        selectedStock = StringVar()
        selectedStock.set("Select symbol for search")
        stockSelector = OptionMenu(entryFrame, selectedStock, "Select symbol for search", *posts[i].get('tickers_arr'), command=lambda selectedStock=selectedStock: stockSelection(selectedStock))
        stockSelector.grid(row=i+1, column=len(keys)+2, padx=1, pady=1, sticky=NSEW)

    postCanvas.yview_moveto(0)
    postCanvas.xview_moveto(0)

# shows stock information inside scroll frame in application
def addStockInfoToFrame(postFrame: Widget, data, labels):
    
    stockFrame = Frame(postFrame)
    stockFrame.grid(row=0, column=0, sticky=NSEW, padx=1, pady=1)

    for i in range(len(labels)):
        label = Label(stockFrame, text=labels[i], fg='white', bg='#454545', padx=2, pady=2)
        label.grid(row=0, column=i, padx=1, pady=1, sticky=NSEW)

        info = Label(stockFrame, text=data[labels[i]], fg='white', bg='#6b6b6b', padx=2, pady=2)
        info.grid(row=1, column=i, padx=1, pady=1, sticky=NSEW)
