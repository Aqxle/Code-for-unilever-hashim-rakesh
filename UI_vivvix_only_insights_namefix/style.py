# Define the black and blue color palette
background_color = "#000000"  # Pure black
primary_gradient = "linear-gradient(135deg, #0077BE, #0056A1)"  # Blue gradient
accent_gradient = "linear-gradient(135deg, #008CFF, #0056A1)"  # Lighter blue gradient
text_color = "#FFFFFF"  # White for contrast
card_color = "#1A1A1A"  # Dark grey for card backgrounds
title_color = "#0077BE"  # Bright blue for the title

style =     f"""
        <style>
        /* Background Styling */
        .main {{
            background-color: {background_color};
            padding: 2rem;
        }}

        /* Card Styling */
        .main .block-container {{
            background-color: {card_color};
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0, 119, 190, 0.3);
        }}

        /* Title Styling */
        .stMarkdown h1 {{
            font-size: 3.5rem;
            font-weight: bold;
            color: {title_color};
            text-align: center;
            margin-bottom: 1rem;
            text-shadow: 3px 3px 5px rgba(0, 87, 161, 0.7);
        }}

        /* Subheading Styling */
        .stMarkdown h2, .stMarkdown h3 {{
            color: {text_color};
            font-weight: bold;
            text-align: center;
        }}

        /* Input Field Styling */
        .stTextInput > div > div > input {{
            background-color: white;
            color: black;
            border: 2px solid #0077BE;
            border-radius: 10px;
            padding: 0.8rem;
            font-size: 1rem;
            box-shadow: 0 2px 5px rgba(0, 119, 190, 0.2);
            transition: border-color 0.3s, transform 0.2s;
        }}
        .stTextInput > div > div > input:focus {{
            border-color: #008CFF;
            transform: scale(1.02);
        }}

        /* Button Styling */
        .stButton > button {{
            background: {primary_gradient};
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.7rem 1.5rem;
            font-size: 1.2rem;
            font-weight: bold;
            box-shadow: 0 4px 10px rgba(0, 119, 190, 0.4);
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.3s;
        }}
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0, 87, 161, 0.6);
            background: {accent_gradient};
        }}

        /* File Uploader Styling */
        .stFileUploader > div > div > input {{
            background-color: #333333;
            color: {text_color};
            border: 2px solid #0077BE;
            border-radius: 10px;
            padding: 0.8rem;
            font-size: 1rem;
            box-shadow: 0 2px 5px rgba(0, 119, 190, 0.2);
        }}

        /* Footer Styling */
        footer {{
            text-align: center;
            margin-top: 2rem;
            font-size: 0.9rem;
            color: {text_color};
        }}



        </style>
        """


