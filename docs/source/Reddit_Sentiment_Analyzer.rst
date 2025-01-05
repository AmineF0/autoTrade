======================
Reddit Sentiment Analyzer
======================

Overview
--------
The Reddit Sentiment Analyzer is a social media analysis system that extracts, analyzes, 
and visualizes sentiment expressed in Reddit posts and comments. It uses Python with VADER 
for sentiment analysis and matplotlib/seaborn for visualizations.

Architecture
-----------

The system consists of three main classes:

RedditParser
~~~~~~~~~~~
.. code-block:: python

   class RedditParser:
       def __init__(self, text: str):
           self.text = text
           self.posts = []

**Responsibilities**:

* Reddit data extraction and structuring  
* Comment hierarchy organization
* Text cleaning
* JSON format saving

SentimentAnalyzer 
~~~~~~~~~~~~~~~
.. code-block:: python

   def analyze_text(text, analyzer):
       scores = analyzer.polarity_scores(text)
       sentiment = get_sentiment_label(scores['compound'])
       return {
           'sentiment': sentiment,
           'scores': scores
       }

**Features**:

* VADER sentiment analysis
* Composite score calculation  
* Sentiment categorization

SentimentVisualizer
~~~~~~~~~~~~~~~~~
.. code-block:: python

   class SentimentVisualizer:
       def __init__(self, csv_path):
           self.df = pd.read_csv(csv_path)

**Generates**:

* Sentiment distributions
* Compound score plots
* Subreddit analysis
* Comment visualizations

Usage Example
------------

Input Data
~~~~~~~~~
.. code-block:: json

   {
     "posts": [
       {
         "subreddit": "NVDA_Stock",
         "title": "NVIDIA GeForce RTX 5080 reportedly launches January 21st",
         "sentiment": "positive", 
         "sentiment_scores": {
           "compound": 0.296
         }
       }
     ]
   }

Results
~~~~~~~
.. code-block:: json

   {
     "total_posts": 5,
     "sentiment_distribution": {
       "positive": 3,
       "neutral": 1,
       "negative": 1
     },
     "average_compound_score": 0.3701
   }

Generated Visualizations
~~~~~~~~~~~~~~~~~~~~~
.. image:: path_to_sentiment_distribution.png
  :alt: Sentiment Distribution
  :align: center

* Post Sentiment Distribution (left)
* Comment Sentiment Distribution (right)

Installation & Dependencies
-------------------------

.. code-block:: python

   requirements = [
       'pandas',
       'numpy', 
       'matplotlib',
       'seaborn',
       'vaderSentiment'
   ]

Usage
-----

.. code-block:: python

   # Initialization
   parser = RedditParser(text)
   analyzer = SentimentAnalyzer()
   visualizer = SentimentVisualizer('data.csv')

   # Analysis
   parser.process_and_save('output.json')
   visualizer.create_all_visualizations()

Best Practices
------------

* Clear function documentation
* Error handling
* Unit testing
* Code modularity 
* Standardized output formats

Limitations & Improvements
------------------------

Current Limitations
~~~~~~~~~~~~~~~~
* Limited to textual data
* No real-time analysis

Possible Improvements
~~~~~~~~~~~~~~~~~~
* Multimodal analysis
* Sarcasm detection
* Temporal analysis
* Multi-platform support

Indices and Tables
----------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
