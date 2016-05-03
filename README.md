# gentrification-datastreaming
List of Repositories Used:
- [311 complaints fetching & analyzing](#1234): https://github.com/eunicekokor/polling-db
- [Finding & Tracking Gentrification Using Methods That Were Defined](#gent) https://github.com/samnnodim/nyc-housing
- [Foursquare and Twitter Stream analyzing](#fsquare)


<a name="1234">NYC 311 Complaints</a>
================================

Uses the NYC 311-Service-Requests-from-2010-to-Present API to get the number of complaints for all of New York City. Creates a Redis store full of NYC Complaint Data. It also uses a Flask app also that returns data on periods of gentrification & complaint information. Charted with pygal, external library. Link: http://www.pygal.org/en/latest/documentation/types/line.html.

## File Overviews
Comparing periods of gentrification to our stats of how many complaints per neighborhood occured in various time periods from 2010-2015

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

## Analysis
### The Objective of `311.py`
The objective was originally to get historical 311 Complaints to understand the data around disinvestment in neighborhoods. We didn't filter out for specific complaints because we felt that if true disinvestment was happening in a neighborhood, it wouldn't just be housing specific complaints. We only collected in the months of January, April, July, and October for 2 reasons. 1) We didn't think we would see verifiable evidence of gentrification in such a smaller period than 3 months. and 2) Fetching the data would have taken an extra week due to the extremely high number of complaints. So what we got from this was
1) a way to look at where the complaints
2) a way to look at when complaints where happening
3) a way to look at what types of complaints were happening
4) a way to look at how many complaints were happening in 1-3 (i.e. how many & where, how many and when, & how many and what types)

### What we learned from `311.py` Redis Inputs
1) There are 188 neighborhoods in new york with a lot of housing complaints in the past 5 years

Using & Searching through a demographic document on changes during a decade: http://www.urbanresearchmaps.org/plurality/
2) The highest # of complaints per neighborhood per person for the most part usually come out of areas with higher Black & Latino populations
3) The lowest # of complaints per neighborhood per person for the most part usually come out of areas with higher Black & Latino populations
4) For neighborhoods with significant demographic change from 2000 to 2010 (highest percentage changes of Black/White/Asian/Latino) there were no specific spectrum of how those


### What we learned from `server.py` gentrification intervals
`oneyear.txt` + 311 complaints during those gentrifying periods
#### Average rate changes during one year intervals
|interval | previous | current
----------|----------|--------
|2010-2011 | None     | -12.76923077
|2011-2012 | -20.26666667  | -3.433333333
|2012-2013 | -4.866666667 | 14
|2013-2014 | 16.85185185 | 15.77777778
|2014-2015 | 17.29166667 | -10.58333333

These all have different start/ending gentrifying periods, but we saw a general trend for there to be a 'negative start' and a sharp upwards increase for 1 or two years, and then sharp decrease. However, we didn't know if this was strong enough to indicate a 'gentrifing factor' of having rate patterns similar for their interval comparison.
#### 1) We learned that we can't find an absolute gentrifying factor for 311 complaints

### What we learned from `server.py` line graph outputs
Because we have the ability to look at whatever list of neighborhoods we want and see their complaints over time, we learned a few things:
1) The trends of the complaint graphs are similar on average
2) Neighborhoods that have gentrified have different complaint counts per person than neighborhoods that have not gentrified.



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

 
###<a name="fsquare">Foursquare Goals</a>

We used the number of Foursquare "interactions" at different points in time (checkins and user-generated photos) as a metric for economic activity and compare the level of economic activity in each neighborhood over different time intervals between 2010-present.

We wanted to see if in the historical Foursquare data there was a correlation in the amount of user-generated data in a neighborhood before or during its time period of gentrification, that is significant enough to investigate as a potential alerting condition for a system that alerts observers when alerting conditions are met signalling the onset of gentrification. Following the analysis of housing prices (sourced from Zillow) that identified NYC neighborhoods that gentrified (according to a subset of Freeman's criteria), we had a set of records of neighborhoods that gentrified and the corresponding time interval. The housing price analysis enumerated all one-year and two-year time intervals between 2010 to 2016, identifying NYC neighborhoods that gentrified during each.

Let G be the set of records (neighborhood_G, time interval_G) such that neighborhood_G gentrified during time interval_G. Let NG be the set of records (neighborhood_NG, time interval_NG) such that neighborhood_NG did not gentrify during time interval_NG.

For each record in G, we compute the relative change in amount of user-generated Foursquare data in neighborhood_G between time interval_G and the time interval of equal duration immediately preceding it. We do the same for each record in NG and compare change measurements in the set of gentrification instances and the set of non-gentrification instances. We repeat this experiment with measurements of change during time intervals instead of change between time intervals. We define the change in Foursquare user interactions per neighborhood nb during a time period interval to be: (amount of user-generated data in nb at end of interval)-(amount of user-generated data in nb in beginning of interval)/(amount of user-generated data in nb in beginning of interval) where (amount of user-generated data in nb in beginning of interval) = (amount of user-generated data in nb in the first 3 months of interval) and (amount of user-generated data in nb at end of interval) = (amount of user-generated data in nb during last 3 months of interval)

Methodology
Identifying neighborhoods

In order for any of the data to be useful, we needed a way to classify a (latitude, longitude) pair into an NYC neighborhood since all the APIs we used returned results with geo-coordinates rather than neighborhood labels. To solve this problem, we stored two sources of NYC neighborhood definitions (Zillow and NYC Dept of City Planning) into separate MongoDB collections, then wrote Python code that, given a geocoordinate, performs a geospatial query in MongoDB to return the polygon (neighborhood) that intersects with it. TODO link to this code

neighborhoods_docp.json
nyc_neighborhoods_zillow.json
How to collect Foursquare venue data for each neighborhood?

User-generated data such as tips and photos must be requested on a per-venue basis. Concretely, given a VENUE_ID, the API will return the tips and photos for that venue. We compiled a set of VENUE_IDs for each of the neighborhoods defined in NYC Dept of City Planning's Neighborhood Tabulation Areas, then requested the tips and photos for each VENUE_ID.

Foursquare's API doesn't allow us to request venues with a neighborhood parameter, so we had to devise a way to generate a set of VENUE_IDs in each neighborhood. Foursquare's API has an endpoint that accepts a geocoordinate parameter and returns VENUE_IDs of venues near that location. We found the centroid of each neighborhood polygon and used it to make an initial request for venues near that centroid. For each venue returned by Foursquare's API, we classified its neighborhood and stored the VENUE_ID in a MongoDB collection of VENUE_IDs for that neighborhood. Then, for all unexplored venue geocoordinates returned by the API that are located in the neighborhood of interest, we repeated the request, effectively performing a breadth-first-search.

As a result, we saved 10 - 200 Foursquare VENUE_IDs for each of 187 NYC Neighborhood Tabulation Areas in a MongoDB database named "foursquare_venues". For each of these venues, we requested tips and photos and saved their timestamps. All timestamps of data generated in a given neighborhood are stored in a single collection.

save_neighborhood_venue_ids.py
save_foursquare_interactions.py
Computing Changes in Amount of Foursquare User-Generated Data

Records in the format (neighborhood_G, time interval_G) are stored in a MongoDB database named "housing", in collections named "oneyear" and "twoyears" depending on the duration of time interval_G.

The first obstacle was that these records were computed with Zillow data whereas the Foursquare venues were mapped to neighborhood tabulation areas defined by NYC Dept of City Planning. We manually made a mapping between the neighborhood names defined by Zillow and those defined by DOCP.

docp_to_zillow_mapping.json
We computed the changes in amount of user-generated data between and during intervals of gentrification by examining every record in our "housing" database that was identified as a "gentrification" instance. Since our goal is to compare these changes to those in neighborhoods that did not gentrify during the same time interval, we enumerated all possible 1-year and 2-year time intervals between 2010-present. For each time interval, we iterated through all NYC neighborhoods, checking if we have observed a gentrification instance for this neighborhood during this time interval. If not, we classify this as an instance of non-gentrification and compute the changes in Foursquare user-generated data during and before this interval.

compute_fsq_interaction_changes.py

write_foursquare_changes_to_csv.py /changes_results fsq_gent_before_oneyear.csv fsq_nongent_before_oneyear.csv fsq_gent_during_oneyear.csv fsq_nongent_during_oneyear.csv
fsq_gent_before_twoyears.csv
fsq_nongent_before_twoyears.csv fsq_gent_during_twoyears.csv
fsq_nongent_during_twoyears.csv

We used d3.js to plot the changes to compare how they differ between intervals of gentrification vs non-gentrification. See results in /changes_results/plots

Streaming Tweet Distributions

We asked Matthew Huie, Foursquare Technical Account Manager, for access to the Foursquare firehose. He suggested using Twitter instead so we wrote and ran a daemon that saves the distribution of Tweets over neighborhoods every hour. We didn't have time to analyze the data.

tweets_by_neighborhood.py
tweet_distrib_api.py
query_tweet_dist_api_response.py
save_tweet_dist_api_response.py
