from utils import clean_df
import pandas as pd
import matplotlib.pyplot as plt

def main(leads_df, code_df, spend_df, texts_df):
    # Convert 'Week Of' in spend_df to datetime and extract the week
    spend_df['Week Of'] = pd.to_datetime(spend_df['Week Of'])
    spend_df['Week'] = spend_df['Week Of'].dt.to_period('W').apply(lambda r: r.start_time)
    
    # Convert 'INITIAL_CONTACT_DATE' in leads_df to datetime and extract the week
    leads_df['INITIAL_CONTACT_DATE'] = pd.to_datetime(leads_df['INITIAL_CONTACT_DATE'])
    leads_df['Week'] = leads_df['INITIAL_CONTACT_DATE'].dt.to_period('W').apply(lambda r: r.start_time)
    
    # Clean up the $ SPENT column to convert it to float
    spend_df['$ SPENT'] = spend_df['$ SPENT'].replace('[\$,]', '', regex=True).astype(float)
    print(spend_df)
    # Join leads_df with spend_df based on Keyword and Week
    merged_df = pd.merge(leads_df, spend_df, left_on=['Week'], right_on=['Week'], how='inner')
    print(merged_df)
    
    # Group by Week and Radio Fmt Name to calculate cost per lead
    grouped = merged_df.groupby(['Week', 'Radio Fmt Name']).agg(
        Total_Spent=('$ SPENT', 'sum'),
        Leads_Count=('LEAD_SOURCE', 'count')
    ).reset_index()
    
    # Calculate cost per lead
    grouped['Cost Per Lead'] = grouped['Total_Spent'] / grouped['Leads_Count']
    
    # Sort by Week and Cost Per Lead to find the most cost-efficient radio format each week
    grouped.sort_values(by=['Week', 'Cost Per Lead'], ascending=[True, True], inplace=True)
    
    # Select the most cost-efficient radio format per week
    most_efficient = grouped.groupby('Week').first().reset_index()
    
    # Select relevant columns to return
    result_df = most_efficient[['Week', 'Radio Fmt Name', 'Cost Per Lead']]
    
    return result_df


df0 = pd.read_csv("../../datasets/lead gen/Leads File.csv")
df1 = pd.read_csv("../../datasets/lead gen/Short Code.csv")
df2 = pd.read_csv("../../datasets/lead gen/Spend Data.csv")
df3 = pd.read_csv("../../datasets/lead gen/Texts File.csv")
# df0 = pd.read_csv("../datasets/Leads File.csv")
# df1 = pd.read_csv("../datasets/Texts File.csv")
df0, df1, df2, df3 = clean_df(df0), clean_df(df1), clean_df(df2), clean_df(df3)

print(main(df0,df1,df2,df3).head(15))