import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend before importing pyplot
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
import json
import numpy as np
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure requests with retries and timeouts
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def fetch_and_parse_data():
    try:
        # Step 1: Fetch the Wikipedia page
        url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
        response = session.get(url, timeout=10)
        response.raise_for_status()
        
        # Step 2: Find the correct table
        soup = BeautifulSoup(response.content, "html.parser")
        tables = soup.find_all("table", class_="wikitable")
        target_table = next((table for table in tables if "Highest-grossing films" in table.get_text()), None)
        
        if target_table is None:
            raise ValueError("Target table not found")
        
        # Step 3: Parse table more efficiently
        df = pd.read_html(str(target_table))[0]
        return clean_data(df)
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def clean_data(df):
    # Step 4: Clean and prepare data more efficiently
    df.columns = df.columns.str.replace(r"\[.*?\]", "", regex=True).str.strip()
    
    # Clean numeric columns in one go
    df["Worldwide gross"] = pd.to_numeric(
        df["Worldwide gross"].str.replace(r'[^\d.]', '', regex=True),  # Better regex for number extraction
        errors='coerce'
    )
    
    numeric_columns = ["Year", "Rank", "Peak"]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    
    # Drop rows with NaN values in critical columns
    df = df.dropna(subset=["Worldwide gross", "Year"])
    
    return df

def analyze_data(df):
    if df is None:
        print("Error: DataFrame is None")
        return json.dumps(["Error", "Error", "Error", ""])
    
    try:
        print("Starting data analysis...")
        print("\nShape of DataFrame:", df.shape)
        
        # Question 1: $2B before 2000 - using numpy for efficiency
        mask = (df["Worldwide gross"] >= 2_000_000_000) & (df["Year"] < 2000)
        q1 = int(np.sum(mask))  # Convert to int for better JSON serialization
        print(f"Q1 completed: {q1} films made $2B+ before 2000")

        # Question 2: Earliest film over $1.5B
        mask = df["Worldwide gross"] >= 1_500_000_000
        filtered_df = df[mask].sort_values("Year")
        if len(filtered_df) > 0:
            q2 = filtered_df.iloc[0]["Title"]
            print(f"Q2 completed: Earliest $1.5B+ film is {q2}")
        else:
            q2 = "No films found over $1.5B"
            print(f"Q2 completed: {q2}")

        # Question 3: Correlation Rank vs Peak
        df_clean = df.dropna(subset=["Rank", "Peak"])
        if len(df_clean) > 1:  # Need at least 2 points for correlation
            q3 = round(df_clean["Rank"].corr(df_clean["Peak"]), 3)
            print(f"Q3 completed: Correlation is {q3}")
        else:
            q3 = "Insufficient data for correlation"
            print(f"Q3 completed: {q3}")

        # Question 4: Scatterplot + regression
        print("Creating visualization...")
        if len(df_clean) > 1:
            plt.figure(figsize=(8, 6), dpi=100)
            sns.set_style("whitegrid")
            sns.regplot(
                x="Rank", 
                y="Peak", 
                data=df_clean,
                scatter_kws={'s': 50, 'alpha': 0.6},
                line_kws={'color': 'red', 'linestyle': 'dotted', 'linewidth': 2}
            )
            plt.title("Rank vs Peak", fontsize=12, pad=15)
            plt.xlabel("Rank", fontsize=10)
            plt.ylabel("Peak", fontsize=10)
            plt.tight_layout()

            # Save as base64 with compression
            buffer = BytesIO()
            plt.savefig(buffer, format="png", bbox_inches='tight', dpi=100)
            plt.close()
            buffer.seek(0)
            img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
            data_uri = f"data:image/png;base64,{img_base64}"
            print("Visualization completed")
        else:
            data_uri = ""
            print("Insufficient data for visualization")

        return json.dumps([str(q1), q2, str(q3), data_uri])
    
    except Exception as e:
        print(f"Error analyzing data: {str(e)}")
        import traceback
        traceback.print_exc()
        return json.dumps(["Error", "Error", "Error", ""])

if __name__ == "__main__":
    df = fetch_and_parse_data()
    if df is not None:
        print("\nDataFrame head:")
        print(df.head())
        print("\nDataFrame info:")
        print(df.info())
    result = analyze_data(df)
    # Save the result to a JSON file
    with open('output.json', 'w') as f:
        f.write(result)
    print("\nResults have been saved to output.json")
