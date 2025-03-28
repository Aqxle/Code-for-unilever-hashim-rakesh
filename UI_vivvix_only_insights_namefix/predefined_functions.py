def main1(df):

    # Filter for Procter & Gamble brands
    df_filtered = df[df['PARENT']==company_name]

    # Select relevant columns
    spend_cols = ["Jul 2024  $", "Aug 2024  $", "Sept 2024  $"]
    
    # Group by brand and sum ad spend
    df_grouped = df_filtered.groupby("BRAND")[spend_cols].sum()

    # Calculate the percentage of total spend for September by each brand
    total_spend_sept = df_grouped["Sept 2024  $"].sum()
    df_grouped["% of Total Spend (Sept)"] = (df_grouped["Sept 2024  $"] / total_spend_sept) * 100

    # Calculate percentage changes
    df_grouped["% Change (Aug vs Jul)"] = ((df_grouped["Aug 2024  $"] - df_grouped["Jul 2024  $"]) / df_grouped["Jul 2024  $"]) * 100
    df_grouped["% Change (Sept vs Aug)"] = ((df_grouped["Sept 2024  $"] - df_grouped["Aug 2024  $"]) / df_grouped["Aug 2024  $"]) * 100
    
    # Sort by the latest month's spend in descending order
    df_grouped = df_grouped.sort_values(by="Sept 2024  $", ascending=False)
    
    # Reset index for better readability
    df_result = df_grouped.reset_index()
    
    # Create a total row
    total_row = pd.DataFrame([{
        'BRAND': 'Total',
        'Jul 2024  $': df_result['Jul 2024  $'].sum(),
        'Aug 2024  $': df_result['Aug 2024  $'].sum(),
        'Sept 2024  $': df_result['Sept 2024  $'].sum(),
        '% of Total Spend (Sept)': 100.0,  # This will always be 100%
        '% Change (Aug vs Jul)': ((df_result['Aug 2024  $'].sum() - df_result['Jul 2024  $'].sum()) / df_result['Jul 2024  $'].sum()) * 100,
        '% Change (Sept vs Aug)': ((df_result['Sept 2024  $'].sum() - df_result['Aug 2024  $'].sum()) / df_result['Aug 2024  $'].sum()) * 100
    }])
    
    # Append the total row to the result dataframe
    df_final = pd.concat([df_result, total_row], ignore_index=True)
    
    # Format currency columns with $ symbol and convert to millions
    for col in ['Jul 2024  $', 'Aug 2024  $', 'Sept 2024  $']:
        new_col = col.replace('$', '$M')
        df_final[new_col] = df_final[col].apply(lambda x: f"${x/1000000:.2f}")
        df_final.drop(col, axis=1, inplace=True)
    
    # Format percentage columns with % symbol
    for col in ['% of Total Spend (Sept)', '% Change (Aug vs Jul)', '% Change (Sept vs Aug)']:
        df_final[col] = df_final[col].apply(lambda x: f"{x:.2f}%")

        # Define new column order
    new_column_order = [
        'BRAND', 'Jul 2024  $M', 'Aug 2024  $M', 'Sept 2024  $M',
        '% of Total Spend (Sept)', '% Change (Aug vs Jul)', '% Change (Sept vs Aug)'
    ]

    # Reorder DataFrame
    df_final = df_final[new_column_order]
    df_final = df_final.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
        
    return df_final, f'1. Recent Ad Spend of {company_name} brands across all platforms'


def main2(df):
    # Filter data for Procter & Gamble Co
    pg_df = df[df['PARENT']==company_name]
    
    # Aggregate total ad spend per brand
    brand_spend = pg_df.groupby('BRAND', as_index=False)['TOTAL $'].sum()
    
    # Filter for brands that spent more than $0.5M
    high_spenders = brand_spend[brand_spend['TOTAL $'] > 500000]
    
    # Sort in descending order
    result = high_spenders.sort_values(by='TOTAL $', ascending=False)
    
    # Format currency column with $ symbol and convert to millions
    result['TOTAL $M'] = result['TOTAL $'].apply(lambda x: f"${x/1000000:.2f}")
    result.drop('TOTAL $', axis=1, inplace=True)

    result = result[result['TOTAL $M'] != "$0.00"]

    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)

    return result, f'2. {company_name} Brands with High Ad Spend'


def main3(df):
    # Filter data for Procter & Gamble Co
    pg_df = df[df['PARENT']==company_name]
    
    # Aggregate total ad spend per brand
    brand_spend = pg_df.groupby('BRAND', as_index=False)['TOTAL $'].sum()
    
    # Filter for brands that spent ≤ $0.5M
    low_spenders = brand_spend[brand_spend['TOTAL $'] <= 500000]
    
    # Sort in descending order
    result = low_spenders.sort_values(by='TOTAL $', ascending=True)
    
    # Format currency column with $ symbol and convert to millions
    result['TOTAL $M'] = result['TOTAL $'].apply(lambda x: f"${x/1000000:.2f}")
    result.drop('TOTAL $', axis=1, inplace=True)

    result = result[result['TOTAL $M'] != "$0.00"]

    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return result, f'2. {company_name} Brands with Low Ad Spend'


def main4(df):
    # Filter for Procter & Gamble Co
    pg_df = df[df['PARENT'] == company_name]
    
    # Calculate total spend by brand for August and September
    brand_spend = pg_df.groupby('BRAND').agg({
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    brand_spend = brand_spend.rename(columns={
        'Aug 2024  $': 'August Spend',
        'Sept 2024  $': 'September Spend'
    })
    
    # Calculate the absolute and percentage difference
    brand_spend['Spend Change'] = brand_spend['September Spend'] - brand_spend['August Spend']
    brand_spend['Spend Change %'] = (brand_spend['Spend Change'] / brand_spend['August Spend'] * 100).round(2)
    
    # Handle division by zero cases
    brand_spend['Spend Change %'] = brand_spend['Spend Change %'].fillna(0)
    # If August spend was 0 and September spend was positive, set percentage to 100%
    brand_spend.loc[(brand_spend['August Spend'] == 0) & (brand_spend['September Spend'] > 0), 'Spend Change %'] = 100
    
    # Filter for brands with positive spend change percentage
    positive_growth_brands = brand_spend[brand_spend['Spend Change %'] > 0].copy()
    
    # Sort by September spend in descending order
    sorted_brands = positive_growth_brands.sort_values('September Spend', ascending=False)
    
    # Format currency columns with $ sign and convert to millions
    for col in ['August Spend', 'September Spend', 'Spend Change']:
        new_col = col + ' ($M)'
        sorted_brands[new_col] = sorted_brands[col].apply(lambda x: f"${x/1000000:.2f}")
        sorted_brands.drop(col, axis=1, inplace=True)
    
    # Format percentage column with % sign
    sorted_brands['Spend Change %'] = sorted_brands['Spend Change %'].apply(lambda x: f"{x}%")


    # Define new column order with 'Spend Change %' at the end
    new_column_order = [
        'BRAND', 'August Spend ($M)', 'September Spend ($M)', 'Spend Change ($M)', 'Spend Change %'
    ]

    # Reorder DataFrame
    sorted_brands = sorted_brands[new_column_order]

    sorted_brands = sorted_brands.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return sorted_brands, f'3. {company_name} Brands with Ad Spend Growth'


def main5(df):
    # Filter for Procter & Gamble Co
    pg_df = df[df['PARENT'] == company_name]
    
    # Calculate total spend by brand for August and September
    brand_spend = pg_df.groupby('BRAND').agg({
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    brand_spend = brand_spend.rename(columns={
        'Aug 2024  $': 'August Spend',
        'Sept 2024  $': 'September Spend'
    })
    
    # Calculate the absolute and percentage difference
    brand_spend['Spend Change'] = brand_spend['September Spend'] - brand_spend['August Spend']
    brand_spend['Spend Change %'] = (brand_spend['Spend Change'] / brand_spend['August Spend'] * 100).round(2)
    
    # Handle division by zero cases
    brand_spend['Spend Change %'] = brand_spend['Spend Change %'].fillna(0)
    # If August spend was positive and September spend was 0, set percentage to -100%
    brand_spend.loc[(brand_spend['August Spend'] > 0) & (brand_spend['September Spend'] == 0), 'Spend Change %'] = -100
    
    # Filter for brands that showed negative growth (negative spend change percentage)
    decline_brands = brand_spend[brand_spend['Spend Change %'] < 0].copy()
    
    # Sort by September spend in decreasing order (highest spenders first)
    decline_brands = decline_brands.sort_values('September Spend', ascending=False)
    
    # Format currency columns with $ sign and convert to millions
    for col in ['August Spend', 'September Spend', 'Spend Change']:
        new_col = col + ' ($M)'
        decline_brands[new_col] = decline_brands[col].apply(lambda x: f"${x/1000000:.2f}")
        decline_brands.drop(col, axis=1, inplace=True)
    
    # Format percentage column with % sign
    decline_brands['Spend Change %'] = decline_brands['Spend Change %'].apply(lambda x: f"{x}%")

        # Define new column order with 'Spend Change %' at the end
    new_column_order = [
        'BRAND', 'August Spend ($M)', 'September Spend ($M)', 'Spend Change ($M)', 'Spend Change %'
    ]

    # Reorder DataFrame
    decline_brands = decline_brands[new_column_order]

    decline_brands = decline_brands.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return decline_brands, f'4. {company_name} Brands with Ad Spend Decline'

def main6(df):
    # Filter for Procter & Gamble Co
    pg_df = df[df['PARENT'] == company_name]
    
    # Group by media channel and calculate total spend for each month and overall
    media_spend = pg_df.groupby('MEDIA').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum',
        'TOTAL $': 'sum'
    }).reset_index()
    
    # Calculate total P&G spend for September 2024
    total_pg_sept_spend = media_spend['Sept 2024  $'].sum()
    
    # Calculate September spend as percentage of total P&G September spend for each media
    media_spend['Sept % of Total'] = (media_spend['Sept 2024  $'] / total_pg_sept_spend * 100).round(2)
    
    # Calculate month-over-month percentage differences
    media_spend['Jul-Aug % Change'] = ((media_spend['Aug 2024  $'] - media_spend['Jul 2024  $']) / 
                                      media_spend['Jul 2024  $'] * 100).round(2)
    
    media_spend['Aug-Sept % Change'] = ((media_spend['Sept 2024  $'] - media_spend['Aug 2024  $']) / 
                                       media_spend['Aug 2024  $'] * 100).round(2)
    
    # Rename columns for clarity
    media_spend = media_spend.rename(columns={
        'Jul 2024  $': 'July Spend',
        'Aug 2024  $': 'August Spend',
        'Sept 2024  $': 'September Spend',
        'TOTAL $': 'Total 3-Month Spend'
    })
    
    # Sort by September spend in descending order
    result = media_spend.sort_values('September Spend', ascending=False)
    
    # Handle NaN values in percentage change calculations (when denominator is 0)
    result = result.fillna(0)
    
    # Create a total row
    total_row = pd.DataFrame([{
        'MEDIA': 'Total',
        'July Spend': result['July Spend'].sum(),
        'August Spend': result['August Spend'].sum(),
        'September Spend': result['September Spend'].sum(),
        'Total 3-Month Spend': result['Total 3-Month Spend'].sum(),
        'Sept % of Total': 100.0,  # This will always be 100%
        'Jul-Aug % Change': ((result['August Spend'].sum() - result['July Spend'].sum()) / 
                             result['July Spend'].sum() * 100).round(2),
        'Aug-Sept % Change': ((result['September Spend'].sum() - result['August Spend'].sum()) / 
                              result['August Spend'].sum() * 100).round(2)
    }])
    
    # Append the total row to the result dataframe
    result = pd.concat([result, total_row], ignore_index=True)
    
    # Format the spending columns with $ sign and convert to millions
    for col in ['July Spend', 'August Spend', 'September Spend', 'Total 3-Month Spend']:
        new_col = col + ' ($M)'
        result[new_col] = result[col].apply(lambda x: f"${x/1000000:.2f}")
        result.drop(col, axis=1, inplace=True)
    
    # Format the percentage columns with % sign
    for col in ['Sept % of Total', 'Jul-Aug % Change', 'Aug-Sept % Change']:
        result[col] = result[col].apply(lambda x: f"{x}%")

    # Rearrange columns: Move the first three columns to the end
    new_column_order = [
        'MEDIA', 'July Spend ($M)', 'August Spend ($M)', 'September Spend ($M)', 'Total 3-Month Spend ($M)',
        'Sept % of Total', 'Jul-Aug % Change', 'Aug-Sept % Change'
    ]

    # Reorder DataFrame
    result = result[new_column_order]

    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
        
    return result, f'5. Spend by {company_name} on different media types'



def main7(df):
    # Filter for Procter & Gamble Co
    pg_df = df[df['PARENT'] == company_name]
    
    # Calculate total spend for each P&G brand
    brand_total = pg_df.groupby('BRAND')['TOTAL $'].sum().reset_index()
    brand_total = brand_total.rename(columns={'TOTAL $': 'Brand Total Spend'})
    
    # Calculate spend by brand and media type
    brand_media_spend = pg_df.groupby(['BRAND', 'MEDIA'])['TOTAL $'].sum().reset_index()
    brand_media_spend = brand_media_spend.rename(columns={'TOTAL $': 'Media Spend'})
    
    # Merge the total spend data with the media spend data
    result = pd.merge(brand_media_spend, brand_total, on='BRAND')
    
    # Calculate percentage of brand's total spend for each media
    result['Spend Percentage'] = (result['Media Spend'] / result['Brand Total Spend'] * 100).round(2)
    
    # Create a pivot table to show media types as columns
    pivot_result = result.pivot_table(
        index='BRAND',
        columns='MEDIA',
        values='Spend Percentage',
        fill_value=0
    ).reset_index()
    
    # Add the total spend column to the pivot table
    pivot_result = pd.merge(pivot_result, brand_total, on='BRAND')
    
    # Sort by total spend in descending order
    pivot_result = pivot_result.sort_values('Brand Total Spend', ascending=False)
    
    # Format currency column with $ symbol and convert to millions
    pivot_result['Brand Total Spend ($M)'] = pivot_result['Brand Total Spend'].apply(lambda x: f"${x/1000000:.2f}")
    pivot_result.drop('Brand Total Spend', axis=1, inplace=True)
    
    # Format percentage values in the pivot table
    # Get all media columns (excludes 'BRAND' and 'Brand Total Spend ($M)')
    media_columns = [col for col in pivot_result.columns if col not in ['BRAND', 'Brand Total Spend ($M)']]
    for col in media_columns:
        pivot_result[col] = pivot_result[col].apply(lambda x: f"{x:.2f}%")

    pivot_result = pivot_result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return pivot_result, f'6. Spend by {company_name} brands on different media types'


def main8(df):
    # Filter for Procter & Gamble Co and Local Radio
    pg_radio_df = df[(df['PARENT'] == company_name) & (df['MEDIA'] == 'Local Radio')]
    
    # Get total spend by brand for each month for Local Radio
    brand_radio_spend = pg_radio_df.groupby('BRAND').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Get total spend by brand for each month (all media)
    pg_all_df = df[df['PARENT'] == company_name]
    brand_total_spend = pg_all_df.groupby('BRAND').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    brand_radio_spend = brand_radio_spend.rename(columns={
        'Jul 2024  $': 'July Local Radio Spend',
        'Aug 2024  $': 'August Local Radio Spend',
        'Sept 2024  $': 'September Local Radio Spend'
    })
    
    brand_total_spend = brand_total_spend.rename(columns={
        'Jul 2024  $': 'July Total Spend',
        'Aug 2024  $': 'August Total Spend',
        'Sept 2024  $': 'September Total Spend'
    })
    
    # Merge radio spend with total spend
    merged_df = pd.merge(brand_radio_spend, brand_total_spend, on='BRAND', how='left')
    
    # Calculate percentage of September radio spend against total September spend
    merged_df['Sept Local Radio % of Total'] = (merged_df['September Local Radio Spend'] / 
                                         merged_df['September Total Spend'] * 100).round(2)
    
    # Calculate month-over-month percentage changes
    merged_df['Aug-Sept % Change'] = ((merged_df['September Local Radio Spend'] - merged_df['August Local Radio Spend']) / 
                                     merged_df['August Local Radio Spend'] * 100).round(2)
    
    merged_df['Jul-Aug % Change'] = ((merged_df['August Local Radio Spend'] - merged_df['July Local Radio Spend']) / 
                                    merged_df['July Local Radio Spend'] * 100).round(2)
    
    # Select relevant columns for final output
    result = merged_df[['BRAND', 'September Local Radio Spend', 'Sept Local Radio % of Total', 
                        'Aug-Sept % Change', 'Jul-Aug % Change']]
    
    # Sort by September Local radio spend in descending order
    result = result.sort_values('September Local Radio Spend', ascending=False)
    
    # Handle NaN values (from divisions by zero)
    result = result.fillna(0)
    
    # Format the spending column with $ sign and convert to millions
    result['September Local Radio Spend'] = result['September Local Radio Spend'].apply(lambda x: f"${x/1000000:.2f}")
    result.rename(columns={'September Local Radio Spend': 'September Local Radio Spend ($M)'}, inplace=True)
    
    # Format the percentage columns with % sign
    for col in ['Sept Local Radio % of Total', 'Aug-Sept % Change', 'Jul-Aug % Change']:
        result[col] = result[col].apply(lambda x: f"{x}%")

    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return result, f'7. Spend by {company_name} brands on Local Radio'


def main9(df):
    # Filter for Procter & Gamble Co and Network Radio
    pg_radio_df = df[(df['PARENT'] == company_name) & (df['MEDIA'] == 'Network Radio')]
    
    # Get total spend by brand for each month for Network Radio
    brand_radio_spend = pg_radio_df.groupby('BRAND').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Get total spend by brand for each month (all media)
    pg_all_df = df[df['PARENT'] == company_name]
    brand_total_spend = pg_all_df.groupby('BRAND').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    brand_radio_spend = brand_radio_spend.rename(columns={
        'Jul 2024  $': 'July Network Radio Spend',
        'Aug 2024  $': 'August Network Radio Spend',
        'Sept 2024  $': 'September Network Radio Spend'
    })
    
    brand_total_spend = brand_total_spend.rename(columns={
        'Jul 2024  $': 'July Total Spend',
        'Aug 2024  $': 'August Total Spend',
        'Sept 2024  $': 'September Total Spend'
    })
    
    # Merge Network radio spend with total spend
    merged_df = pd.merge(brand_radio_spend, brand_total_spend, on='BRAND', how='left')
    
    # Calculate percentage of September radio spend against total September spend
    merged_df['Sept Network Radio % of Total'] = (merged_df['September Network Radio Spend'] / 
                                         merged_df['September Total Spend'] * 100).round(2)
    
    # Calculate month-over-month percentage changes
    merged_df['Aug-Sept % Change'] = ((merged_df['September Network Radio Spend'] - merged_df['August Network Radio Spend']) / 
                                     merged_df['August Network Radio Spend'] * 100).round(2)
    
    merged_df['Jul-Aug % Change'] = ((merged_df['August Network Radio Spend'] - merged_df['July Network Radio Spend']) / 
                                    merged_df['July Network Radio Spend'] * 100).round(2)
    
    # Select relevant columns for final output
    result = merged_df[['BRAND', 'September Network Radio Spend', 'Sept Network Radio % of Total', 
                        'Aug-Sept % Change', 'Jul-Aug % Change']]
    
    # Sort by September Network radio spend in descending order
    result = result.sort_values('September Network Radio Spend', ascending=False)
    
    # Handle NaN values (from divisions by zero)
    result = result.fillna(0)
    
    # Format the spending column with $ sign and convert to millions
    result['September Network Radio Spend'] = result['September Network Radio Spend'].apply(lambda x: f"${x/1000000:.2f}")
    result.rename(columns={'September Network Radio Spend': 'September Network Radio Spend ($M)'}, inplace=True)
    
    # Format the percentage columns with % sign
    for col in ['Sept Network Radio % of Total', 'Aug-Sept % Change', 'Jul-Aug % Change']:
        result[col] = result[col].apply(lambda x: f"{x}%")

    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return result, f'7. Spend by {company_name} brands on Network Radio'

def main10(df):
    # Filter for Procter & Gamble Co and Natl Spot Radio
    pg_radio_df = df[(df['PARENT'] == company_name) & (df['MEDIA'] == 'Natl Spot Radio')]
    
    # Get total spend by brand for each month for Natl Spot Radio
    brand_radio_spend = pg_radio_df.groupby('BRAND').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Get total spend by brand for each month (all media)
    pg_all_df = df[df['PARENT'] == company_name]
    brand_total_spend = pg_all_df.groupby('BRAND').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum'
    }).reset_index()
    
    # Rename columns for clarity
    brand_radio_spend = brand_radio_spend.rename(columns={
        'Jul 2024  $': 'July Natl Spot Radio Spend',
        'Aug 2024  $': 'August Natl Spot Radio Spend',
        'Sept 2024  $': 'September Natl Spot Radio Spend'
    })
    
    brand_total_spend = brand_total_spend.rename(columns={
        'Jul 2024  $': 'July Total Spend',
        'Aug 2024  $': 'August Total Spend',
        'Sept 2024  $': 'September Total Spend'
    })
    
    # Merge Natl Spot radio spend with total spend
    merged_df = pd.merge(brand_radio_spend, brand_total_spend, on='BRAND', how='left')
    
    # Calculate percentage of September radio spend against total September spend
    merged_df['September Natl Spot Radio % of Total'] = (merged_df['September Natl Spot Radio Spend'] / 
                                         merged_df['September Total Spend'] * 100).round(2)
    
    # Calculate month-over-month percentage changes
    merged_df['Aug-Sept % Change'] = ((merged_df['September Natl Spot Radio Spend'] - merged_df['August Natl Spot Radio Spend']) / 
                                     merged_df['August Natl Spot Radio Spend'] * 100).round(2)
    
    merged_df['Jul-Aug % Change'] = ((merged_df['August Natl Spot Radio Spend'] - merged_df['July Natl Spot Radio Spend']) / 
                                    merged_df['July Natl Spot Radio Spend'] * 100).round(2)
    
    # Select relevant columns for final output
    result = merged_df[['BRAND', 'September Natl Spot Radio Spend', 'September Natl Spot Radio % of Total', 
                        'Aug-Sept % Change', 'Jul-Aug % Change']]
    
    # Sort by September Natl Spot radio spend in descending order
    result = result.sort_values('September Natl Spot Radio Spend', ascending=False)
    
    # Handle NaN values (from divisions by zero)
    result = result.fillna(0)
    
    # Format the spending column with $ sign (in millions)
    result['September Natl Spot Radio Spend'] = result['September Natl Spot Radio Spend'].apply(lambda x: f"${x/1000000:.2f}")
    
    # Rename the column after formatting to indicate millions
    result = result.rename(columns={'September Natl Spot Radio Spend': 'September Natl Spot Radio Spend ($M)'})
    
    # Format the percentage columns with % sign
    for col in ['September Natl Spot Radio % of Total', 'Aug-Sept % Change', 'Jul-Aug % Change']:
        result[col] = result[col].apply(lambda x: f"{x}%")

    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return result, f'7. Spend by {company_name} brands on Natl Spot Radio'


def main11(df):
    # Filter for Procter & Gamble Co
    pg_df = df[df['PARENT'] == company_name]
    
    # Group by category and calculate total spend for each month and overall
    category_spend = pg_df.groupby('CATEGORY').agg({
        'Jul 2024  $': 'sum',
        'Aug 2024  $': 'sum',
        'Sept 2024  $': 'sum',
        'TOTAL $': 'sum'
    }).reset_index()
    
    # Calculate the total P&G spend for September 2024
    total_pg_sept_spend = category_spend['Sept 2024  $'].sum()
    
    # Calculate September spend as percentage of total P&G September spend
    category_spend['Sept % of P&G Total'] = (category_spend['Sept 2024  $'] / total_pg_sept_spend * 100).round(2)
    
    # Calculate month-over-month percentage differences
    category_spend['Jul-Aug % Change'] = ((category_spend['Aug 2024  $'] - category_spend['Jul 2024  $']) / 
                                         category_spend['Jul 2024  $'] * 100).round(2)
    
    category_spend['Aug-Sept % Change'] = ((category_spend['Sept 2024  $'] - category_spend['Aug 2024  $']) / 
                                          category_spend['Aug 2024  $'] * 100).round(2)
    
    # Rename columns for clarity
    category_spend = category_spend.rename(columns={
        'Jul 2024  $': 'July Spend',
        'Aug 2024  $': 'August Spend',
        'Sept 2024  $': 'September Spend',
        'TOTAL $': 'Total 3-Month Spend'
    })
    
    # Sort by September spend in descending order
    result = category_spend.sort_values('September Spend', ascending=False)
    
    # Handle NaN values in percentage change calculations (when denominator is 0)
    result = result.fillna(0)
    
    # Create a total row
    total_row = pd.DataFrame([{
        'CATEGORY': 'Total',
        'July Spend': result['July Spend'].sum(),
        'August Spend': result['August Spend'].sum(),
        'September Spend': result['September Spend'].sum(),
        'Total 3-Month Spend': result['Total 3-Month Spend'].sum(),
        'Sept % of P&G Total': 100.0,  # This will always be 100%
        'Jul-Aug % Change': ((result['August Spend'].sum() - result['July Spend'].sum()) / 
                             result['July Spend'].sum() * 100).round(2),
        'Aug-Sept % Change': ((result['September Spend'].sum() - result['August Spend'].sum()) / 
                              result['August Spend'].sum() * 100).round(2)
    }])
    
    # Append the total row to the result dataframe
    result = pd.concat([result, total_row], ignore_index=True)
    
    # Format currency columns with $ symbol (in millions)
    currency_columns = ['July Spend', 'August Spend', 'September Spend', 'Total 3-Month Spend']
    for col in currency_columns:
        result[col] = result[col].apply(lambda x: f"${x/1000000:.2f}")
    
    # Rename columns after formatting to indicate millions
    result = result.rename(columns={
        'July Spend': 'July Spend ($M)',
        'August Spend': 'August Spend ($M)',
        'September Spend': 'September Spend ($M)',
        'Total 3-Month Spend': 'Total 3-Month Spend ($M)'
    })
    
    # Format percentage columns with % symbol
    percentage_columns = ['Sept % of P&G Total', 'Jul-Aug % Change', 'Aug-Sept % Change']
    for col in percentage_columns:
        result[col] = result[col].apply(lambda x: f"{x:.2f}%")
    
    result = result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return result, f'8. Spend by {company_name} categories across all platforms'


def main12(df):
    # Calculate total spend for each parent company
    parent_total = df.groupby('PARENT')['TOTAL $'].sum().reset_index()
    parent_total = parent_total.rename(columns={'TOTAL $': 'Parent Total Spend'})
    
    # Calculate spend by parent and media
    parent_media_spend = df.groupby(['PARENT', 'MEDIA'])['TOTAL $'].sum().reset_index()
    parent_media_spend = parent_media_spend.rename(columns={'TOTAL $': 'Media Spend'})
    
    # Merge the total spend data with the media spend data
    result = pd.merge(parent_media_spend, parent_total, on='PARENT')
    
    # Calculate percentage of parent's total spend for each media
    result['Spend Percentage'] = (result['Media Spend'] / result['Parent Total Spend'] * 100).round(2)
    
    # Create a pivot table to show media types as columns
    pivot_result = result.pivot_table(
        index='PARENT',
        columns='MEDIA',
        values='Spend Percentage',
        fill_value=0
    ).reset_index()
    
    # Add the total spend column to the pivot table
    pivot_result = pd.merge(pivot_result, parent_total, on='PARENT')
    
    # Sort by total spend in descending order
    pivot_result = pivot_result.sort_values('Parent Total Spend', ascending=False)
    
    # Get the top 50 rows
    top_50_result = pivot_result[:50]
    
    # Calculate the total row data
    # First for total spend
    total_spend = pivot_result['Parent Total Spend'].sum()
    
    # Get all media columns
    media_columns = [col for col in pivot_result.columns if col not in ['PARENT', 'Parent Total Spend']]
    
    # For media percentages, we need to recalculate based on actual spend amounts
    media_totals = {}
    for media in media_columns:
        # Calculate actual spend for each media type
        df_media_total = df.groupby('MEDIA')['TOTAL $'].sum().reset_index()
        df_media_total = df_media_total.set_index('MEDIA')['TOTAL $'].to_dict()
        
        # Calculate percentage of total spend for each media
        if media in df_media_total:
            media_totals[media] = (df_media_total[media] / df['TOTAL $'].sum() * 100).round(2)
        else:
            media_totals[media] = 0
    
    # Create total row
    total_row = {'PARENT': 'Total', 'Parent Total Spend': total_spend}
    for media in media_columns:
        total_row[media] = media_totals.get(media, 0)
    
    # Add total row to top 50
    top_50_with_total = pd.concat([top_50_result, pd.DataFrame([total_row])], ignore_index=True)
    
    # Format currency column with $ symbol (in millions)
    top_50_with_total['Parent Total Spend'] = top_50_with_total['Parent Total Spend'].apply(lambda x: f"${x/1000000:.2f}")
    
    # Rename the column after formatting
    top_50_with_total = top_50_with_total.rename(columns={'Parent Total Spend': 'Parent Total Spend ($M)'})
    
    # Format percentage values in the pivot table
    # Get all media columns (excludes 'PARENT' and 'Parent Total Spend ($M)')
    media_columns = [col for col in top_50_with_total.columns if col not in ['PARENT', 'Parent Total Spend ($M)']]
    for col in media_columns:
        top_50_with_total[col] = top_50_with_total[col].apply(lambda x: f"{x:.2f}%")
    
    top_50_with_total = top_50_with_total.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    
    return top_50_with_total, f'9. Spend by parents on different media types'


def main13(df):
    import pandas as pd

    # Remove specific rows from 'INDUSTRY' column
    excluded_values = [
        'GRAND TOTAL',
        '(c) 2024 Competitive Media Reporting LLC d/b/a Vivvix',
        'Digital estimation models include SimilarWeb metrics.',
        'Mobile Web dollars and impressions start April 1 2015',
        'Mobile Web Video spend and impressions start October 1 2019',
        'Mobile App dollars and impressions start January 1 2021',
        'The following media have no occurrence (units) data: Internet - Search'
    ]

    df = df[~df['INDUSTRY'].isin(excluded_values)]
    # Step 1: Calculate total spend by industry
    industry_total = df.groupby('INDUSTRY')['TOTAL $'].sum().reset_index()
    industry_total = industry_total.sort_values('TOTAL $', ascending=False)
    
    # Step 2: Calculate spend by industry and media group
    industry_media_spend = df.groupby(['INDUSTRY', 'MEDIA'])['TOTAL $'].sum().reset_index()
    
    # Step 3: Create a pivot table to get industry-media combinations
    pivot_df = pd.pivot_table(
        industry_media_spend,
        values='TOTAL $',
        index='INDUSTRY',
        columns='MEDIA',
        fill_value=0
    ).reset_index()
    
    # Step 4: Merge with industry totals
    result = pd.merge(
        industry_total,
        pivot_df,
        on='INDUSTRY',
        how='left'
    )
    
    # Get the media columns (excluding 'INDUSTRY' and 'TOTAL $')
    media_columns = [col for col in result.columns if col not in ['INDUSTRY', 'TOTAL $']]
    
    # Step 5: Calculate percentages for each media group within each industry
    for media in media_columns:
        result[f'{media} %'] = (result[media] / result['TOTAL $'] * 100).round(2)
    
    # Sort before formatting
    result = result.sort_values('TOTAL $', ascending=False)
    
    # Create a total row before formatting
    total_row_data = {'INDUSTRY': 'Total', 'TOTAL $': result['TOTAL $'].sum()}
    
    # Calculate total values for each media column
    for media in media_columns:
        total_row_data[media] = result[media].sum()
        # Calculate the percentage for total row
        total_row_data[f'{media} %'] = (total_row_data[media] / total_row_data['TOTAL $'] * 100).round(2)
    
    # Create DataFrame from total row data
    total_row = pd.DataFrame([total_row_data])
    
    # Append the total row to the result
    result = pd.concat([result, total_row], ignore_index=True)
    
    # Construct final dataframe
    final_result = pd.DataFrame({
        'Industry': result['INDUSTRY'],
        'Total Spend ($M)': result['TOTAL $'].apply(lambda x: f"${x/1000000:.2f}")
    })
    
    # Add separate columns for each media percentage
    for media in media_columns:
        final_result[f'{media} %'] = result[f'{media} %'].apply(lambda x: f"{x:.2f}%")

    # Define new column order with 'Total Spend ($M)' at the end
    new_column_order = ['Industry', 'AVOD %', 'B-to-B Magazines %',
       'Cable TV %', 'Cinema %', 'Hispanic Magazines %',
       'Hispanic Newspapers %', 'Internet - Display %', 'Internet - Search %',
       'Local Magazines %', 'Local Radio %', 'Magazines %', 'Mobile App %',
       'Mobile Web %', 'Mobile Web Video %', 'Natl Spot Radio %',
       'Network Radio %', 'Network TV %', 'Newspapers %', 'Online Video %',
       'Outdoor %', 'Span Lang Net TV %', 'Spot TV %', 'Sunday Magazines %',
       'Syndication %', 'Total Spend ($M)']

    # Reorder DataFrame
    final_result = final_result[new_column_order]

    final_result = final_result.applymap(lambda x: '-' if isinstance(x, str) and 'inf%' in x else x)
    print(final_result.columns)
    
    return final_result, '10. Spend by industry on different media types'


def main14(df):
    # Define the parent name explicitly here
    #company_name = "Procter & Gamble Co"  # You can change this to any parent company name
    
    # Filter dataframe for the specified parent
    parent_df = df[df['PARENT'] == company_name]
    
    if parent_df.empty:
        print(f"No data found for parent: {company_name}")
        return pd.DataFrame()  # Return empty dataframe if no data found
    
    # Get unique brands for this parent
    brands = parent_df['BRAND'].unique()
    
    # Create empty lists to store our results
    results = []
    
    for brand in brands:
        # Filter for this brand
        brand_df = parent_df[parent_df['BRAND'] == brand]
        
        # Calculate total spend for this brand
        total_spend = brand_df['TOTAL $'].sum()
        
        # Calculate radio spend for this brand
        radio_df = brand_df[brand_df['MEDIA GROUP'] == 'Radio']
        radio_spend = radio_df['TOTAL $'].sum()
        
        # Calculate iHeart spend for this brand
        iheart_df = brand_df[brand_df['MEDIA OWNER'] == 'iHeartMedia Inc']
        iheart_spend = iheart_df['TOTAL $'].sum()
        
        # Calculate iHeart spend on radio
        iheart_radio_df = iheart_df[iheart_df['MEDIA GROUP'] == 'Radio']
        iheart_radio_spend = iheart_radio_df['TOTAL $'].sum()
        
        # Calculate percentages
        iheart_pct_of_total = (iheart_spend / total_spend * 100) if total_spend > 0 else 0
        iheart_pct_of_radio = (iheart_radio_spend / radio_spend * 100) if radio_spend > 0 else 0
        
        # Add to results
        results.append({
            'Brand': brand,
            'Total Spend ($)': total_spend,
            'Radio Spend ($)': radio_spend,
            'iHeart Total Spend ($)': iheart_spend,
            'iHeart % of Total': iheart_pct_of_total,
            'iHeart Radio Spend ($)': iheart_radio_spend,
            'iHeart % of Radio': iheart_pct_of_radio
        })
    
    # Convert to DataFrame
    result_df = pd.DataFrame(results)
    
    # Format percentages
    result_df['iHeart % of Total'] = result_df['iHeart % of Total'].round(1)
    result_df['iHeart % of Radio'] = result_df['iHeart % of Radio'].round(1)
    
    # Sort the dataframe by Radio Spend in descending order
    result_df = result_df.sort_values(by='iHeart Total Spend ($)', ascending=False)
    
    
    return result_df, f'Spend by {company_name} brands on iHeartMedia Inc'