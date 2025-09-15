import pandas as pd
import numpy as np
import requests
import os
from itertools import combinations
import collections

def data_loading():
    url = 'https://archive.ics.uci.edu/ml/machine-learning-databases/00502/online_retail_II.xlsx'
    raw_data_path = '../data/01_raw/online_retail_II.xlsx'

    # Create directory and download if needed
    os.makedirs(os.path.dirname(raw_data_path), exist_ok=True)

    if not os.path.exists(raw_data_path):
        print('Downloading dataset...')
        response = requests.get(url)
        response.raise_for_status()
        with open(raw_data_path, 'wb') as f:
            f.write(response.content)
        print('Download complete.')
    else:
        print('Dataset already exists.')
        
        
    # Load data from both sheets
    print('Loading data...')
    xls = pd.ExcelFile(raw_data_path)
    df_year_1 = pd.read_excel(xls, 'Year 2009-2010')
    df_year_2 = pd.read_excel(xls, 'Year 2010-2011')

    # Combine datasets
    df = pd.concat([df_year_1, df_year_2], ignore_index=True)
    print(f'Total data shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')
    df.head()
    

def data_processing():
    # Basic cleaning
    print('Original shape:', df.shape)

    # Remove rows with missing CustomerID
    df = df.dropna(subset=['Customer ID'])
    print('After removing null CustomerID:', df.shape)

    # Remove returns (invoices starting with 'C')
    df = df[~df['Invoice'].astype(str).str.startswith('C')]
    print('After removing returns:', df.shape)

    # Keep only positive quantities
    df = df[df['Quantity'] > 0]
    print('After removing negative quantities:', df.shape)

    # Clean descriptions
    df['Description'] = df['Description'].str.strip()
    df = df.dropna(subset=['Description'])
    print('After cleaning descriptions:', df.shape)
    
    # ULTRA-CONSERVATIVE SAMPLING for guaranteed success
    print('\n=== SMART SAMPLING FOR MEMORY EFFICIENCY ===')

    # Step 1: Take only top 50 most popular products
    product_counts = df['Description'].value_counts()
    top_products = product_counts.head(50).index.tolist()

    print(f'Top 50 products:')
    for i, (product, count) in enumerate(product_counts.head(50).items(), 1):
        print(f'{i:2d}. {product[:50]:<50} ({count:,} times)')

    # Filter to only these products
    df_sample = df[df['Description'].isin(top_products)].copy()
    print(f'\nData with top 50 products: {df_sample.shape}')

    # Step 2: Sample 10000 random invoices
    unique_invoices = df_sample['Invoice'].unique()
    sample_invoices = np.random.choice(unique_invoices, size=min(10000, len(unique_invoices)), replace=False)
    df_final = df_sample[df_sample['Invoice'].isin(sample_invoices)].copy()

    print(f'\nFinal sample: {df_final.shape}')
    print(f'Unique invoices: {df_final["Invoice"].nunique()}')
    print(f'Unique products: {df_final["Description"].nunique()}')
    
    
def market_basket_analysis():
    # Simple co-occurrence analysis (no memory issues)
    print('\n=== MARKET BASKET ANALYSIS ===')

    # Group products by invoice
    invoice_products = df_final.groupby('Invoice')['Description'].apply(list).reset_index()
    print(f'Analyzing {len(invoice_products)} invoices...')

    # Count co-occurrences
    pair_counts = collections.Counter()
    product_counts = collections.Counter()
    total_baskets = 0

    for products in invoice_products['Description']:
        if len(products) >= 2:  # Only multi-item baskets
            total_baskets += 1
            
            # Count individual products
            for product in products:
                product_counts[product] += 1
            
            # Count pairs
            for pair in combinations(sorted(products), 2):
                pair_counts[pair] += 1

    print(f'Multi-item baskets: {total_baskets}')
    print(f'Unique product pairs: {len(pair_counts)}')
    
    # Calculate association metrics
    associations = []

    for (product_a, product_b), pair_count in pair_counts.items():
        # Support: P(A and B)
        support = pair_count / total_baskets
        
        # Confidence: P(B|A) and P(A|B)
        confidence_a_to_b = pair_count / product_counts[product_a]
        confidence_b_to_a = pair_count / product_counts[product_b]
        
        # Lift: Support / (P(A) * P(B))
        prob_a = product_counts[product_a] / total_baskets
        prob_b = product_counts[product_b] / total_baskets
        lift = support / (prob_a * prob_b)
        
        associations.append({
            'Product_A': product_a,
            'Product_B': product_b,
            'Count': pair_count,
            'Support': support,
            'Confidence_A→B': confidence_a_to_b,
            'Confidence_B→A': confidence_b_to_a,
            'Lift': lift
        })

    # Create results DataFrame
    results_df = pd.DataFrame(associations)
    results_df = results_df.sort_values(['Lift', 'Support'], ascending=[False, False])

    print(f'\nTotal associations found: {len(results_df)}')
    print('\nTop 15 Product Associations:')
    display(results_df.head(15).round(3))
    
    
def business_insgihts():
    # Filter for strong associations
    strong_associations = results_df[
        (results_df['Support'] >= 0.01) &  # At least 1% support
        (results_df['Lift'] >= 1.5)        # At least 50% lift
    ]

    print('\n' + '='*60)
    print('BUSINESS INSIGHTS')
    print('='*60)

    if len(strong_associations) > 0:
        print(f'\n🎯 STRONG ASSOCIATIONS FOUND: {len(strong_associations)}')
        print('\nTop recommendations for cross-selling:')
        
        for i, row in strong_associations.head(10).iterrows():
            print(f'\n{len(strong_associations.head(10)) - len(strong_associations.head(10)[strong_associations.head(10).index <= i]) + 1}. "{row["Product_A"]}" + "{row["Product_B"]}"')
            print(f'   • Lift: {row["Lift"]:.2f}x more likely to be bought together')
            print(f'   • Confidence: {max(row["Confidence_A→B"], row["Confidence_B→A"]):.1%} of customers who buy one also buy the other')
            print(f'   • Support: {row["Support"]:.1%} of all transactions contain both items')
        
        print(f'\n📊 SUMMARY STATISTICS:')
        print(f'• Average lift for strong associations: {strong_associations["Lift"].mean():.2f}')
        print(f'• Highest lift found: {strong_associations["Lift"].max():.2f}')
        print(f'• Most frequent pair appears in {strong_associations["Support"].max():.1%} of transactions')
        
    else:
        print('\n⚠️  No strong associations found with current thresholds.')
        print('\nTop 5 associations by lift (regardless of thresholds):')
        
        for i, row in results_df.head(5).iterrows():
            print(f'\n{i+1}. "{row["Product_A"]}" + "{row["Product_B"]}"')
            print(f'   • Lift: {row["Lift"]:.2f}')
            print(f'   • Support: {row["Support"]:.1%}')

    print(f'\n💡 RECOMMENDATIONS:')
    print('• Use these associations for product placement and bundling')
    print('• Consider promotional campaigns for high-lift pairs')
    print('• Monitor inventory levels for associated products')
    print('• Implement "customers who bought X also bought Y" recommendations')
    
    
def main():
    data_loading()
    data_processing()
    market_basket_analysis()
    business_insgihts()
    

if '__name__' == '__main__':
    main()
    
