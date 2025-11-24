# Due to Streamlit's limitations, Pandas will be used. Normally I'd would prefer PySpark for several reasons 
# (readability, performance, scalability). But PySpark requires a JVM with JRE's for Spark.

# I would like to present a simple implemntation of a data pipeline that is organized into logical steps.
#   1. Manage the initial database connection to the desired table(s)
#   2. Extract selected table-level data (only have one "table" here)
#   3. Transform the data, which includes
#       a. filtering & reducing
#       b. cleaning columns such that the types are consistent, are exploded or joined, and 
#          organizational data operations for following steps
#       c. aggregating the data
#       d. performing a final clean and select on the data to reduce the size and improve the ease of use
#   4. Loading the data into the final dashboard
#   5. If needed, tuning the dashboard for tasks which only the dashboard can do.
#
# A special note that PySpark is lazily implemented, so writing maintainable code is a little easier do to 
# without having to (persistently) worry about if a particular filter or aggregation should happen first or last,
# or somewhere else, because the (inspectable) Spark optimizer handles that.
# 
# Additionally, with an integrated platform like Streamlit, the discrete steps above are often inmplemented at 
# render, so the separation of concerns can be a little less obvious than I'd like.

import streamlit as st
import pandas as pd
import os
from pathlib import Path
from supabase import create_client, Client

DB_URL: str = os.environ.get("SUPABASE_URL")
DB_KEY: str = os.environ.get("SUPABASE_KEY")

@st.cache_data
def get_supabase_data():
    """
    Connect to supabase and return table data.
    """
    db_client: Client = create_client(DB_URL, DB_KEY)

    return (
        db_client.table("tablecheck_takehome_data")
        .select("*")
        .execute()
    )

st.set_page_config(
    page_title = "Tablecheck Dashboard",
    page_icon = ":globe_showing_asia_australia:"
)

@st.cache_data
def get_tablecheck_data():
    """Grab data from a CSV file.

    This uses caching to avoid having to read the file every time. If we were
    reading from an HTTP endpoint instead of a file, it's a good idea to set
    a maximum age to the cache with the TTL argument: @st.cache_data(ttl='1d')
    """

    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    # data_filename = Path(__file__).parent/'data/data.csv'

    # raw_tablecheck_df = pd.read_csv(data_filename)

    df = pd.DataFrame(get_supabase_data().data)

    return df

raw_tablecheck_df = get_tablecheck_data()

'''
# :cherry_blossom: Tablecheck Dashboard :cherry_blossom:

Browse results from the Tablecheck take home challenge.
'''

''
''

'''
1. How many customers visited the "Restaurant at the end of the universe"?
'''
rest_a_end_ot_uni_df = raw_tablecheck_df[raw_tablecheck_df["restaurant_names"] == "the-restaurant-at-the-end-of-the-universe"]

# I'm assuming that nothing else is implied: the take home is narrowing asking about "Restaurant at the end of the universe"
# and no more flexibility is needed to lookup the same information for other restuarants in the following two solutions.
# I'm also assuming the currency is in Japanese Yen.
st.metric("The Restaurant at the End of the Univerise customer traffic", f"{'{:,}'.format(rest_a_end_ot_uni_df['restaurant_names'].count())}", border=True)

''
''

'''
2. How much money did the "Restaurant at the end of the universe" make?
'''
st.metric("The Restaurant at the End of the Univerise total earnings", f"¥{'{:,}'.format(int(rest_a_end_ot_uni_df['food_cost'].sum()))}", border=True)

''
''

'''
3. What was the most popular dish at each restaurant?
'''
# Filter & aggregate
food_counts_df = (
    raw_tablecheck_df
    .groupby(['restaurant_names', 'food_names'])
    .size()
    .reset_index(name='order_count')
)
most_popular_dishes_df = (
    food_counts_df
    .loc[
        food_counts_df
        .groupby('restaurant_names')['order_count']
        .idxmax()
    ]
)

# present
st.write("Most popular dish at each restaurant:")
st.dataframe(
    (
        most_popular_dishes_df
        .sort_values("restaurant_names")
        .reset_index(drop=True)
    ),
    width="stretch"
)

''
''

'''
4. What was the most profitable dish at each restaurant?

The data to determinate the most *profitable* dish at each restarurant is missing because we need the net revenue of 
each dish (price - cost), not just cost of the dish.

I'm going to assume there's a possibly of language issue, that the "food_cost" column could mean either the cost to the
restuarant OR the price of the dish.

There is also the possibility the profit is pre-calculated, but I have no way of knowing at this time.

I can provide which food had the highest sum "cost" per provided data. 

However, I will still label the data on the dashboard as "most profitlable".
'''
food_sums_df = (
    raw_tablecheck_df
    .groupby(["restaurant_names", "food_names"])
    .agg(food_cost_sum=('food_cost', 'sum'))
    .reset_index()
)
most_profitable_dishes_df = (
    food_sums_df
    .loc[
        food_sums_df
        .groupby("restaurant_names")["food_cost_sum"]
        .idxmax()
    ]
)

''
''

st.write("Most 'profitable' dish at each restaurant:")
st.dataframe(
    (
        most_profitable_dishes_df
        .sort_values("restaurant_names")
        .reset_index(drop=True)
    ),
    width="stretch"
)

''
''

'''
5a. Who visited each store the most?
'''
customer_restarant_counts_df = (
    raw_tablecheck_df
    .groupby(["first_name", "restaurant_names"])
    .size()
    .reset_index(name='order_count')
)
customer_restarant_max_count_df = (
    customer_restarant_counts_df.loc[
        customer_restarant_counts_df.groupby("restaurant_names")["order_count"].idxmax()
    ]
)

st.write("Who visited each store the most?")
st.dataframe(
    (
        customer_restarant_max_count_df
        .sort_values("restaurant_names")
        .reset_index(drop=True)
    ),
    width="stretch"
)

''
''

'''
5b. Who has the highest cumulative sum of restuarant visits?
'''
total_visits_df = (
    raw_tablecheck_df
    .groupby("first_name")
    .size()
    .reset_index(name="total_visits")
)

customer_with_most_visits_df = total_visits_df[
    total_visits_df["total_visits"] == total_visits_df["total_visits"].max()
]

st.write("Customer with the most visits (all stores):")
st.dataframe(
    customer_with_most_visits_df.reset_index(drop=True),
    width="stretch"
)

''
''

''' 
How would you build this differently if the data was being streamed from Kafka?

I'm answering this assuming I can imagine whatever I wish given this new context, to wit:

    1. A production environment, with clear separation between streams, data lake / sink, ETL pipelines, data warehouse, 
       and dashboards/reporting
    2. Separately and centrally managed configuration for each major project and/or devision (whichever makes sense)
    3. Storage policies and other governance 
    4. Use of PySpark, which is highly effecient and has a Kafka Connector

Firstly, a stream reader which pulls from the Kafka stream for specified topics into a an hourly partitioned 
data lake with an approxiamate 30 day retention policy. 

Next, depending on the cadence, either hourly or daily (daily recommended), run one or several ETLs which aggregate and send
data to a warehouse or "lake house," ready for consumption by dashboards or other teams within the company.


'''

''
''

''' 
How would you improve the deployment of this system? 

Assuming this is narrowly related to my current implementation using Streamlit and _ database, and not some imaginary 
system, I would:

    1. Make the code more testable and maintainable by extracting the logic into functions or objects
        a. debatably the initial database connection could be managed with a context manager or a class
            i. really depends on the size of the project and how much it needs future proofed without being
               overly paranoid or wasting too much time (not that either would be a big time issue)
        b. most of the logic here is organized by question, this was a tradeoff I made because it would 
           be better to organize this into steps that iterate on the dataframe for groupings and aggregations
           for each question, however, this was the tradeoof for using streamlit as well, and not some backend 
           pipeline where the aggregate logic can be separated more discretely from the display logic
    2. Add unit testing to each extract and transform 
    3. Update pre-commit hooks to run tests and check for "success" before pushing
    4. Upon succeful completion of the work, have a deployment (probably a mix of manual and some self-automation)
       that tags the job in git, and pushes to the main branch upon a success pull/merge request. 
    
Importantly, I'd also have a local docker container (or similar) where I can inspect the results before pushing to the site
on my local 


'''