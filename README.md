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
