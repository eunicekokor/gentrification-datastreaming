Goal
=====
We used the number of Foursquare "interactions" at different points in time (checkins and user-generated photos) as a metric for economic activity and compare the level of economic activity in each neighborhood over different time intervals between 2010-present.

We wanted to see if in the historical Foursquare data there was a correlation in the amount of user-generated data in a neighborhood before or during its time period of gentrification, that is significant enough to investigate as a potential alerting condition for a system that alerts observers when alerting conditions are met signalling the onset of gentrification. Following the analysis of housing prices (sourced from Zillow) that identified NYC neighborhoods that gentrified (according to a subset of Freeman's criteria), we had a set of records of neighborhoods that gentrified and the corresponding time interval. The housing price analysis enumerated all one-year and two-year time intervals between 2010 to 2016, identifying NYC neighborhoods that gentrified during each.

Let G be the set of records (`neighborhood_G`, `time interval_G`) such that `neighborhood_G` gentrified during `time interval_G`. Let NG be the set of records (`neighborhood_NG`, `time interval_NG`) such that `neighborhood_NG` did not gentrify during `time interval_NG`.

For each record in G, we compute the relative change in amount of user-generated Foursquare data in `neighborhood_G` between `time interval_G` and the time interval of equal duration immediately preceding it. We do the same for each record in NG and compare change measurements in the set of gentrification instances and the set of non-gentrification instances. We repeat this experiment with measurements of change during time intervals instead of change between time intervals. We define the change in Foursquare user interactions per neighborhood `nb` during a time period `interval` to be:
(amount of user-generated data in `nb` at end of interval)-(amount of user-generated data in `nb` in beginning of interval)/(amount of user-generated data in `nb` in beginning of interval)
where 
(amount of user-generated data in `nb` in beginning of interval) =
(amount of user-generated data in `nb` in the first 3 months of `interval`)
and
(amount of user-generated data in `nb` at end of interval) = 
(amount of user-generated data in `nb` during last 3 months of interval)


Methodology
============
Identifying neighborhoods
--------------------------
In order for any of the data to be useful, we needed a way to classify a (latitude, longitude) pair into an NYC neighborhood since all the APIs we used returned results with geo-coordinates rather than neighborhood labels. To solve this problem, we stored two sources of NYC neighborhood definitions (Zillow and NYC Dept of City Planning) into separate MongoDB collections, then wrote Python code that, given a geocoordinate, performs a geospatial query in MongoDB to return the polygon (neighborhood) that intersects with it. TODO link to this code

* neighborhoods_docp.json
* nyc_neighborhoods_zillow.json


How to collect Foursquare venue data for each neighborhood?
------------------------------------------------------------
User-generated data such as tips and photos must be requested on a per-venue basis. Concretely, given a VENUE_ID, the API will return the tips and photos for that venue. We compiled a set of VENUE_IDs for each of the neighborhoods defined in NYC Dept of City Planning's Neighborhood Tabulation Areas, then requested the tips and photos for each VENUE_ID.

Foursquare's API doesn't allow us to request venues with a neighborhood parameter, so we had to devise a way to generate a set of VENUE_IDs in each neighborhood. Foursquare's API has an endpoint that accepts a geocoordinate parameter and returns VENUE_IDs of venues near that location. We found the centroid of each neighborhood polygon and used it to make an initial request for venues near that centroid. For each venue returned by Foursquare's API, we classified its neighborhood and stored the VENUE_ID in a MongoDB collection of VENUE_IDs for that neighborhood. Then, for all unexplored venue geocoordinates returned by the API that are located in the neighborhood of interest, we repeated the request, effectively performing a breadth-first-search.

As a result, we saved 10 - 200 Foursquare VENUE_IDs for each of 187 NYC Neighborhood Tabulation Areas in a MongoDB database named "foursquare_venues". For each of these venues, we requested tips and photos and saved their timestamps. All timestamps of data generated in a given neighborhood are stored in a single collection.

* save_neighborhood_venue_ids.py
* save_foursquare_interactions.py


Computing Changes in Amount of Foursquare User-Generated Data
--------------------------------------------------------------
Records in the format (`neighborhood_G`, `time interval_G`) are stored in a MongoDB database named "housing", in collections named "oneyear" and "twoyears" depending on the duration of `time interval_G`.

The first obstacle was that these records were computed with Zillow data whereas the Foursquare venues were mapped to neighborhood tabulation areas defined by NYC Dept of City Planning. We manually made a mapping between the neighborhood names defined by Zillow and those defined by DOCP.

* docp_to_zillow_mapping.json

We computed the changes in amount of user-generated data between and during intervals of gentrification by examining every record in our "housing" database that was identified as a "gentrification" instance. Since our goal is to compare these changes to those in neighborhoods that did not gentrify during the same time interval, we enumerated all possible 1-year and 2-year time intervals between 2010-present. For each time interval, we iterated through all NYC neighborhoods, checking if we have observed a gentrification instance for this neighborhood during this time interval. If not, we classify this as an instance of non-gentrification and compute the changes in Foursquare user-generated data during and before this interval.
* compute_fsq_interaction_changes.py

* write_foursquare_changes_to_csv.py
/changes_results
fsq_gent_before_oneyear.csv
fsq_nongent_before_oneyear.csv
fsq_gent_during_oneyear.csv
fsq_nongent_during_oneyear.csv   
fsq_gent_before_twoyears.csv        
fsq_nongent_before_twoyears.csv
fsq_gent_during_twoyears.csv        
fsq_nongent_during_twoyears.csv

We used d3.js to plot the changes to compare how they differ between intervals of gentrification vs non-gentrification.
See results in /changes_results/plots


Streaming Tweet Distributions
------------------------------
We asked Matthew Huie, Foursquare Technical Account Manager, for access to the Foursquare firehose. He suggested using Twitter instead so we wrote and ran a daemon that saves the distribution of Tweets over neighborhoods every hour. We didn't have time to analyze the data.
* tweets_by_neighborhood.py
* tweet_distrib_api.py
* query_tweet_dist_api_response.py
* save_tweet_dist_api_response.py