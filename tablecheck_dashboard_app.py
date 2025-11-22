# Due to Streamlit's limitations, Pandas will be used. Normally I'd would prefer PySpark for several reasons 
# (readability, performance, scalability). But PySpark requires a JVM with JRE's for Spark.

# I would like to present a simple implemntation of a data pipeline that is organized into logical steps.
#   1. Manage the initial database connection
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
# :globe_showing_asia_australia: :japan: :jp: :cherry_blossom: Tablecheck Dashboard

Browse selected data from Tablecheck.
'''

st.header("Initial test")