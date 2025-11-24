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
from pathlib import Path


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
    data_filename = Path(__file__).parent/'data/data.csv'

    raw_tablecheck_df = pd.read_csv(data_filename)

    return raw_tablecheck_df

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
6. Is there any customer who visited any individual restaurant more than Michael? I'm curious
'''

# This DataFrame is already calculated in 5a, but we'll reference it here.
# It contains the visit count for each customer at each restaurant.
michaels_visits_df = customer_restarant_counts_df[customer_restarant_counts_df["first_name"] == "michael"]
michaels_max_visits = michaels_visits_df["order_count"].max() if not michaels_visits_df.empty else 0

# Find the customer(s) with the absolute most visits to a single restaurant
top_single_visit_df = customer_restarant_counts_df.loc[[customer_restarant_counts_df['order_count'].idxmax()]]
top_visitor_name = top_single_visit_df['first_name'].iloc[0]
top_visit_count = top_single_visit_df['order_count'].iloc[0]

if top_visitor_name == "michael":
    st.write("No, Michael is the customer with the most visits to a single restaurant.")
else:
    st.write(f"Yes. While Michael's highest visit count to a single restaurant is **{michaels_max_visits}**, "
             f"the customer **{top_visitor_name.title()}** visited one restaurant **{top_visit_count}** times.")
    st.dataframe(top_single_visit_df.reset_index(drop=True), width="stretch")
    