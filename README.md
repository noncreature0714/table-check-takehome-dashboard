# Tablecheck Restaurant Data Dashboard

A Streamlit dashboard that connects to a Supabase database to analyze and answer questions about restaurant customer data for the Tablecheck take-home challenge.

[View the project on GitHub](https://github.com/noncreature0714/table-check-takehome-dashboard)

### How to run it on your own machine

1.  **Set up Environment Variables**

    Add your Supabase credentials on the Supabase dashboard.

2.  **Install the requirements**

   ```
   $ pip install -r requirements.txt
   ```

3.  **Run the app**

   ```
   $ streamlit run tablecheck_dashboard_app.py
   ```

------------------------

## Final Summary of Answers

This summary outlines the final answers to the questions posed in the take-home challenge,
derived from the data hosted in and queried from a Supabase database.

1. How many customers visited the "Restaurant at the end of the universe"?
   - The script calculates the total number of entries (visits) for this specific restaurant.

2. How much money did the "Restaurant at the end of the universe" make?
   - The script calculates the sum of the `food_cost` column for all visits to this restaurant.

3. What was the most popular dish at each restaurant?
   - A table is generated showing the dish with the highest order count for each restaurant.

4. What was the most profitable dish at each restaurant?
   - Acknowledging that true profit cannot be calculated, the script identifies the dish with the
     highest total `food_cost` sum for each restaurant as a proxy for profitability.

5a. Who visited each store the most?
   - A table is generated showing the single customer with the highest number of visits for each
     individual restaurant.

5b. Who has the highest cumulative sum of restaurant visits?
   - The script identifies the customer(s) with the highest total number of visits across all
     restaurants combined.


## Additional questions from the challenge

### How would you build this differently if the data was being streamed from Kafka?

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

### How would you improve the deployment of this system? 

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
    
Importantly, I'd also have a local docker container (or similar) where I can inspect the results before pushing to the site.