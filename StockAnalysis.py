# =====================================================================================#
#
# File: FinanceProject.py
# Current Author: Ayokunlemi (Kay) Yomi-Badejo.
#
# Previous Author: None.
#
# Contact Info: kay.badejo@gmail.com
#
# Purpose : Stock Analysis within specified date ranges (using user input)
#
# Dependencies: {Pandas modules, Access to stock Market database (yfinance), Datetime modules,
# OS module}
#
# Modification Log:
#       --> Created 2023-05-13
#       --> Updated 2024-03-05


# Import necessary Modules

import pandas as pd

import pandas_datareader as pdr

import datetime

from datetime import date

import yfinance as yf

import os

# Variables

# Create relative path for UserLogin csv file (this will serve as a pseudo-database for login details.
absolute_path = os.path.dirname(__file__)
relative_path = "./UserLogins.csv"
path = os.path.join(absolute_path, relative_path)



# Create a dataframe to allow for searching user log in details.
userDB = pd.read_csv(path, skiprows=1,
                     sep=',',
                     names=('Username', 'Password'),
                     engine='python')

# Allow full Width of teh data frame to show
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)


# FileDate saves the date of user login which is used to store any stock analysis in a date specific format.
def logIn():
    global fileDate
    print(
        "\n***********************************************************************************************"
    )
    print("LOG-IN/CREATE AN ACCOUNT")
    print("***********************************************************************************************")
    global user
    global fileDate
    user = input("Do you have an account? (Y/N): ").upper()
    fileDate = str(datetime.date.today())


logIn()


# User Log in/ create account

# Checks the "Database for user login details"
def searchUserDB(userName, passWord):
    global userValid
    userValid = False
    for i in range(len(userDB)):
        if userName == str(userDB.loc[i]['Username']) and passWord == str(userDB.loc[i]['Password']):
            userValid = True


def userLogIn():
    global foldername
    if user == 'Y':
        userName = input("enter your username ")
        passWord = input("enter your password ")
        searchUserDB(userName, passWord)
        if not userValid:
            print("doesn't match records, please try again")
            userLogIn()
        else:
            foldername = userName + passWord

    elif user == 'N':
        userName = input("please create a username ")
        passWord = input("please create a password ")
        searchUserDB(userName, passWord)
        if userValid:
            print("username is taken please enter a different username")
            username = input('enter a new username')
            password = input('enter a new password')
            searchUserDB(username, password)
            while userValid:
                print("username is taken please enter a different username")
                username = input('enter a new username')
                password = input('enter a new password')
                searchUserDB(username, password)

            foldername = username + password
            userDB.loc[len(userDB.index)] = [username, password]
            userDB.to_csv(path, index=False)


        else:
            foldername = userName + passWord
            userDB.loc[len(userDB.index)] = [userName, passWord]
            userDB.to_csv(path, index=False)
    else:

        print("Please enter a valid response (Y/N")
        logIn()
        userLogIn()


userLogIn()


def startDate():
    # Set dates.

    choice = input("Is your start day today? (Y/N) ").upper()

    dt = datetime.date.today()
    global dates

    if choice == 'Y':
        dates = dt
        print(dates)

    elif choice == 'N':
        dayInput = input("Enter desired start date(DD/MM/YYYY)").split('/')

        day = int(dayInput[0])
        month = int(dayInput[1])
        year = int(dayInput[2])

        dates = date(year, month, day)
        global dayInital
        dayInital = dates + datetime.timedelta(days=1)
        print(dates)

    else:
        print("please choose from Y/N")
        startDate()


startDate()


def endDate(dayInital):
    global duration
    duration = int(input("duration of analysis (in days): "))
    global ends
    ends = dayInital - datetime.timedelta(days=duration)
    print(ends)


endDate(dates)


def whatStock():
    global stk
    stk = input("what Stock are you interested in?").upper()


whatStock()


# Get Stock and refine the dataframe


def getStocks():
    dfStock = yf.download(stk, start=ends, end=dates, progress=False)
    return dfStock


getStocks()


def removeTime(df):
    newDateList = []
    dateList = list(df.index.values)
    for i in range(0, len(dateList)):
        dateStr = str(dateList[i])
        itemList = dateStr.split("T")
        newDateList.append(itemList[0])
    df["Date"] = newDateList
    df.set_index("Date", inplace=True)


dfInitial = getStocks()
removeTime(dfInitial)

# add %change in volume and close price


# Loop through database and update final database


dfBase = dfInitial[['Close', 'Volume']].copy()
dfBase['Volume % Change'] = 0
dfBase['Close % Change'] = 0
closeChange = 3
volChange = 2



# path

# This path creates/modifies a user specific folder

dirPath = os.path.join(absolute_path, f'./{foldername}')


def volumeChange():
    print("\n****************************************************************************")
    print(f"Daily Percent Changes - {dates} to {ends} to *{stk}*")
    print("****************************************************************************")

    for i in range(0, len(dfBase)):

        if i == 0:
            dfBase.iat[0, closeChange] = 0.0000
            dfBase.iat[0, volChange] = 0.0000



        else:

            oldClose = dfBase['Close'].iloc[i - 1]
            newClose = dfBase['Close'].iloc[i]
            oldVolume = dfBase['Volume'].iloc[i - 1]
            newVolume = dfBase['Volume'].iloc[i]
            dfBase.iat[i, closeChange] = round(((newClose - oldClose) / oldClose), 7)

            dfBase.iat[i, volChange] = round(((newVolume - oldVolume) / oldVolume), 7)

    print(dfBase)

    dfVolSum = dfBase['Volume % Change'].sum()
    dfClosSum = dfBase['Close % Change'].sum()

    print("\n****************************************************************************")
    print(f"Summary of Cumulative changes to *{stk}* from {dates} to {ends}")
    print("****************************************************************************")
    print(f"\nPercentage Volume Change: {dfVolSum}")
    print(f"Percentage Close Change: {dfClosSum}")

    csvPath = f"/{foldername}_{stk}_{dates}-{ends}.csv"

    # checks if the folder path exist, if it doesn't, makes a new folder.

    if os.path.isdir(dirPath):
        dfBase.to_csv(dirPath + csvPath, index=False)

    else:
        os.makedirs(dirPath)

        dfBase.to_csv(dirPath + csvPath, index=False)


volumeChange()


def cont():
    startDate()
    endDate(dates)
    whatStock()
    getStocks()
    dfInitial = getStocks()
    removeTime(dfInitial)
    volumeChange()


def loop():
    repeat = True

    while repeat:
        print("\n__________________________________________________________________________________"
              )
        print("STOCK REPORT OPTIONS")
        print("__________________________________________________________________________________")
        print("1. Report changes for stock")
        print("2. Log-out")
        userCon = input("")

        if userCon == "1":
            cont()

        elif userCon == "2":
            repeat = False
            print("Goodbye")

        else:
            print("please enter valid input (1/2)")
            loop()


loop()
