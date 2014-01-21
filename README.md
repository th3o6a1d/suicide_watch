Suicide Watch
===========

Twitter mining for suicide prevention, gun violence, influenza, and other public health threats. Wordlist obtained from Argyle et al. "Tracking Suicide Risk Factors
Through Twitter in the US." Crisis 2014; Vol. 35(1):51–59. 

Opens twitter public stream.  Identifies concerning tweets in a geographical location, such as a school district.  Once it flags a tweet, will scan that user's past tweets, tally up instances of the word, record the number of followers, reverse geocode the user's address using the Google Maps API, dump the output into a sqlite3 db and .txt file, then send a text message to a user.  

Uses TwitterAPI for Python (thanks geduldig).  To install, pip install TwitterAPI.  

http://www.twitter.com/th3o6a1d
