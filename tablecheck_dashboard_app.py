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

Browse data from Tablecheck.
'''
# How many customers visited the "Restaurant at the end of the universe"?
rest_a_end_ot_uni_df = raw_tablecheck_df[raw_tablecheck_df["restaurant_names"] == "the-restaurant-at-the-end-of-the-universe"]

# I'm assuming that nothing else is implied: the take home is narrowing asking about "Restaurant at the end of the universe"
# and no more flexibility is needed to lookup the same information for other restuarants in the following two solutions.
# I'm also assuming the currency is in Japanese Yen.
st.metric("The Restaurant at the End of the Univerise customer traffic", f"{'{:,}'.format(rest_a_end_ot_uni_df['restaurant_names'].count())}", border=True)

# How much money did the "Restaurant at the end of the universe" make?
st.metric("The Restaurant at the End of the Univerise total earnings", f"¥{'{:,}'.format(rest_a_end_ot_uni_df['food_cost'].sum())}", border=True)

# What was the most popular dish at each restaurant?
food_counts_df = raw_tablecheck_df.groupby(['restaurant_names', 'food_names']).size().reset_index(name='order_count')
most_popular_dishes_df = food_counts_df.loc[food_counts_df.groupby('restaurant_names')['order_count'].idxmax()]

st.write("Most popular dish at each restaurant:")
st.dataframe(
    most_popular_dishes_df.sort_values("restaurant_names").reset_index(drop=True),
    use_container_width=True
)
