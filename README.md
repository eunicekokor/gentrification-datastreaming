# gentrification-datastreaming
List of Repositories Used:
[311 complaints fetching & analyzing](#1234): https://github.com/eunicekokor/polling-db
[Finding & Tracking Gentrification Using Methods That Were Defined](#gent) https://github.com/samnnodim/nyc-housing
Foursquare and Twitter Stream analyzing

311 Complaints Fetching

<a name="1234">NYC 311 Complaints</a>
================================
## File Overviews
*Comparing periods of gentrification to our stats of how many complaints per neighborhood occured in various time periods from 2010-2015*

Uses the NYC [311-Service-Requests-from-2010-to-Present](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9) API to get the number of complaints for all of New York City. Creates a Redis store full of NYC Complaint Data. It also uses a Flask app also that returns data on periods of gentrification & complaint information.

### Python Files
#### `311.py`
This gets historical and realtime 311 complaints and adds it to a Redis store. We only run this once.
#### `server.py`
This displays gentrifying periods as well as neighborhood 311 complaints, through a span of five years using Flask as a server and Pygal to display graphs.
### Static Files
#### `population.json`
This gets historical and realtime 311 complaints and adds it to a Redis store.
#### `threemonths.txt`
Gentrification intervals for neighborhoods based off of NYC Housing data drawn from `query_mongo.py`
#### `sixmonths.txt`
Gentrification intervals for neighborhoods based off of NYC Housing data drawn from `query_mongo.py`
#### `oneyear.txt`
Gentrification intervals for neighborhoods based off of NYC Housing data drawn from `query_mongo.py`
#### `twoyears.txt`
Gentrification intervals for neighborhoods based off of NYC Housing data drawn from `query_mongo.py`
#### `zillow_to_docp_mapping.json`
Our neighborhood names were not a 1-1 match from `query_mongo.py` (based on Zillow neighborhood definitions to the standardized neighborhood names) so we created our own mapping that included neighborhoods we missed. 

### Usage w/ Complete Installation Instructions

####How We View All 311 Complaints By Neighborhood
Install Redis using istructions here: http://redis.io/topics/quickstart
Redis `redis-cli -n 0` to access our DB from the command line.
`keys *` to see all the neighborhoods
`LRANGE key 0 -1`  where `key` is the name of one of our neighborhood keys. The neighborhood keys are stored in the format: `Neighborhood Name/Borough`. For each complaint found in `311.py`, the complaint is appended to a Redis list of complaints ordered by our neighborhood key.

If you want to try this on your own machine:
Make sure you have Redis running
Run: `pip install requests time redis urllib3 pymongo` to install required dependencies
Run: `python 311.py` in one window
Run the above steps in another window to see Redis results. It will take 30 seconds for the initial values to show up and a few days for all the values to show up (there are a few hundred thousand) due to the nature of the API and size of the dataset.

####How To View Raw Gentrification Periods
Two Year Period: http://54.152.176.233:5000/?p=oneyear
One Year Period: http://54.152.176.233:5000/?p=twoyears
These are views into for each neighborhood that was determined to be gentrified, a percent change in 311 complaints from one year to the next.
For example:

    "Borough Park": [
    {
      "delta": -16, 
      "end": 2012, 
      "prev": -17, 
      "start": 2011
    }, 
    {
      "delta": 12, 
      "end": 2015, 
      "prev": -14, 
      "start": 2014
    }
 
`delta` is the percent change in that interval. This is so we can track changes in 311 complaints in the years that we determined they gentrified.
`prev` is the percent change in the previous interval (because we'd liked to see, if there was complaint data from the previous interval, what the percent change was before this).
`start` is the starting interval year we are fetching a count of 311 complaints from
`end` is the ending interval year  we are fetching a count of 311 complaints from

You can also run this locally!
However you *must* have data from the years 2010-2015.
Install all dependencies
Run: `pip install flask redis json pygal flask bson json_util pprint`
`python server.py` and go to `localhost:5000/?p=twoyears` or `localhost:5000/?p=oneyear` in a browser 


<a name="gent">:house: NYC Housing Data :house:</a>
================================
###### *"Tracking Periods of Gentrification from 2010-2015 and the neighborhoods by which they gentrified*

Uses the [Quandl API](https://www.quandl.com/) to get housing data for all of New York City. Creates a Redis store full of NYC Housing Data. Uses a Flask app to creates a RESTful API that can be used to get relevant statistics on dataset and make visualisations.

## File Overviews
#### `config.py`
This is a python file that is used to hide the Quandl API key
#### `get_data_from_quandl.py`
This inserts Zillow data from the Quandl API into a MongoDB Store
#### `query_mongo.py`
This query'se the mongo store and creates
#### `test.py`
This is our server which can access information based on data collected in our server.

### Usage

Note: First make sure you have the following Python libraries installed. 

Run: 
`pip install Quandl requests pandas pymongo`


1. Create file config which holds Quandl API key

	`config.py`
	
2. Put the API key from Quandl into config.py

	`echo apiKey = "YOUR_API_KEY" > config.py`

3. Populate a local Mongo store
	
	`python get_data_from_quandl.py` 
	
4. Query the store, to get gentrification data for a particular interval: `(3,6,12,24)`

	`python query_mongo.py <interval>`

 

