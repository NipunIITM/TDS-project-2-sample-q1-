import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Set non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import json
import base64
from io import BytesIO
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# Configure requests with retries
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
session.mount('http://', HTTPAdapter(max_retries=retries))
session.mount('https://', HTTPAdapter(max_retries=retries))

def fetch_and_parse_data():
    try:
        print("Fetching data from Wikipedia...")
        url = "https://en.wikipedia.org/wiki/List_of_highest-grossing_films"
        response = requests.get(url)
        response.raise_for_status()
        
        print("Parsing HTML...")
        soup = BeautifulSoup(response.text, 'lxml')
        table = soup.find('table', class_='wikitable sortable')
        
        if not table:
            print("Error: Could not find the table in Wikipedia page")
            return None
            
        print("Converting to DataFrame...")
        df = pd.read_html(str(table))[0]
        
        print("Cleaning data...")
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Clean numeric columns
        df["Worldwide gross"] = pd.to_numeric(
            df["Worldwide gross"].str.replace(r'[^0-9.]', '', regex=True),
            errors='coerce'
        )
        
        df["Year"] = pd.to_numeric(df["Year"], errors='coerce')
        df["Rank"] = pd.to_numeric(df["Rank"], errors='coerce')
        df["Peak"] = pd.to_numeric(df["Peak"], errors='coerce')
        
        print(f"Data shape: {df.shape}")
        print("Sample of cleaned data:")
        print(df.head())
        
        return df
        
    except Exception as e:
        print(f"Error in fetch_and_parse_data: {str(e)}")
        return None

def analyze_data(df):
    try:
        if df is None:
            print("Error: DataFrame is None")
            return json.dumps(["Error", "Error", "Error", ""])
            
        print("\nAnalyzing data...")
        
        # Question 1: $2B before 2000
        mask = (df["Worldwide gross"] >= 2_000_000_000) & (df["Year"] < 2000)
        q1 = int(np.sum(mask))
        print(f"Q1 result: {q1} movies over $2B before 2000")
        
        # Question 2: Earliest film over $1.5B
        mask = df["Worldwide gross"] >= 1_500_000_000
        filtered_df = df[mask].sort_values("Year")
        if len(filtered_df) > 0:
            q2 = filtered_df.iloc[0]["Title"]
        else:
            q2 = "No films found"
        print(f"Q2 result: Earliest film over $1.5B: {q2}")
        
        # Question 3: Correlation Rank vs Peak
        q3 = round(df["Rank"].corr(df["Peak"]), 3)
        print(f"Q3 result: Correlation = {q3}")
        
        # Question 4: Visualization
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x="Rank", y="Peak")
        sns.regplot(data=df, x="Rank", y="Peak", scatter=False, color='red', line_kws={'linestyle': ':'})
        plt.title("Rank vs Peak")
        
        # Save plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        print("Analysis complete!")
        return json.dumps([str(q1), str(q2), str(q3), f"data:image/png;base64,{image_base64}"])
        
    except Exception as e:
        print(f"Error in analyze_data: {str(e)}")
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
