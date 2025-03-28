import streamlit as st
from utils import get_company_description, search_similar, extract_parent_gpt, generate_overall_insights, gpt_insight_response, execute_predefined, gpt_response, read_document, store_json, segment_code, dataframe_to_html, execute
import pandas as pd
import logging
import plotly.express as px
from style import style
from pathlib import Path

GIVE_UP = "Sorry, Unable to provide answer for the given query :( We are working on our product"
pd.set_option('display.float_format', '{:,.0f}'.format) 



# Add this function to load and execute your predefined functions
def load_and_execute_predefined_functions(file_content, company_name):
    results = []
    
    # Path to the predefined functions file
    functions_file_path = Path("predefined_functions.py")
    if functions_file_path.exists():
        with open("predefined_functions.py", "r") as file:
            code_str = file.read() 
        results = execute_predefined(code_str, file_content, company_name)

    return results

def write_or_append(data, file_name):

    file_path = Path(file_name)

    # Set the mode to "w" only if the file is being written for the first time in this session
    if file_name not in st.session_state.first_run_in_script:
        st.session_state.first_run_in_script[file_name] = True

    mode = "w" if st.session_state.first_run_in_script[file_name] else "a"
    st.session_state.first_run_in_script[file_name] = False  # Switch to "a" mode after the first function call for this file

    # Convert a single string to a list
    if isinstance(data, str):
        data = [data]

    with file_path.open(mode) as file:
        file.writelines(f"{line}\n" for line in data)


def load_preloaded_files(usr_id):
    preload_dir = Path("/home/ec2-user/data")
    #preload_dir = Path("C:/Users/Hashim/OneDrive/Desktop/aqxle/insights_demo/data")
    preloaded_files = []
    
    if preload_dir.exists():
        for file in preload_dir.glob("*.csv"):  # List only CSV files
            preloaded_files.append((file.name, str(file)))  # Store as (name, path)
    else:
        print(f"Directory does not exist: {preload_dir}")

    return preloaded_files

def main_page(usr_id):

    if "file_content" not in st.session_state:
        st.session_state.file_content = []

    if "first_run_in_script" not in st.session_state:
        st.session_state.first_run_in_script = {}
        
    if "Check_upload" not in st.session_state:
        st.session_state.Check_upload = []

    # if "gen_button" not in st.session_state:
    #     st.session_state.gen_button = False

    if 'run_predefined_functions' not in st.session_state:
        st.session_state.run_predefined_functions = False
        
    # Set the page title and icon
    st.set_page_config(page_title="Aqxle", page_icon=":speech_balloon:", layout="wide")

    # Set the background color and other styles
    st.markdown(style, unsafe_allow_html=True)
    

    def handle_data_source_change():
        st.session_state.file_content = []

    with st.sidebar:

        # Title of the app
        st.markdown("<h1 style='font-size: 50px; text-align: center;'>Aqxle</h1>", unsafe_allow_html=True)
        
        st.title("Manage Files")

        # Track the radio button selection
        if 'data_source' not in st.session_state:
            st.session_state.data_source = "Pre-loaded Files"

        st.radio(
            "Choose data source:",
            ("Pre-loaded Files", "Upload Files"),
            index=0 if st.session_state.data_source == "Pre-loaded Files" else 1,
            key="data_source",
            on_change=handle_data_source_change,
        )

        if st.session_state.data_source == "Upload Files":
            st.session_state.uploaded_file = st.file_uploader("Upload a file", type=["csv"], accept_multiple_files=True)
        else:
            # Load pre-loaded files
            preloaded_files = load_preloaded_files(usr_id)
            if preloaded_files:
                # Show available pre-loaded files
                selected_files = st.multiselect(
                    "Select pre-loaded files:",
                    options=[file[0] for file in preloaded_files],  # Use first element of tuple (filename)
                    default=[]  # Use first element of tuple (filename)
                )
                # Convert selected pre-loaded files to format similar to uploaded files
                st.session_state.uploaded_file = [
                    {
                        'name': filename,
                        'path': next(f[1] for f in preloaded_files if f[0] == filename)  # Match filename to get path
                    }
                    for filename in selected_files
                ]
            else:
                st.warning("No pre-loaded files available")
                st.session_state.uploaded_file = []

            # Display uploaded file information
            if len(st.session_state.uploaded_file) and st.session_state.Check_upload!=st.session_state.uploaded_file:
                for i, file in enumerate(st.session_state.uploaded_file):
                    #for a single file
                    st.session_state.file_content.append(read_document(file,usr_id))
                st.session_state.Check_upload = st.session_state.uploaded_file

        if len(st.session_state.uploaded_file) > 0:
            st.title("Analyze")

            company_name = st.text_input("Enter company name:")


            gpt_output_2 = extract_parent_gpt(company_name)
            #st.write(gpt_output)

            if gpt_output_2['PARENT'] is not None:

                parent_string_2 = gpt_output_2['PARENT'][0].lower()

                company_desc_2 = get_company_description(parent_string_2)

                normalized_parent_2 = search_similar(parent_string_2+" "+company_desc_2)

                company_name = company_name.lower().replace(parent_string_2, str(normalized_parent_2[0][0]))

            st.write(company_name)

            if st.button("Analyze"):
                if len(st.session_state.uploaded_file) > 0:
                    with st.spinner("Analyzing data... This may take a moment."):
                        # Run predefined functions
                        try:
                            predefined_results = load_and_execute_predefined_functions(st.session_state.file_content, company_name)
                            write_or_append("Predefined Functions:\n", 'results.log')
                            write_or_append(predefined_results, 'results.log')

                            #### write gpt function here to get table wise insights.

                            # Display results from each function
                            for result, desc in predefined_results:
                                if isinstance(result, pd.DataFrame):
                                    # Add results to display history to show in the chat interface
                                    insight = gpt_insight_response(result, company_name)
                                    st.session_state.display_history.append({"role": "assistant", "table": result, "insight": insight, 'desc':desc})
                                    write_or_append([desc+"\n"], 'conversation.txt')
                                    write_or_append([result[:100].to_string()+"\n\n"], 'conversation.txt')
                        except:
                            st.write(GIVE_UP)
                                
                else:
                    st.warning("Please upload files first before running predefined analysis.")

        else:
            st.markdown("Please add a file to get started")


    # Add index for chatting
    if 'stop_index' not in st.session_state:
        st.session_state.stop_index = 0
        
    # Initialize session state for chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Chat to display to the user
    if 'display_history' not in st.session_state:
        st.session_state.display_history = []

    
    def eval_loop(user_input, response, error, return_code=True, termination = 0):
        global_env = {'pd':pd}
        for _ in range(5):
            try:
                st.session_state.chat_history.extend([{"role": "user", "content": user_input},{"role": "assistant", "content": response}])
                user_input = f"""\n Got the following error when executing the code. Correct the line with the error and return only the complete code.\n{error}."""
                response = gpt_response(f"{user_input}", message_history=st.session_state.chat_history, return_code=return_code)
                executables = segment_code(response,usr_id=usr_id)
                logging.info("Logging ERROR \n" + str(error) +response)
                logging.info("Logging Result - ", global_env.keys())
                table = execute(executables[0], st.session_state.file_content)

                return response, user_input, table # Add markdown of the result to response using -> + f"\n{dataframe_to_markdown(global_env['result'])}"
            
            except Exception as e:
                error = f"{str(type(e))} {e}"
                # logging.info("ERROR TRACEBACK - ", traceback.format_exc())
                continue
            
        return GIVE_UP, user_input, None
    

    # Function to handle user input
    
    def respond():

        user_input = st.session_state.user_input

        gpt_output = extract_parent_gpt(user_input)
        #st.write(gpt_output)

        if gpt_output['PARENT'] is not None:

            parent_list = [parent.lower() for parent in gpt_output['PARENT']]
            #st.write(parent_list)
            user_input = user_input.lower()

            for parent in parent_list:
                company_desc = get_company_description(parent)
                #st.write(company_desc)
                normalized_parent = search_similar(parent+" "+company_desc)
                #st.write(str(normalized_parent[0][0]))

                user_input = user_input.replace(parent, str(normalized_parent[0][0]))
                #st.write(user_input)



        write_or_append(["QUESTION:"], 'codes.log')
        write_or_append(["QUESTION:"], 'results.log')
        write_or_append([user_input], 'codes.log')
        write_or_append([user_input], 'results.log')
        if user_input:
            if len(st.session_state.uploaded_file):
                
                st.session_state.uploaded_file = sorted(st.session_state.uploaded_file, key=lambda x:x['name'] if isinstance(x, dict) else x.name)
                st.session_state.display_history.append({"role": "user", "content": user_input})
                table = None


                # Response Logic
                return_code = True
                response = gpt_response(user_input, message_history=st.session_state.chat_history, return_code=return_code) 
                
                if return_code:
                    global_env = {'pd':pd}
                    executables = segment_code(response,usr_id=usr_id)
                    if len(executables)>0:
                        code = executables[0]
                        logging.info("Logging CODE\n"+code)
                        write_or_append(["\nCODE:"], 'codes.log')
                        write_or_append([code], 'codes.log')
                        write_or_append(["\n*************************************************\n"], 'codes.log')
                        
                        try:
                            table = execute(code, st.session_state.file_content)
                        except Exception as e:
                            # Loop until error is rectified
                            # logging.info("ERROR TRACEBACK - ", traceback.format_exc())
                            response, user_input, table = eval_loop(user_input, response, f"{str(type(e))} {e}", return_code=True)

                        # Check if 'table' is a dictionary
                    
                        if isinstance(table, dict):
                            # Convert the dictionary to a DataFrame
                            table = pd.DataFrame(table)
                        if table is not None:
                            write_or_append(["\nRESULT:"], 'results.log')
                            write_or_append([table.to_string(index=False)], 'results.log')
                            write_or_append(["\n*************************************************\n"], 'results.log')
                    
                # Update the history and display output
                
                st.session_state.chat_history.extend([{"role": "user", "content": user_input},{"role": "assistant", "content": response}]) # Add markdown of the result to response using -> + f"\n{dataframe_to_markdown(global_env['result'])}"
                st.session_state.display_history.append({"role": "assistant", "error": response, "table": table})
                st.session_state.user_input = ""  # Clear the input field
                # st.session_state.uploaded_file = None
                if table is not None:
                    write_or_append([user_input+"\n"], 'conversation.txt')
                    write_or_append([table[:100].to_string()+"\n\n"], 'conversation.txt')

            else:
                st.session_state.display_history.append({"role": "assistant", "plot": 0, "error": "Please upload the necessary files", "table": None})
                st.session_state.user_input = ""  # Clear the input field
        
            
                
        logging.info(st.session_state.display_history)
    


    for i, message in enumerate(st.session_state.display_history):  # Added enumerate to track message index
        if "desc" in message.keys():
            st.subheader(f"{message['desc']}")
        if "insight" in message.keys():
            st.markdown(f"{message['insight']}")
        if message["role"] == "user":
            st.markdown(f"{message['role']}: {message['content']}")
        elif message["role"] == "assistant" and (message["table"] is not None):
            # cols = list(message["table"].columns)

            # # Define start and end colors
            # start_color = "#E0F7FA"  # Light turquoise
            # end_color = "#006064"    # Dark turquoise

            # # Number of colors in the gradient
            # num_colors = 10

        
            # if isinstance(message["table"], pd.DataFrame):
            #     # Format numeric columns with commas
            #     for col in message["table"].select_dtypes(include=['number']).columns:
            #         message["table"][col] = message["table"][col].apply(lambda x: f"{x:,.0f}")

            #     cols = list(message["table"].columns)

            #     # Select x-axis and y-axis based on the user's choice
            #     x_axis = st.selectbox("Select X-axis", cols, index=0, key=f"x_axis{i}")
            #     updated_cols = [option for option in cols if option != x_axis]
            #     y_axis = st.selectbox("Select Y-axis", updated_cols, index=0, key=f"y_axis{i}")
            #     value_cols = [option for option in cols if option != x_axis and option != y_axis]
            #     value_axis = st.selectbox("Select Value", value_cols, index=0, key=f"value_axis{i}")

            #     # Create a Plotly bar chart
            #     if len(cols) > 2:
            #         # If we have a third column, use it for color mapping
            #         plot = px.bar(
            #             message["table"],
            #             x=x_axis,
            #             y=y_axis,
            #             color=value_axis,
            #             hover_data=[value_axis]
            #         )
            #     else:
            #         # If we only have two columns, use a single color for all bars
            #         plot = px.bar(
            #             message["table"],
            #             x=x_axis,
            #             y=y_axis,
            #         )
            #         # Update the bar color after creating the plot
            #         plot.update_traces(marker_color='#40E0D0')

            #     # Format the axes with commas
            #     plot.update_yaxes(tickformat=",.0f")
            #     plot.update_xaxes(tickformat=",.0f")

            #     # Use a unique key for the plot
            #     if 'plot_counter' not in st.session_state:
            #         st.session_state.plot_counter = 0
            #     st.session_state.plot_counter += 1
            #     unique_key = f"plot{x_axis}{y_axis}{st.session_state.plot_counter}"

            #     # Display the Plotly chart in Streamlit
            #     st.plotly_chart(plot, key=unique_key)

                # If you want to display the table as well (optional)
            table = dataframe_to_html(message['table'])

###########

            # collapsible_text = f"""
            # <details>
            #     <summary>Click to expand Table!</summary>
            #     <div style="height:300px; width:100%; overflow-y:scroll; overflow-x:scroll; border:1px solid #ccc; padding:10px;">
            #         {table}
            #     </div>
            # </details>
            # """
            collapsible_text = f"""
                <div style="max-height:300px; width:100%; overflow-y:auto; overflow-x:auto; padding:10px;">
                    {table}
                </div>
            """
            st.markdown(collapsible_text, unsafe_allow_html=True)
            st.markdown("&nbsp;")
            st.markdown("&nbsp;")
        else:
            st.markdown(f"**{message['role']}**: {message['error']}")
            

    store_json({"conversation": st.session_state.chat_history}, usr_id)


    if 'gen_button' in st.session_state:
        if st.session_state.gen_button:
                with st.spinner("Generating insights... This may take a moment."):
                    generate_overall_insights('conversation.txt')
                # st.session_state.gen_button = False


    if len(st.session_state.uploaded_file) > 0:

        # User input field
        st.text_input("Type your message here:", key="user_input")#, on_change=respond)

        # Send button
        st.button("Send", on_click=respond)

        # Add Generate Insights button
        st.button("Generate Insights", type="primary", key="gen_button")



        if st.button("Clear Session"):
            st.session_state["chat_history"] = []
            st.session_state.stop_index = 0









