import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas, numpy as np
import os
from sqlalchemy import create_engine
from pandas.io import sql


###Setting up Postgres DB
engine = create_engine('postgres://wfmnyfwdodwjvj:49cb5d80d43011be38a957cf42bc0340bb454552a0ad1274a988d99fc31f4170@ec2-54-225-119-223.compute-1.amazonaws.com:5432/d60uuffk20up1i')

####BeautifulSoup WebScraping
page = requests.get("https://www.forexfactory.com/calendar.php?day=today")
content = page.content

soup = BeautifulSoup(content,"html.parser")

table = soup.find_all("tr",{"class":"calendar_row"})
#print(table)

forcal = []
for item in table:
    dict = {}
    dict["Date"] = datetime.today()
    dict["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text #Currency
    dict["Event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
    dict["Time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
    impact = item.find_all("td", {"class":"impact"})
    
    for icon in range(0,len(impact)):
        dict["Impact"] = impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]

    dict["Forecast"] = item.find_all("td", {"class":"calendar__forecast"})[0].text #forecasted Value
    dict["Previous"] = item.find_all("td", {"class":"calendar__previous"})[0].text # Previous
    forcal.append(dict)

###Pandas - to clean table 
df = pandas.DataFrame(forcal)

df['Time_Eastern'] = df['Time_Eastern'].replace("", np.nan).fillna(method='ffill')
df = df[["Date", "Currency","Event", "Impact","Time_Eastern","Forecast", "Previous"]]
df = df[df["Impact"] == "High"]


###Appends data to Postgres
df.to_sql('events', engine, if_exists = "replace")
