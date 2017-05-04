import requests
from bs4 import BeautifulSoup
import pandas
import os


page = requests.get("https://www.forexfactory.com/calendar.php?day=today")
content = page.content

soup = BeautifulSoup(content,"html.parser")

table = soup.find_all("tr",{"class":"calendar_row"})
#print(table)

forcal = []
for item in table:
    dict = {}
    
    dict["Currency"] = item.find_all("td", {"class":"calendar__currency"})[0].text #Currency
    dict["Event"] = item.find_all("td",{"class":"calendar__event"})[0].text.strip() #Event Name
    dict["Time_Eastern"] = item.find_all("td", {"class":"calendar__time"})[0].text #Time Eastern
    impact = item.find_all("td", {"class":"impact"})
    
    for icon in range(0,len(impact)):
        dict["Impact"] = impact[icon].find_all("span")[0]['title'].split(' ', 1)[0]

    dict["Actual"] = item.find_all("td", {"class":"calendar__actual"})[0].text #Actual Value
    dict["Forecast"] = item.find_all("td", {"class":"calendar__forecast"})[0].text #forecasted Value
    dict["Previous"] = item.find_all("td", {"class":"calendar__previous"})[0].text # Previous
    forcal.append(dict)

df = pandas.DataFrame(forcal)

df = df[["Currency","Event", "Impact","Time_Eastern", "Actual","Forecast", "Previous"]]
df = df[df["Impact"] == "High"]


path = '../templates/forexcal.html'


cwd = os.getcwd()
path = cwd + "\\templates" +"\\forexcal.html"
df.to_html(path,index=False)

with open(path,'r+') as f:
    content = f.read()
    f.seek(0, 0)
    f.write("{%  extends \"tools.html\" %}\n{% block forexcalendar %}\n" + content + "\n {%endblock%}")

