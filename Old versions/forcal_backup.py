import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas, numpy as np
import os
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Column, Table, ForeignKey
from sqlalchemy import Integer, String, Date
from pandas.io import sql
from sqlalchemy.ext.declarative import declarative_base



###Setting up Postgres DB
engine = create_engine('postgres://wfmnyfwdodwjvj:49cb5d80d43011be38a957cf42bc0340bb454552a0ad1274a988d99fc31f4170@ec2-54-225-119-223.compute-1.amazonaws.com:5432/d60uuffk20up1i', echo=True)

'''
###Create SQLAlchemy Schema
metadata = MetaData(bind=engine)

events_table = Table('events', metadata,
            Column('id',Integer, primary_key=True),
            Column('Date', Date),
            Column('Currency', String),
            Column('Event', String),
            Column('Time_Eastern', String),
            Column('Impact', String),
            Column('Forecast', Integer),
            Column('Previous', Integer),
                    )
metadata.create_all()
'''
'''
###Create SQLAlchemy Mapping
Base = declarative_base()
class events(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    Date = Column('Date', Date)
    Currency = Column('Currency', String)
    Event = Column('Event', String)
    Time_Eastern = Column('Time_Eastern', String)
    Impact = Column('Impact', String)
    Forecast = Column('Forecast', String)
    Previous = Column('Previous', String)

    def __init__(self, Date, Currency, Event, Time_Eastern, Impact, Forecast, Previous):
        self.Date = Date
        self.Currency = Currency
        self.Event = Event
        self.Time_Eastern = Time_Eastern
        self.Impact = Impact
        self.Forecast = Forecast
        self.Previous = Previous


events.__table__.drop(engine)

'''
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

df = pandas.DataFrame(forcal)

df['Time_Eastern'] = df['Time_Eastern'].replace("", np.nan).fillna(method='ffill')
df = df[["Date", "Currency","Event", "Impact","Time_Eastern","Forecast", "Previous"]]
df = df[df["Impact"] == "High"]

engine = create_engine('postgres://wfmnyfwdodwjvj:49cb5d80d43011be38a957cf42bc0340bb454552a0ad1274a988d99fc31f4170@ec2-54-225-119-223.compute-1.amazonaws.com:5432/d60uuffk20up1i')



df.to_sql('events', engine, if_exists = "append")


'''
path = '../templates/forexcal.html'

cwd = os.getcwd()
path = cwd + "\\templates" +"\\forexcal1.html"
df.to_html(path,index=False)

with open(path,'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write("{%  extends \"tools.html\" %}\n{% block forexcalendar %}\n" + content + "\n {%endblock%}")

'''