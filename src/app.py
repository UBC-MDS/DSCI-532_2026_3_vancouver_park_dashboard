from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px
from ipyleaflet import Map, Marker, WidgetControl
from ipyleaflet import Popup
from ipywidgets import HTML
import folium
from folium import Popup
import chatlas
from chatlas import ChatAnthropic
import os
from dotenv import load_dotenv
import json
import difflib

# read dataframe
parks_df = pd.read_csv("data/raw/parks.csv", sep=';')

# adding neighbourhood best match for random prompts
VALID_NEIGHBOURHOODS = sorted(parks_df["NeighbourhoodName"].dropna().unique().tolist())

def best_match_neighbourhoods(user_neighs, valid_neighs, cutoff=0.6):
    """
    Map user-provided neighbourhood strings to closest matches in valid_neighs.
    Returns a list of matched neighbourhood names (duplicates removed).
    """
    matched = []
    for n in user_neighs:
        if not n:
            continue
        n_str = str(n).strip()
        if n_str in valid_neighs:
            matched.append(n_str)
            continue
        guess = difflib.get_close_matches(n_str, valid_neighs, n=1, cutoff=cutoff)
        if guess:
            matched.append(guess[0])
    # unique, preserve order
    seen = set()
    out = []
    for x in matched:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# function to create a folium map with circle markers for each park
def folium_map(df):
    
    # create map centered around downtown Vancouver
    fmap = folium.Map(
        location=(49.275, -123.12),
        zoom_start=12,
        tiles="OpenStreetMap"
    )
    
    # create a circle marker at each park latitude and longitude
    for _, row in df.iterrows():
        coords = row["GoogleMapDest"]
        if pd.isna(coords):
            continue

        lat_str, lon_str = coords.split(",")
        lat, lon = float(lat_str), float(lon_str)

        # add a pop-up with the name of the park
        popup_html = f"""
            <b>{row['Name']}</b><br>
            Neighbourhood: {row['NeighbourhoodName']}<br>
            Size: {row['Hectare']} ha
        """
        
        # create circle marker
        folium.CircleMarker(
            location=(lat, lon),
            radius=6,
            color="#2e7d32",
            fill=True,
            fill_color="#2e7d32",
            fill_opacity=0.8,
            popup=Popup(popup_html, max_width=250)
        ).add_to(fmap)

    return fmap.get_root().render()

def get_vancouver_parks_info():
    """
    Retrieves the dataset of Vancouver parks. 
    Use this to answer questions about park names, hectares, 
    washrooms, and neighbourhoods.
    """
    return parks_df.to_dict(orient="records")

# Set up AI agent with chatlas
# read the GitHub token from .env file
# Initialize the chat agent with the appropriate model and token
load_dotenv() 
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found! Check your .env file.")

chat_agent = ChatAnthropic(
    model="claude-sonnet-4-0",
    api_key=api_key,
    system_prompt="""
    You are helping filter a pandas DataFrame named vancouver_parks.
    
    Return ONLY valid JSON (no markdown, no backticks, no explanation).
    Schema:
    {
        "name_contains": string or null,
        "neighbourhoods": list of strings or [],
        "hectare_min": number or null,
        "hectare_max": number or null,
        "flags": { "Washrooms": "Y"|"N"|null, "Facilities": "Y"|"N"|null, "SpecialFeatures": "Y"|"N"|null }
    }

    Rules:
    - Use only the fields in the schema.
    - If the user doesn’t specify something, use null (or [] for neighbourhoods).
    - Strings must be plain values (no regex).
    - Flags must be only Y, N, or null.
    - If unsure, set the field to null/[].

    Examples (JSON only):
    {"name_contains":"Stanley","neighbourhoods":[],"hectare_min":null,"hectare_max":null,"flags":{"Washrooms":null,"Facilities":null,"SpecialFeatures":null}}
    {"name_contains":null,"neighbourhoods":["Kitsilano"],"hectare_min":2,"hectare_max":null,"flags":{"Washrooms":"Y","Facilities":null,"SpecialFeatures":null}}
    """
)

# register the parks dataframe with the chat agent so it can be queried
chat_agent.register_tool(get_vancouver_parks_info)

# chat = ui.Chat(id="park_chat") # Moved this here
app_ui = ui.page_navbar(
    # original dashboard tab
    ui.nav_panel(
        "Standard Explorer",
        ui.layout_sidebar(
            # Sidebar with filters
            ui.sidebar(
                # Search input for parks
                ui.input_text("search", "Search Parks", placeholder="Enter keywords..."),
                
                # Dropdown for neighbourhood selection
                ui.input_selectize(
                    "neighbourhood", 
                    "Neighbourhood",
                    choices=sorted(parks_df['NeighbourhoodName'].dropna().unique().tolist()),
                    multiple=True
                ),

                # Slider for park size
                ui.input_slider("size", "Hectare", 
                                parks_df['Hectare'].min(), parks_df['Hectare'].max(), 
                                [parks_df['Hectare'].min(), parks_df['Hectare'].max()]),
                
                # Checkbox group for facilities
                ui.input_checkbox_group(
                    "facilities", 
                    "Select Facilities",
                    {
                        "Washrooms": "Washrooms", 
                        "Facilities": "Facilities", 
                        "SpecialFeatures": "Special Features"
                    },
                    selected=[]
                ),
                ui.hr(),
                ui.markdown("Adjust filters to update the charts."),
                title="Filters"
            ),
            ui.card(
                ui.card_header("Park Overview"),
                ui.layout_column_wrap(
                    ui.card(ui.card_header("Table of data"), ui.output_table("table_out")),
                    ui.card(ui.card_header("Washroom availability"), output_widget("washroom_chart")),
                    width=1/2, height=300
                ),
                ui.card(
                    ui.card_header("Map"), 
                    ui.tags.div(
                        {"style": "position: relative;"},
                        # create map output
                        ui.output_ui("park_map"),
                        ui.tags.div(
                            # add park count widget
                            ui.output_text("park_count"),
                            style=(
                                "position: absolute; top: 12px; right: 12px; z-index: 1000; "
                                "background: rgba(255, 255, 255, 0.8); border-radius: 7px; "
                                "padding: 6px 10px; font-weight: 600; "
                                "box-shadow: 0 1px 4px rgba(0,0,0,0.15);"
                            ),
                        ),
                    ),
                    full_screen=True
                )
            )
        )
    ),
    
    # AI power tab
    ui.nav_panel(
        "AI Query Chat",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### AI Assistant"),
                ui.input_text_area("chat_input", "Ask a question about the parks:", 
                                  placeholder="e.g., Show me parks in Kitsilano larger than 2 hectares with washrooms"),
                
                ui.input_action_button("ask_ai", "Query Data", class_="btn-primary"),
                ui.hr(),
                ui.download_button("download_ai_data", "Download Filtered Data"),
                title="AI Controls"
            ),
            # Added wrapped for Ai chat
            ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("Chat Log"),
                        ui.chat_ui("park_chat")
                    ),
            # ---
                    # ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("AI Filtered Data"),
                        ui.output_ui("ai_table_out")
                    ),
                    ui.layout_column_wrap(
                        ui.card(
                            ui.card_header("Distribution by Neighbourhood"),
                            output_widget("ai_bar_chart")
                        ),
                        ui.card(
                            ui.card_header("Washroom Stats (AI Filtered)"),
                            output_widget("ai_washroom_pie")
                    ),
                    width=1/2
                ),
                # Added Map UI for AI interface
                ui.card(
                    ui.card_header("AI Map"),
                    ui.tags.div( {"style": "position: relative;"},
                                ui.output_ui("ai_park_map"),
                                ui.tags.div(
                                    ui.output_text("ai_park_count"),
                                    style=(
                                        "position: absolute; top: 12px; right: 12px; z-index: 1000; "
                                        "background: rgba(255, 255, 255, 0.8); border-radius: 7px; "
                                        "padding: 6px 10px; font-weight: 600; "
                                        "box-shadow: 0 1px 4px rgba(0,0,0,0.15);"
                                    ),
                                ),
                    ), full_screen=True
                ),
                # ---
                width=1
            )
        )
    ),
    title="Vancouver Park Dashboard",
    id="main_tabs"
)


def server(input, output, session):
    
    # Original Dashboard Reactive Logic
    # Reactive expression to filter the parks data frame based on user inputs
    
    chat = ui.Chat(id="park_chat") # Moved this here

    @reactive.calc
    def filtered():
        """
        Filter once for all outputs
        """
        # create a copy of the parks data frame to apply filters on
        filtered_df = parks_df.copy()

        # filters the parks data frame for park name search
        if input.search():
            filtered_df = filtered_df[filtered_df['Name'].str.contains(input.search(), case=False, na=False)]

        # filters the parks data frame for neighbourhood selection
        if input.neighbourhood():
            filtered_df = filtered_df[filtered_df['NeighbourhoodName'].isin(input.neighbourhood())]
        
        # filters the parks data frame whose Hectare size is within slider range
        min_size, max_size = input.size()
        filtered_df = filtered_df[
            (filtered_df['Hectare'] >= min_size) &
            (filtered_df['Hectare'] <= max_size)
        ]
        
        # filters the parks data frame for facilities selection
        for facility in input.facilities():
            filtered_df = filtered_df[filtered_df[facility] == 'Y']

        return filtered_df

    # Added filtered df for Ai output
    ai_filtered_df = reactive.Value(parks_df)
    @reactive.calc
    def ai_filtered():
        return ai_filtered_df()
    # ---
    
    @render.ui
    def table_out():
        df = filtered()
        
        display_df = pd.DataFrame({
            'Name': df['Name'],
            'Address': df['StreetNumber'].astype(str) + ' ' + df['StreetName'],
            'Neighbourhood': df['NeighbourhoodName'],
            'URL': df['NeighbourhoodURL'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
            })
        return ui.HTML(display_df.to_html(escape=False, index=False))
        
    @render.ui
    def park_map():
        df = filtered()
        html_str = folium_map(df)
        
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 50vh; width: 100%; border: none;"
        )
        
    @render.text
    def park_count():
        return f"Park Count: {len(filtered())}"
    
    @render_widget
    def washroom_chart():
        df = filtered()
        
        # calculate total number of washrooms per neighbourhood across ALL parks
        all_counts = parks_df[parks_df['Washrooms'] == 'Y'].groupby('NeighbourhoodName').size().reset_index(name='Count')
    
        # extract selected neighbourhoods from the drop-down input
        selected = list(input.neighbourhood())
    
        # color: light red if selected (or none selected), grey otherwise
        all_counts['Color'] = all_counts['NeighbourhoodName'].apply(
            lambda n: '#90caf9' if (not selected or n in selected) else '#bdbdbd'
        )
    
        # average washroom counts across all parks
        avg = all_counts['Count'].mean()
    
        # plot a bar chart
        fig = px.bar(
            all_counts,
            x='NeighbourhoodName',
            y='Count',
            labels={'NeighbourhoodName': 'Neighbourhood', 'Count': 'Total Washrooms'},
        )
    
        fig.update_traces(marker_color=all_counts['Color'])
    
        # add horizontal dotted average line
        fig.add_hline(
            y=avg,
            line_dash="dot",
            line_color="#ef9a9a"
        )
    
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_tickfont=dict(size=6.5),
            xaxis_title_font=dict(size=12),
            yaxis_title_font=dict(size=12)
        )
    
        return fig

    # AI dashboard
    # AI Reactive Logic
    # 1. Setup the Chat object (Native Shiny)
    
    # Reactive value to store the dataframe for the AI tab
    # This keeps it separate from your manual filters


    # ai_filtered_df = reactive.Value(parks_df)
    # chat = ui.Chat(id="park_chat")

    # 2. Trigger AI when the "Query Data" BUTTON is clicked
    @reactive.effect
    @reactive.event(input.ask_ai)
    async def handle_button_query():
        user_msg = input.chat_input()
        
        # Check if the input is actually there
        if not user_msg or user_msg.strip() == "":
            await chat.append_message("⚠️ Please type a question before clicking Query.")
            return

        # Show the user's message in the UI so you can see it working
        await chat.append_message({"role": "user", "content": user_msg})

        # Send to AI
        try:
            response = chat_agent.chat(user_msg)
            raw = str(response).strip().replace("```", "").strip()

            # Parse JSON from model
            try:
                spec = json.loads(raw)
            except Exception:
                await chat.append_message({"role": "assistant", "content": f"⚠️ AI did not return valid JSON.\nGot:\n{raw}"})
                return

            new_df = parks_df.copy()

            # 1) Name contains (case-insensitive)
            name_contains = spec.get("name_contains")
            if name_contains:
                new_df = new_df[new_df["Name"].str.contains(str(name_contains), case=False, na=False)]

            # 2) Neighbourhoods (best-match)
            user_neighs = spec.get("neighbourhoods") or []
            matched_neighs = best_match_neighbourhoods(user_neighs, VALID_NEIGHBOURHOODS, cutoff=0.6)
            if matched_neighs:
                new_df = new_df[new_df["NeighbourhoodName"].isin(matched_neighs)]

            # 3) Hectare range
            hmin = spec.get("hectare_min")
            hmax = spec.get("hectare_max")
            if hmin is not None:
                new_df = new_df[new_df["Hectare"] >= float(hmin)]
            if hmax is not None:
                new_df = new_df[new_df["Hectare"] <= float(hmax)]

            # 4) Flags (Y/N)
            flags = spec.get("flags") or {}
            for col in ["Washrooms", "Facilities", "SpecialFeatures"]:
                val = flags.get(col)
                if val in ("Y", "N"):
                    new_df = new_df[new_df[col] == val]

            ai_filtered_df.set(new_df)

            # Tell user what we matched
            msg = f"Filtered to {len(new_df)} parks."
            if user_neighs and matched_neighs:
                msg += f"\nMatched neighbourhoods: {matched_neighs}"

            await chat.append_message({"role": "assistant", "content": msg})

        except Exception as e:
            await chat.append_message({"role": "assistant", "content": f"Connection/Error: {str(e)}"})



        # try:
        #     # Note: response = chat_agent.chat(...) is synchronous in chatlas
        #     response = chat_agent.chat(user_msg)
        #     ai_text = str(response) # Use str() to get the text content clearly

        #     # Attempt to filter
        #     try:
        #         new_df = parks_df.query(ai_text)
        #         ai_filtered_df.set(new_df)
        #         await chat.append_message(f"Filtered to **{len(new_df)}** parks using: `{ai_text}`")
        #     except:
        #         # If it wasn't a query, just show the text
        #         await chat.append_message(ai_text)
                
        # except Exception as e:
        #     await chat.append_message(f"Connection Error: {str(e)}")
    
    # Commented. Code added towards the end. Code kept for future refernce. Can remove before update.
    # render function
    # @render.data_frame
    # def ai_table_out():
    #     """Displays the AI-filtered dataframe"""
    #     return render.DataTable(ai_filtered_df())

    # Commented. Code added towards the end. Code kept for future refernce. Can remove before update.

    # @render_widget
    # def ai_bar_chart():
    #     """Visualization 1: Bar chart of Park Sizes"""
    #     df = ai_filtered_df()
    #     if df.empty: return px.scatter(title="No data found")
    #     return px.bar(df, x='Name', y='Hectare', color='NeighbourhoodName', 
    #                   title="Park Sizes (AI Results)")

    # Commented. Code added towards the end. Code kept for future refernce. Can remove before update.
    # @render_widget
    # def ai_washroom_pie():
    #     """Visualization 2: Pie chart of Washrooms"""
    #     df = ai_filtered_df()
    #     if df.empty: return px.scatter(title="No data found")
    #     counts = df['Washrooms'].value_counts().reset_index()
    #     counts.columns = ['Status', 'Count']
    #     return px.pie(counts, names='Status', values='Count', 
    #                   title="Washroom Availability (AI Results)")

    @render.download(filename="vancouver_parks_ai_export.csv")
    def download_ai_data():
        """Download the data currently shown in the AI tab"""
        yield ai_filtered_df().to_csv(index=False)

    # AI rendered table output
    @render.ui
    def ai_table_out():
        df = ai_filtered()
        
        if df.empty:
            return ui.HTML("<p><b>No parks match your AI query.</b> Try a different prompt.</p>")
        
        display_df = pd.DataFrame({
            "Name": df["Name"],
            "Address": df["StreetNumber"].astype(str) + " " + df["StreetName"],
            "Neighbourhood": df["NeighbourhoodName"],
            "URL": df["NeighbourhoodURL"].apply(
                lambda x: f'<a href="{x}" target="_blank">{x}</a>' if pd.notna(x) else ""
                                            ),
        })
        
        return ui.HTML(display_df.to_html(escape=False, index=False))

    # AI rendered washroom pie chart
    @render_widget
    def ai_washroom_pie():
        df = ai_filtered()
        
        if df.empty:
            tmp = pd.DataFrame({"Category": ["No results"], "Count": [1]})
            return px.pie(tmp, names="Category", values="Count")
        
        counts = df["Washrooms"].value_counts(dropna=False).reset_index()
        counts.columns = ["Washrooms", "Count"]
        counts["Washrooms"] = counts["Washrooms"].map({"Y": "Yes", "N": "No"}).fillna("Unknown")

        return px.pie(
            counts,
            names="Washrooms",
            values="Count",
            color="Washrooms",
            color_discrete_map={"Yes": "darkgreen", "No": "lightgreen", "Unknown": "gray"}
        )

    # AI rendered map
    @render.ui
    def ai_park_map():
        df = ai_filtered()
        html_str = folium_map(df)
        
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 50vh; width: 100%; border: none;"
        )
    
    # AI rendered text for 'No results'
    @render.text
    def ai_park_count():
        df = ai_filtered()
        
        if df.empty:
            return "Park Count: 0 (No results)"
        return f"Park Count: {len(df)}"

    # Ai rendered bar chart
    @render_widget
    def ai_bar_chart():
        df = ai_filtered()
        
        if df.empty:
            tmp = pd.DataFrame({"NeighbourhoodName": ["No results"], "Count": [0], "Color": ["#bdbdbd"]})
            fig = px.bar(
                tmp,
                x="NeighbourhoodName",
                y="Count",
                labels={"NeighbourhoodName": "Neighbourhood", "Count": "Total Washrooms"},
            )
            fig.update_traces(marker_color=tmp["Color"])
            return fig

        # washrooms per neighbourhood
        all_counts = (
            df[df["Washrooms"] == "Y"]
            .groupby("NeighbourhoodName")
            .size()
            .reset_index(name="Count")
        )

        if all_counts.empty:
            tmp = pd.DataFrame({"NeighbourhoodName": ["No washrooms in results"], "Count": [0], "Color": ["#bdbdbd"]})
            fig = px.bar(
                tmp,
                x="NeighbourhoodName",
                y="Count",
                labels={"NeighbourhoodName": "Neighbourhood", "Count": "Total Washrooms"},
            )
            fig.update_traces(marker_color=tmp["Color"])
            return fig

        all_counts["Color"] = "#90caf9"

        # average washroom counts for AI results
        avg = all_counts["Count"].mean()

        fig = px.bar(
            all_counts,
            x="NeighbourhoodName",
            y="Count",
            labels={"NeighbourhoodName": "Neighbourhood", "Count": "Total Washrooms"},
        )

        fig.update_traces(marker_color=all_counts["Color"])

        fig.add_hline(
            y=avg,
            line_dash="dot",
            line_color="#ef9a9a",
        )

        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_tickfont=dict(size=6.5),
            xaxis_title_font=dict(size=12),
            yaxis_title_font=dict(size=12),
            )

        return fig

app = App(app_ui, server)
