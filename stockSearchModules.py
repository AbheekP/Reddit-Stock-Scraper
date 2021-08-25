from numpy.lib.function_base import average
from apiModules import finnhubExecution
import numpy
import re
from datetime import date
from datetime import timedelta
from apiModules import alphaVantageExecution
from pandas.tseries.holiday import USFederalHolidayCalendar

# --------------------- Current Stock Information (Finnhub) --------------------- #

# Determines if the given ticker symbol is an actual symbol
def isValidSymbol(symbol):
    query = "/search?q=" + symbol
    results = finnhubExecution(query).json()

    if results['count'] == 0:
        return False

    for i in range(results['count']):
        if results['result'][i]['symbol'] == symbol:
            return True

    return False

# Returns the profile of the company associated with the ticker symbol. 
def getCompanyProfile(symbol):
    if not isValidSymbol(symbol):
        return None
    
    query = "/stock/profile2?symbol=" + symbol
    results = finnhubExecution(query).json()

    info = {
        'Company': results['name'],
        'Symbol': results['ticker'],
        'Industry': results['finnhubIndustry'],
        'Exchange': results['exchange'],
        'Market Cap': results['marketCapitalization'],
        'IPO Listing Date': results['ipo'],
        'Website': results['weburl']
    }

    return info

# Returns quote of the stock, including current, open, close, and change in price
def getQuote(symbol):
    if not isValidSymbol(symbol):
        return None
    
    query = '/quote?symbol=' + symbol
    results = finnhubExecution(query).json()

    info = {
        'Symbol': symbol,
        'Open': results['o'],
        'Current': results['c'],
        'Change': str(results['d']) + " (" + str((results['dp']))[0:5] + "%)",
        "Previous Close": + results['pc'],
        'Day High': results['h'],
        'Day Low': results['l']
    }

    return info

# --------------------- Historical Stock Information (Alpha Vantage) --------------------- #

# Returns the closing price of a stock on a certain date
def getPriceOnDate(symbol, dateInput: date, compact=False):
    if not isValidSymbol(symbol):
        return None
    
    query = "function=TIME_SERIES_DAILY_ADJUSTED&symbol=" + symbol
    r = alphaVantageExecution(query, compact).json()
    
    # If inputted date is a holiday, then find a previous day that wasn't a holiday
    inputYear = str(dateInput.year)
    holidays = USFederalHolidayCalendar().holidays(start=inputYear + "-01-01", end=inputYear + "-12-31")
    if str(dateInput) in holidays:
        holiday = True
        while holiday:
            dateInput -= timedelta(days=1)
            holiday = str(dateInput) in holidays

    # if inputted date is a weekend, then change date to the previous friday
    if dateInput.isoweekday() == 6:             
        dateInput -= timedelta(days=1)
    elif dateInput.isoweekday() == 7:           
        dateInput -= timedelta(days=2)

    try:
        datePrice = r['Time Series (Daily)'][str(dateInput)]
    except KeyError:
        return None

    return float(datePrice["5. adjusted close"])

def getDifference(symbol, dateInput):
    
    currentQuote = getQuote(symbol)

    datePrice = getPriceOnDate(symbol, dateInput)
    if(datePrice == None):
        return "Symbol not found"

    currentPrice = currentQuote['Current']
    percentageChange = str(round((currentPrice / datePrice - 1) * 100, 2))
    actualChange = currentPrice - datePrice

    prevWeek = getPriceOnDate(symbol, date.today() - timedelta(weeks=1), compact=True)
    prevMonth = getPriceOnDate(symbol, date.today() - timedelta(weeks=4))
    prev6Month = getPriceOnDate(symbol, date.today() - timedelta(weeks=(4*6)))
    prevYear = getPriceOnDate(symbol, date.today() - timedelta(weeks=52))


    # Determines if stock has been bullish or bearish over a period of time
    if(prevWeek == None):
        weekTrend = 'null'
    else:
        weekTrend = "BULL" if currentPrice > prevWeek else "BEAR"

    if(prevMonth == None):
        monthTrend = 'null'
    else:
        monthTrend = "BULL" if currentPrice > prevMonth else "BEAR"

    if(prev6Month == None):
        month6Trend = 'null'
    else:
        month6Trend = "BULL" if currentPrice > prev6Month else "BEAR"

    if(prevYear == None):
        yearTrend = 'null'
    else:
        yearTrend = "BULL" if currentPrice > prevYear else "BEAR"

    dayTrend = "BULL" if currentPrice > currentQuote['Open'] else "BEAR"

    info = {
        'Symbol': symbol,
        'Current Price': currentPrice,
        'Date Inputted': str(dateInput),
        'Price Then': datePrice,
        'Change (Percentage)': str(percentageChange) + " %",
        'Change (Absolute)': actualChange,
        "Day Trend": dayTrend,
        "Week Trend": weekTrend,
        "Month Trend": monthTrend,
        "6 Month Trend": month6Trend,
        "Year Trend": yearTrend,
    }

    return info

# ABML 6 MONTH TREND THROWS ERROR