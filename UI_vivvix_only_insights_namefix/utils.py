from openai import OpenAI
import os
from vars import SIMPLE_PROMPT, INSIGHTS_PROMPT, OVERALL_INSIGHTS_PROMPT
import pandas as pd
import json
import streamlit as st
from pandas.api.types import is_numeric_dtype
import spacy
import re
import types
import json
#from langchain_community.embeddings import OllamaEmbeddings
#import faiss
import json
import numpy as np
import logging

#API_KEY = os.environ["OPENAI_API_KEY"]
MODEL="gpt-4-turbo"
# Set the API
client = OpenAI(api_key=API_KEY)

def gpt_response(prompt, message_history=None, return_code=False):
    
    history = message_history[:]
    # Define the system prompt
    if return_code:
        system_prompt = SIMPLE_PROMPT
            
        logging.info("SYS - " + system_prompt)
        prompt = [[{"role": "system", "content": system_prompt}], {"role": "user", "content": prompt}]
        
    else:
        system_prompt = """You are a data analyst chatbot designed to help users understand and analyze their data effectively.
                You can perform tasks such as summarizing datasets, identifying trends, visualizing data, and providing
                actionable insights. Always respond in a clear, concise, and professional tone. Provide the result by inferring from the given data.
                Return values representing them."""
                
        prompt = [[{"role": "system", "content": system_prompt}], {"role": "user", "content": prompt}]
        
    prompt[0].extend(history)
    history = prompt[0]
    history.append(prompt[1]) # Goes like System - history - user prompt
    
    # Store the history for every prompt
    file = open("prompts.json", "a+")
    json.dump(history, file, indent=4)
        
    # Call the API
    bot = client.chat.completions.create(
        model=MODEL,
        messages = history,
        temperature=0,
    )
    return bot.choices[0].message.content



def gpt_insight_response(df: pd.DataFrame, company_name):
    """
    Generates insights based on the given DataFrame using GPT.
    
    Args:
        df (pd.DataFrame): The input data table.
    
    Returns:
        str: Generated insights from the model.
    """
    
    # Convert the DataFrame to a JSON-friendly string format
    data_json = df.to_json(orient="records")  # Convert full data to JSON format
    print(data_json)
    
    # Construct the system prompt
    system_prompt = INSIGHTS_PROMPT(company_name) + "\n\nData:\n" + data_json
    
    # Construct the prompt
    prompt = [{"role": "system", "content": system_prompt}]

    
    # Call the OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o",  # Update with the appropriate model
        messages=prompt,
        temperature=0.5,  # Adjust temperature for creativity
    )
    
    return response.choices[0].message.content




def read_document(file, usr_id):
    if isinstance(file, dict):
        name = file['name']
        file = pd.read_csv(file['path'])
        file  = clean_df(file)
        #save_files(file, name, usr_id)
        return file
    name = file.name
    if name.endswith(".csv"):
        file = pd.read_csv(file)
        file = clean_df(file)
        save_files(file, name, usr_id)
    return file

def store_json(content, usr_id):
    os.makedirs(usr_id, exist_ok=True)
    out_file = open(f"{usr_id}/conversation.json", "w")
    json.dump(content, out_file, indent=4)
    
    return None

def segment_code(content, usr_id):
    finds = re.findall(r"(?<=```python)([\s\S]*?)(?=```)", content)
    try:
        files = os.listdir(f"{usr_id}/imgs")
    except:
        files = []
        os.makedirs(f"{usr_id}/imgs", exist_ok=True)
    executables = []
    plots = []
    for code in finds:
        # if "plt.show()" in code:
        #     code = code.replace("plt.show()",f"plt.savefig('{usr_id}/imgs/plot_{len(files)}.png')")
        #     plots.append(f'{usr_id}/imgs/plot_{len(files)}.png')
            
        executables.append(code)
    return executables

def save_files(file, name, usr_id):
    os.makedirs(f"{usr_id}/docs", exist_ok=True)
    file.to_csv(f"{usr_id}/docs/{name}", index=False)
    
    
def dataframe_to_markdown(df):
    markdown = "| " + " | ".join(df.columns) + " |\n"
    markdown += "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
    for index, row in df.iterrows():
        markdown += "| " + " | ".join(map(str, row.values)) + " |\n"
    return markdown

def dataframe_to_html(df):
    return df.to_html(classes='table', border=0, index=False, justify='center', escape=False).replace(
        '<table ',
        '<table style="width:100%; border-collapse: collapse; text-align: center;" '
    )

def change_dtype(x):
    if len(x) == 10:
        return int(x)
    else:
        return 0
    
# def clean_df(df):

#     df = df.copy()
#     df = df.iloc[:, 1:]

#     # Columns to process for float conversion
#     float_columns = [
#         'Jul 2024  $', 'Jul 2024  UNITS', 'Aug 2024  $', 'Aug 2024  UNITS',
#         'Sept 2024  $', 'Sept 2024  UNITS', 'TOTAL $', 'TOTAL UNITS'
#     ]

#     # Remove commas and convert to float
#     for col in float_columns:
#         df[col] = df[col].str.replace(',', '').astype('float64')

#     return df

def clean_df(df):
    if 'TOTAL $' in df.columns:
        df = df.copy()
        df = df.iloc[:, 1:]
        # df = df[df['MEDIA GROUP'] != 'Digital']
        # Columns to process for float conversion
        float_columns = [
            'Jul 2024  $', 'Jul 2024  UNITS', 'Aug 2024  $', 'Aug 2024  UNITS',
            'Sept 2024  $', 'Sept 2024  UNITS', 'TOTAL $', 'TOTAL UNITS'
        ]
        # Remove commas and convert to float
        for col in float_columns:
            df[col] = df[col].astype(str).str.replace(',', '').astype('float64')
        #df = df.dropna(subset=['MEDIA'])
    else:
        df = df.copy()
        df = df.iloc[:, 1:]
        df['Date'] = pd.to_datetime(df['Date'])
    return df

def check_user_existence(file_name, username):
    file = open(file_name, "r")
    lines = file.readlines()
    lines = list(map(lambda x: x[:-1].split(",")[0], lines[1:]))
    file.close()
    return username in lines

def turq_grad(step=10):
    import matplotlib.colors as mcolors
    # Define start and end colors
    start_color = '#E0F7FA' #"#E0F7FA"  # Light turquoise
    end_color = "#004D40" #"#006064"    # Dark turquoise

    # Number of colors in the gradient
    num_colors = 10

    # Generate the gradient
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_gradient", [start_color, end_color])
    gradient = [mcolors.to_hex(cmap(i / (num_colors - 1))) for i in range(num_colors)]
    
    return gradient

def check_numeric(df):
    return is_numeric_dtype(df)

def format_table(df):
    for col in df.columns:
        if check_numeric(df[col]):
            df = df[df[col] != 0]
    return df

def execute(code, data):
    global_env = {'pd':pd}
    exec(code, global_env)
    if len(data) == 1:
        result = global_env["main"](data[0])
        return result
    elif len(data) > 1:
        result = global_env["main"](*tuple(data))
        return result
    
def execute_predefined(code, data, company_name):
    final_result = []
    global_env = {'pd':pd, 'company_name': company_name}
    exec(code, global_env)
    function_names = [name for name, obj in global_env.items() if isinstance(obj, types.FunctionType)]
    # function_count = sum(1 for name, obj in global_env.items() if isinstance(obj, types.FunctionType))
    for function in function_names:
        if len(data) == 1:
            result, desc = global_env[function](data[0])
            final_result.append((result, desc))
        elif len(data) > 1:
            result, desc = global_env[function](*tuple(data))
            final_result.append((result, desc))
    return final_result
    




def generate_overall_insights(conversation_file):
    # Read the entire conversation file
    def read_conversation_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        return content
    
    # Read conversation text
    conversation_text = read_conversation_file(conversation_file)
    
    # Construct the input message
    messages = [
        {"role": "system", "content": OVERALL_INSIGHTS_PROMPT},
        {"role": "user", "content": f"Data:\n\n{conversation_text}"}
    ]
    
    # Make API call to OpenAI
    api_response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.5,
    )
    insight_text = api_response.choices[0].message.content.strip()
    
    # Display results in Streamlit
    st.header("Insights")
    st.markdown(insight_text)
    
    return insight_text



# def extract_category_gpt(sentence):
#     prompt = f"""
#     You are an advanced NLP model that extracts **industries** and **organization names** from a given sentence.

#     Output format:
#         CATEGORY: ['industry1', 'industry2'] or None
#         PARENT: ['Organization1', 'Organization2'] or None

#     Instructions:
#         1. Identify industries (e.g., "pharmaceutical", "automobile", "technology") if they exist in the sentence. If multiple industries exist, return all of them.
#         2. Identify organization names (e.g., "p&g", "sanofi", "verizon") if they exist in the sentence. If multiple organizations exist, return all of them.
#         3. Return 'None' if no industry or organization is found.
#         4. Return only single words for industries (e.g., extract "pharmaceutical" instead of "pharmaceutical industry").


#     Sentence:
#     {sentence}
#     """

#     # Call the API
#     bot = client.chat.completions.create(
#         model="gpt-4o-mini",  
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0
#     )

#     text = bot.choices[0].message.content.strip()

#     # Regular expression to extract content inside square brackets
#     category_match = re.search(r"CATEGORY:\s*\[(.*?)\]", text)
#     parent_match = re.search(r"PARENT:\s*\[(.*?)\]", text)

#     # Extract values and store in a dictionary
#     extracted_data = {
#         "CATEGORY": category_match.group(1).replace("'", "").split(', ') if category_match else None,
#         "PARENT": parent_match.group(1).replace("'", "").split(', ') if parent_match else None
#     }

#     return extracted_data


import re

def extract_parent_gpt(sentence):
    prompt = f"""
    You are an advanced model that extracts organization names from a given sentence.

    Output format:
        PARENT: ['Organization1', 'Organization2'] or None

    Instructions:
        1. Identify organization names (e.g., "P&G", "Sanofi", "Verizon") if they exist in the sentence. 
        2. If multiple organizations exist, return all of them.
        3. Return 'None' if no organization is found.

    Sentence:
    {sentence}
    """

    # Call the API
    bot = client.chat.completions.create(
        model="gpt-4o-mini",  
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    text = bot.choices[0].message.content.strip()

    # Regular expression to extract content inside square brackets
    parent_match = re.search(r"PARENT:\s*\[(.*?)\]", text)

    # Extract values and store in a dictionary
    extracted_data = {
        "PARENT": parent_match.group(1).replace("'", "").split(', ') if parent_match else None
    }

    return extracted_data



def load_faiss_index(index_path="vector_database.index", metadata_path="metadata.json"):
    """
    Loads the FAISS index and metadata from disk.

    Args:
        index_path (str): Path to the FAISS index file.
        metadata_path (str): Path to the metadata JSON file.

    Returns:
        faiss.IndexFlatL2, List[str]: The FAISS index and corresponding metadata (company names).
    """
    index = faiss.read_index(index_path)
    with open(metadata_path, "r") as f:
        company_names = json.load(f)
    return index, company_names

# def search_similar(query: str, index_path="vector_database.index", metadata_path="metadata.json"):
#     """
#     Searches for the top_k most similar company descriptions in the FAISS vector database.

#     Args:
#         query (str): Input string (company name or company name + short description).
#         top_k (int): Number of results to return.
#         index_path (str): Path to the FAISS index file.
#         metadata_path (str): Path to the metadata JSON file.

#     Returns:
#         List of tuples containing (company_name, similarity_score).
#     """

#     top_k = 1

#     # Load FAISS Index and Metadata
#     index, company_names = load_faiss_index(index_path, metadata_path)

#     # Initialize embedding model
#     embeddings_model = OllamaEmbeddings(model="nomic-embed-text")

#     # Generate query embedding
#     query_embedding = np.array([embeddings_model.embed_query(query)])

#     # Search for the top_k most similar embeddings
#     distances, indices = index.search(query_embedding, top_k)

#     # Retrieve matching company names
#     results = [(company_names[i], distances[0][j]) for j, i in enumerate(indices[0])]

#     return results




import json
import numpy as np
import requests
import faiss

def load_faiss_index(index_path, metadata_path):
    """Load the FAISS index and metadata."""
    index = faiss.read_index(index_path)
    
    with open(metadata_path, 'r') as f:
        company_names = json.load(f)
    
    return index, company_names

def get_ollama_embedding(text, model="nomic-embed-text"):
    """Get embeddings directly from Ollama API."""
    response = requests.post(
        "http://localhost:11434/api/embeddings",
        json={
            "model": model,
            "prompt": text
        }
    )
    
    if response.status_code != 200:
        raise Exception(f"Error from Ollama API: {response.text}")
    
    return np.array(response.json()["embedding"])

def search_similar(query: str, index_path="vector_database.index", metadata_path="metadata.json"):
    """
    Searches for the top_k most similar company descriptions in the FAISS vector database.

    Args:
        query (str): Input string (company name or company name + short description).
        index_path (str): Path to the FAISS index file.
        metadata_path (str): Path to the metadata JSON file.

    Returns:
        List of tuples containing (company_name, similarity_score).
    """
    top_k = 1

    # Load FAISS Index and Metadata
    index, company_names = load_faiss_index(index_path, metadata_path)

    # Generate query embedding directly using Ollama API
    query_embedding = np.array([get_ollama_embedding(query, model="nomic-embed-text")])

    # Search for the top_k most similar embeddings
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve matching company names
    results = [(company_names[i], distances[0][j]) for j, i in enumerate(indices[0])]

    return results






def get_company_description(company_name: str) -> str:
    """
    Queries Perplexity AI to get a one-line description of a company.

    Args:
        company_name (str): Name of the company.
        api_key (str): API key for Perplexity AI.

    Returns:
        str: A string containing the company name and its description.
    """

    PERPLEXITY_API_KEY = "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"
    # Initialize OpenAI client with Perplexity's base URL
    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
    
    # Define prompt for getting a single-line description
    messages = [
        {
            "role": "system",
            "content": "You are an assistant that provides short descriptions of companies."
        },
        {
            "role": "user",
            "content": f"Give me a 1-line description about the company {company_name}."
        }
    ]
    
    try:
        # Call Perplexity API
        response = client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",
            messages=messages,
        )
        
        # Extract the description from the response
        description = response.choices[0].message.content.strip()
        
        # Return formatted output
        return f"{company_name}: {description}"
    
    except Exception as e:
        logging.error(f"Error fetching description for {company_name}: {str(e)}")
        return f"{company_name}: Description not available"



