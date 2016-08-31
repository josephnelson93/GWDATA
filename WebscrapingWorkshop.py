'''
CLASS: Getting Data from APIs
What is an API?
- Application Programming Interface
- Structured way to expose specific functionality and data access to users
- Web APIs usually follow the "REST" standard
How to interact with a REST API:
- Make a "request" to a specific URL (an "endpoint"), and get the data back in a "response"
- Most relevant request method for us is GET (other methods: POST, PUT, DELETE)
- Response is often JSON format
- Web console is sometimes available (allows you to explore an API)
'''

# read IMDb data into a DataFrame: we want a year column!
import pandas as pd
# movies = pd.read_csv('imdb_1000.csv')
movies = pd.read_csv('https://raw.githubusercontent.com/josephnelson93/GWDATA/master/imdb_1000.csv')
movies.head()

# use requests library to interact with a URL
import requests
r = requests.get('http://www.omdbapi.com/?t=the shawshank redemption&r=json&type=movie')

# check the status: 200 means success, 4xx means error
r.status_code

# view the raw response text
r.text

# decode the JSON response body into a dictionary
r.json()

# extracting the year from the dictionary
r.json()['Year']

# what happens if the movie name is not recognized?
r = requests.get('http://www.omdbapi.com/?t=blahblahblah&r=json&type=movie')
r.status_code
r.json()

# define a function to return the year
def get_movie_year(title):
    r = requests.get('http://www.omdbapi.com/?t=' + title + '&r=json&type=movie')
    info = r.json()
    if info['Response'] == 'True':
        return int(info['Year'])
    else:
        return None

# test the function
get_movie_year('The Shawshank Redemption')
get_movie_year('blahblahblah')

# create a smaller DataFrame for testing
top_movies = movies.head().copy()

# write a for loop to build a list of years
from time import sleep
years = []
for title in top_movies.title:
    years.append(get_movie_year(title))
    sleep(1)

# check that the DataFrame and the list of years are the same length
assert(len(top_movies) == len(years))

# save that list as a new column
top_movies['year'] = years

'''
Bonus content: Updating the DataFrame as part of a loop
'''

# enumerate allows you to access the item location while iterating
letters = ['a', 'b', 'c']
for index, letter in enumerate(letters):
    print index, letter

# iterrows method for DataFrames is similar
for index, row in top_movies.iterrows():
    print index, row.title

# create a new column and set a default value
movies['year'] = -1

# loc method allows you to access a DataFrame element by 'label'
movies.loc[0, 'year'] = 1994

# write a for loop to update the year for the first three movies
for index, row in movies.iterrows():
    if index < 3:
        movies.loc[index, 'year'] = get_movie_year(row.title)
        sleep(1)
    else:
        break

'''
Other considerations when accessing APIs:
- Most APIs require you to have an access key (which you should store outside your code)
- Most APIs limit the number of API calls you can make (per day, hour, minute, etc.)
- Not all APIs are free
- Not all APIs are well-documented
- Pay attention to the API version
Python wrapper is another option for accessing an API:
- Set of functions that "wrap" the API code for ease of use
- Potentially simplifies your code
- But, wrapper could have bugs or be out-of-date or poorly documented





***THE FOLLOWING IS NOW DEPRECATED AS IMDB CHANGED THEIR WEB LAYOUT***

CLASS: Web Scraping with Beautiful Soup
What is web scraping?
- Extracting information from websites (simulates a human copying and pasting)
- Based on finding patterns in website code (usually HTML)
What are best practices for web scraping?
- Scraping too many pages too fast can get your IP address blocked
- Pay attention to the robots exclusion standard (robots.txt)
- Let's look at http://www.imdb.com/robots.txt
What is HTML?
- Code interpreted by a web browser to produce ("render") a web page
- Let's look at example.html
- Tags are opened and closed
- Tags have optional attributes
How to view HTML code:
- To view the entire page: "View Source" or "View Page Source" or "Show Page Source"
- To view a specific part: "Inspect Element"
- Safari users: Safari menu, Preferences, Advanced, Show Develop menu in menu bar
- Let's inspect example.html
'''

# read the HTML code for a web page and save as a string
with open('example.html', 'rU') as f:
    html = f.read()

# convert HTML into a structured Soup object
from bs4 import BeautifulSoup
b = BeautifulSoup(html)

# print out the object
print b
print b.prettify()

# 'find' method returns the first matching Tag (and everything inside of it)
b.find(name='body')
b.find(name='h1')

# Tags allow you to access the 'inside text'
b.find(name='h1').text

# Tags also allow you to access their attributes
b.find(name='h1')['id']

# 'find_all' method is useful for finding all matching Tags
b.find(name='p')        # returns a Tag
b.find_all(name='p')    # returns a ResultSet (like a list of Tags)

# ResultSets can be sliced like lists
len(b.find_all(name='p'))
b.find_all(name='p')[0]
b.find_all(name='p')[0].text
b.find_all(name='p')[0]['id']

# iterate over a ResultSet
results = b.find_all(name='p')
for tag in results:
    print tag.text

# limit search by Tag attribute
b.find(name='p', attrs={'id':'scraping'})
b.find_all(name='p', attrs={'class':'topic'})
b.find_all(attrs={'class':'topic'})

# limit search to specific sections
b.find_all(name='li')
b.find(name='ul', attrs={'id':'scraping'}).find_all(name='li')

'''
EXERCISE ONE
'''

# find the 'h2' tag and then print its text
b.find(name='h2').text

# find the 'p' tag with an 'id' value of 'feedback' and then print its text
b.find(name='p', attrs={'id':'feedback'}).text

# find the first 'p' tag and then print the value of the 'id' attribute
b.find(name='p')['id']

# print the text of all four resources
results = b.find_all(name='li')
for tag in results:
    print tag.text

# print the text of only the API resources
results = b.find(name='ul', attrs={'id':'api'}).find_all(name='li')
for tag in results:
    print tag.text

'''
Scraping the IMDb website
'''

# get the HTML from the Shawshank Redemption page
import requests
r = requests.get('http://www.imdb.com/title/tt0111161/')

# convert HTML into Soup
b = BeautifulSoup(r.text)
print b

# run this code if you have encoding errors
import sys
reload(sys)
sys.setdefaultencoding('utf8')

# get the actors
b.find_all(name='span', attrs={'class':'itemprop', 'itemprop':'name'})    # too many results
b.find(name='span', attrs={'class':'itemprop', 'itemprop':'name'}).text   # just get the first

# Shawshank Redemption, Flubber
list_of_movies = ['tt0111161', 'tt0119137']

# function to get the source code of two titles
from time import sleep
html = []
for movie in list_of_movies:
    r = requests.get('http://www.imdb.com/title/' + movie)  
    # print r.text
    b = BeautifulSoup(r.text)
    html.append(b)
    sleep(1)
html[0] # check it out


# gets rating vale
def get_rating_value(source_code):
    return float(source_code.find(name='span',  attrs={'itemprop':'ratingValue'}).text)
    
# loop the function and rating together
ratings = []
for source in html:
    ratings.append(get_rating_value(source))


# deprecated
# b.find(name='h1').find(name='span', attrs={'class':'itemprop', 'itemprop':'name'}).text   # limit the search








# get the star rating (as a float)
float(b.find(name='span', attrs={'itemprop':'ratingValue'}).text)
float(b.find(name='div', attrs={'class':'titlePageSprite star-box-giga-star'}).text)

'''
EXERCISE TWO
'''

# get the description
b.find(name='p', attrs={'itemprop':'description'}).text.strip()

# get the content rating
b.find(name='meta', attrs={'itemprop':'contentRating'})['content']

# get the duration in minutes (as an integer)
int(b.find(name='time', attrs={'itemprop':'duration'}).text.strip()[:-4])
int(b.find(name='time', attrs={'itemprop':'duration'})['datetime'][2:-1])

'''
OPTIONAL WEB SCRAPING PRACTICE
First, define a function that accepts an IMDb ID and returns a dictionary of
movie information: title, star_rating, description, content_rating, duration.
The function should gather this information by scraping the IMDb website, not
by calling the OMDb API. (This is really just a wrapper of the web scraping
code we wrote above.)
For example, get_movie_info('tt0111161') should return:
{'content_rating': 'R',
 'description': u'Two imprisoned men bond over a number of years...',
 'duration': 142,
 'star_rating': 9.3,
 'title': u'The Shawshank Redemption'}
Then, open the file imdb_ids.txt using Python, and write a for loop that builds
a list in which each element is a dictionary of movie information.
Finally, convert that list into a DataFrame.
'''

# define a function that accepts an IMDb ID and returns a dictionary of movie information
def get_movie_info(imdb_id):
    r = requests.get('http://www.imdb.com/title/' + imdb_id + '/')
    b = BeautifulSoup(r.text)
    info = {}
    info['title'] = b.find(name='span', attrs={'class':'itemprop', 'itemprop':'name'}).text
    info['star_rating'] = float(b.find(name='span', attrs={'itemprop':'ratingValue'}).text)
    info['description'] = b.find(name='p', attrs={'itemprop':'description'}).text.strip()
    info['content_rating'] = b.find(name='meta', attrs={'itemprop':'contentRating'})['content']
    info['duration'] = int(b.find(name='time', attrs={'itemprop':'duration'}).text.strip()[:-4])
    return info

# test the function
get_movie_info('tt0111161')

# open the file of IDs (one ID per row), and store the IDs in a list
imdb_ids = []
with open('imdb_ids.txt', 'rU') as f:
    imdb_ids = [row.strip() for row in f]

# get the information for each movie, and store the results in a list
from time import sleep
movies = []
for imdb_id in imdb_ids:
    movies.append(get_movie_info(imdb_id))
    sleep(1)

# check that the list of IDs and list of movies are the same length
assert(len(imdb_ids) == len(movies))

# convert the list of movies into a DataFrame
import pandas as pd
pd.DataFrame(movies, index=imdb_ids)

'''
Another IMDb example: Getting the genres
'''

# read the Shawshank Redemption page again
r = requests.get('http://www.imdb.com/title/tt0111161/')
b = BeautifulSoup(r.text)

# only gets the first genre
b.find(name='span', attrs={'class':'itemprop', 'itemprop':'genre'})

# gets all of the genres
b.find_all(name='span', attrs={'class':'itemprop', 'itemprop':'genre'})

# stores the genres in a list
[tag.text for tag in b.find_all(name='span', attrs={'class':'itemprop', 'itemprop':'genre'})]

'''
Another IMDb example: Getting the writers
'''

# attempt to get the list of writers (too many results)
b.find_all(name='span', attrs={'itemprop':'name'})

# limit search to a smaller section to only get the writers
b.find(name='div', attrs={'itemprop':'creator'}).find_all(name='span', attrs={'itemprop':'name'})

'''
Another IMDb example: Getting the URLs of cast images
'''

# find the images by size
results = b.find_all(name='img', attrs={'height':'44', 'width':'32'})

# check that the number of results matches the number of cast images on the page
len(results)

# iterate over the results to get all URLs
for tag in results:
    print tag['loadlate']

'''
Useful to know: Alternative Beautiful Soup syntax
''

# read the example web page again
with open('example.html', 'rU') as f:
    html = f.read()

# convert to Soup
b = BeautifulSoup(html)

# these are equivalent
b.find(name='p')    # normal way
b.find('p')         # 'name' is the first argument
b.p                 # can also be accessed as an attribute of the object

# these are equivalent
b.find(name='p', attrs={'id':'scraping'})   # normal way
b.find('p', {'id':'scraping'})              # 'name' and 'attrs' are the first two arguments
b.find('p', id='scraping')                  # can write the attributes as arguments

# these are equivalent
b.find(name='p', attrs={'class':'topic'})   # normal way
b.find('p', class_='topic')                 # 'class' is special, so it needs a trailing underscore
b.find('p', 'topic')                        # if you don't name it, it's assumed to be the class

# these are equivalent
b.find_all(name='p')    # normal way
b.findAll(name='p')     # old function name from Beautiful Soup 3
b('p')                  # if you don't name the method, it's assumed to be find_all
