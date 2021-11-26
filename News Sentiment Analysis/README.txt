This project is a News Sentiment Visualizer produced by Calvin Zhang, Allen (Yixin) Hu, Nicholas Thom, and Charles Hong.

Calvin Zhang and Nicholas Thom is primarily responsible for web-app launching and scraping;
Allen Hu is primarily responsible for NLP development to analyze the sentiment in the news (primarily during the start of COVID-19);
Charles Huang is primarily responsible for first-order Markov model to predict the source of a given article;

Notes from Calvin Zhang regarding running the app:

You need Wifi to run the app because it uses a live scraper. 
python3 app.py in our VM
Right click on https link after “Running on”, then Open Link
To quit app, CTRL-C in VM. Do NOT CTRL-Z because this will exit the app on the browser, but not fully in python. 
On rare occasions, e.g. due to Wifi hickups or the large amount of functionality we have, there might be a runtime error when you do python3 app.py
In this case, just reload the app again (python3 app.py).
For the NLP, you can train a new model by setting train_and_save parameter to True

Notes from Allen Hu regarding reddit API for sentiment analysis training data:
Reddit API user info:
	client_id='mjKYOVGPTg1tUQ',
	client_secret='ZQYXjepTZ71UNGWnxAZMy-Cj364',
	user_agent='akatyusha'
