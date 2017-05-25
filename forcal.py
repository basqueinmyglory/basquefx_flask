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

forecasts_calevents = []
for item in table:
    dict = {}
    dict["date"] = datetime.today()
    dict["currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text #Currency
    dict["event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
    dict["time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
    impact = item.find_all("td", {"class":"impact"})
    
    for icon in range(0,len(impact)):
        dict["impact"] = impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]

    dict["forecast"] = item.find_all("td", {"class":"calendar__forecast"})[0].text #forecasted Value
    dict["previous"] = item.find_all("td", {"class":"calendar__previous"})[0].text # Previous
    forecasts_calevents.append(dict)

###Pandas - to clean table 
df = pandas.DataFrame(forecasts_calevents)

df['time_Eastern'] = df['time_Eastern'].replace("", np.nan).fillna(method='ffill')
df = df[["date", "currency","event", "impact","time_Eastern","forecast", "previous"]]
df = df[df["impact"] == "High"]
df.index.names = ['id']

###Appends data to Postgres
df.to_sql('forecasts_calevents', engine, if_exists = "replace")
