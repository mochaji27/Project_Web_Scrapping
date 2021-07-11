from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this


#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister-list'})
list = table.find_all('div', attrs={'class' : 'lister-item mode-advanced'})
row_length = len(list)

temp = [] #initiating a list 

for i in range(0, row_length):
#insert the scrapping process here
    header = list[i].find('h3', attrs = {'class':'lister-item-header'})
    judul = header.find('a').text
    try:
        rating_list = list[i].find('div', attrs={'class':'inline-block ratings-imdb-rating'})
        rating = rating_list.find('strong').text.strip()
    except:
        rating = 0
    
    try:
        meta_score = list[i].find('span', {'class':'metascore mixed'}).text.strip()
    except:
        meta_score = 0
        
        
    votes_bar = list[i].find('p', {'class':'sort-num_votes-visible'})
    
    try:
        votes = votes_bar.find('span', attrs={'name':'nv'}).text.strip().replace(',', '.')
    except:
        votes = 0

    genres = list[i].find('span', attrs={'class':'genre'}).text.strip().split(', ')
        
    temp.append((judul, rating, meta_score, votes))

#change into dataframe
df = pd.DataFrame(temp, columns=('Tittle', 'Rating', 'MetaScore', 'Vote'))

#insert data wrangling here
df['Rating'] = df['Rating'].astype('float64')
df['MetaScore'] = df['MetaScore'].astype('float64')
df['Vote'] = df['Vote'].astype('float64')
df = df.set_index('Tittle', drop=True).sort_values(by = 'Vote', ascending=False)


#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["Vote"].max().round(2)}' #be careful with the " and ' 
	# generate plot
	
	ax = df['Vote'].head(7).sort_values(ascending=True).plot(kind = 'barh', figsize = (15,5)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)