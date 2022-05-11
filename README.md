# General Programming Projects
Collection of projects including natural language processing, Markov models, probabilistic data linkage etc.

## NOTE: Please do not distribute code as it is meant for demonstration purposes only.

# 1) Course Selector App: 

Develop web application that will find courses on the UChicago college catalog which matches a set of user preferences such as enrollment bounds, class meeting times, and walking distance from one building to another. The first step is to develop a web crawler to construct an index of classes on the UChicago college catalog. The second step is to build the full backend of the search tool, combining information with individual serches to give the user a list of results which match their requirements.

(Example of potential user preferences: "Find all courses that have Plato in their description, meet on Tuesdays between 10:30am and 3pm, and are within a 10 minute walk of the Ryerson Building")

COURSE: CMSC 12200 "Computer Science with Applications", Instructor: Matthew Wachs, reference: https://www.classes.cs.uchicago.edu/archive/2019/winter/12200-1/pa/pa2/index.html; https://www.classes.cs.uchicago.edu/archive/2019/winter/12200-1/pa/pa3/index.html

THANKS TO: Nicholas Thom

# 2) Probabilistic Data Linkage: 

Assignment to link a pair of datasets containing restaurant names and addresses and link them, i.e., find records in the two datasets that refer to the same restaurant, even if they are spelled or refered to differently (e.x. "Lou Mitchell's" V.S. "Lou's" / "McDonalds" V.S. "Maccas" etc.)

COURSE: CMSC 12200 "Computer Science with Applications", Instructor: Matthew Wachs; reference: https://www.classes.cs.uchicago.edu/archive/2019/winter/12200-1/pa/pa4/index.html

# 3) Speaker prediction using markov models and hash tables: 

Develop custom hash table to construct k-th order markov model which will predict the speaker of a given text given a training set of speaker-text data.

COURSE: CMSC 12300 "Computer Science with Applications", Instructor: Matthew Wachs; reference: https://www.classes.cs.uchicago.edu/archive/2019/winter/12200-1/pa/pa5/index.html

# 4) Processing streaming data with a thread pool:

Implementing a thread pool to handle the 1.USA.gov clicks public stream data using C. First making the data thread-safe, then implementing a thread pool with worker threads to handle the aformentioned data.

COURSE: CMSC 12300 "Computer Science with Applications", Instructor: Matthew Wachs; reference: https://www.classes.cs.uchicago.edu/archive/2020/spring/12300-1/pa3.html

# 5) Analyzing the White House visitor logs using MapReduce

Develop MapReduce code to extrapolate lists of guests who visited the White House based on various conditions:
    1. A list of the guests who visited at least ten times (task1.py).
    2. A list of the ten most frequently-visited staff members (task2.py).
    3. A list of the guests who visited at least once in both 2009 and 2010 (task3.py).
    4. A list of the people who were both guests and staff (in other words, someone whom is visited) in 2009 and / or 2010 (as long as someone visited at any point across the two years, and was visited at any point across the two years, they count, whether or not these two events occurred in the same year) (task4.py).
    
# 6) Basic Game Theory reduction with C

Use C to create a simple game reduction table to find the Nash Equilibrium of a given game, taking into account games that cannot be reduced.
    
COURSE: CMSC 12300 "Computer Science with Applications", Instructor: Matthew Wachs; reference: https://www.classes.cs.uchicago.edu/archive/2020/spring/12300-1/pa2/

# 7) Implementing Gram-Schmidt Orthonormalization:

Use Python to develop a simple Gram-Schmidt procedure used in linear algebra.
    
COURSE: MENG 25610 "Applied Scientific Computing in Molecular Engineering", Instructor: Marco Govoni

# 8) Implementing MPI (parallel programing) to a single-thread analysis of atomic structures.

Use mpi4py to parallelize a single-thread program which calculates a radial distribution function (RDF) to analyze results of molecular dynamics simulation of water.
    
COURSE: MENG 25610 "Applied Scientific Computing in Molecular Engineering", Instructor: Marco Govoni

# 9) Implementing Fourier Transformation to analyze noisy signals:

Given a periodic signal, smoothen out the signal by removing the noise using a fourier transform process.
    
COURSE: MENG 25610 "Applied Scientific Computing in Molecular Engineering", Instructor: Marco Govoni

# 10) News Sentiment Analysis:

Using webscraped data for select news sources from different countries (SCMP - China, BBC - UK, RT - RU etc.), develop a web-app which:

1) Visualizes the frequent terms used in select region's news source
2) Conducts general sentiment analysis of given news source using NLTK
3) Predicts the source of articles of unknown origin using a k-th level markov model.

COURSE: CMSC 12200 "Computer Science with Applications", Instructor: Matthew Wachs

THANKS TO: Calvin Zhang, Nicholas Thom, Charles Hong 
