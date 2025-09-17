import pickle
import pandas as pd
from fastapi import FastAPI, HTTPException

# --- 1. Initialize the FastAPI app ---
app = FastAPI(
    title="E-commerce Recommendation API",
    description="An API that provides product recommendations based on Association Rules.",
    version="1.0.0"
)


# --- 2. Load the trained model (association rules) ---
# This is done once when the application starts.
try:
    with open('models/association_rules.pkl', 'rb') as f:
        rules = pickle.load(f)
except FileNotFoundError:
    raise RuntimeError("Model file not found. Please run the training notebook first.")


def get_recommendations(product, results_df, top_n=5, min_lift=1.0):
    """
    Given a product name, return top N recommended products based on association rules.
    
    Args:
        product (str): Product name to get recommendations for.
        results_df (pd.DataFrame): DataFrame with association rules.
        top_n (int): Number of recommendations to return.
        min_lift (float): Minimum lift threshold for recommendations.
        
    Returns:
        pd.DataFrame: Top N recommended products with metrics.
    """
    # Find associations where the product is either Product_A or Product_B
    mask_a = (results_df['Product_A'] == product) & (results_df['Lift'] >= min_lift)
    mask_b = (results_df['Product_B'] == product) & (results_df['Lift'] >= min_lift)
    
    recs_a = results_df[mask_a].copy()
    recs_a['Recommended_Product'] = recs_a['Product_B']
    recs_a['Direction'] = 'A→B'
    recs_a['Confidence'] = recs_a['Confidence_A→B']
    
    recs_b = results_df[mask_b].copy()
    recs_b['Recommended_Product'] = recs_b['Product_A']
    recs_b['Direction'] = 'B→A'
    recs_b['Confidence'] = recs_b['Confidence_B→A']
    
    recs = pd.concat([recs_a, recs_b], ignore_index=True)
    recs = recs.sort_values(['Lift', 'Confidence', 'Support'], ascending=[False, False, False])
    
    # Select columns to display
    cols = ['Recommended_Product', 'Support', 'Confidence', 'Lift', 'Count', 'Direction']
    return recs[cols].head(top_n).reset_index(drop=True)


# --- 4. Define API Endpoints ---
@app.get("/")
def read_root():
    """A welcome message for the API root."""
    return {"message": "Welcome to the E-commerce Recommendation API!"}


@app.get("/recommend/{product_name}")
def recommend_products(product_name: str):
    """
    Provides top 5 product recommendations for a given product name.
    """
    if not product_name:
        raise HTTPException(status_code=400, detail="Product name cannot be empty.")
        
    recommendations = get_recommendations(product_name, rules)
    
    if not recommendations:
        raise HTTPException(
            status_code=404, 
            detail=f"No recommendations found for product: '{product_name}'"
        )
        
    return {
        "product": product_name,
        "recommendations": recommendations
    }