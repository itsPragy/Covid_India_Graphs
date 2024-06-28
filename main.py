from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
import datetime 
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os


app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/graphs", StaticFiles(directory="graphs"), name="graphs")
data = pd.read_csv("datafiles\\covid_vaccine_statewise.csv")
data['Updated On'] = pd.to_datetime(data['Updated On'], format= '%d/%m/%Y', errors = 'coerce')

@app.get("/", response_class = HTMLResponse)
async def home(request: Request):
	states = data['State'].unique()
	return templates.TemplateResponse("home.html",{"request":request, "states":states})

@app.get("/state/{state}", response_class = HTMLResponse)
async def state(request: Request, state: str):
	df = data[data['State'].str.contains(state)]
	df.sort_values(by = 'Updated On')
	sns.scatterplot(x='Updated On', y='Total Doses Administered', data=df)
	plt.title(state)
	print(os.getcwd())
	link = "graphs\\{}.png".format(state)
	print(type(link))
	plt.savefig(link)
	link = '..\\..\\' + link
	return templates.TemplateResponse("state.html",{"request":request, 'link':link, 'state':state})

@app.post("/state/date/{state}", response_class = HTMLResponse)
async def date(request: Request, state:str):
	form  = await request.form()
	dates = dict(form)
	df = data[data['State'].str.contains(state)]
	df = df[(df['Updated On']>=dates['start']) & (df['Updated On']<=dates['end'])]
	df.sort_values(by = 'Updated On')
	sns.scatterplot(x='Updated On', y='Total Doses Administered', data=df)
	plt.title(state)
	link = "graphs\\{}.png".format(state+dates['start']+dates['end'])
	plt.savefig(link)
	link = "..\\..\\..\\" + link
	return templates.TemplateResponse("state.html",{"request":request, 'dates':dates, 'state':state, 'link':link})