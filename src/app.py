from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px
from ipyleaflet import Map, Marker, WidgetControl
from ipyleaflet import Popup
from ipywidgets import HTML

parks_df = pd.read_csv("data/raw/parks.csv", sep=';')

app_ui = ui.page_sidebar(
    # Sidebar with filters
    ui.sidebar(
        # Search input for parks
        ui.input_text("search", "Search Parks", placeholder="Enter keywords..."),

        # Dropdown for neighbourhood selection
        ui.input_selectize(
            "neighbourhood", 
            "Neighbourhood", 
            choices=["Downtown", "Kitsilano"],
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

        # Dropdown for specific park selection
        ui.input_selectize(
            "specific_park", 
            "Search Specific Park", 
            choices=["Stanley Park", "Queen Elizabeth Park", "Kitsilano Beach"]
        ),

        ui.hr(),
        ui.markdown("Adjust filters to update the charts."),
        title="Filters"
    ),

    # Main Content Area
    ui.card(
        ui.card_header("Park Overview"),
        
        # Top level, Table and Pie Chart
        # We use height=350 to ensure the top row doesn't crowd the map
        ui.layout_column_wrap(
            ui.card(
                ui.card_header("Table of data"),
                ui.output_table("table_out")
            ),
            ui.card(
                ui.card_header("Washroom availability"),
                output_widget("washroom_chart")
            ),
            width=1/2,
            height=300
            
        ),

        # Bottom level, Map for park location
        ui.card(
            ui.card_header("Map"),
            output_widget("park_map"),
            full_screen=True
        ),
        fill=True
    ),
    title="Vancouver Park Dashboard",
    fillable=True
)

def server(input, output, session):
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
    
    @render.table
    def table_out():
        # example table
        return pd.DataFrame({
            "Name": ["Stanley Park"], 
            "Neighbourhood": ["Downtown"], 
            "Address" : ["1234 Park Ave"], 
            "Email": ["info@stanley-park.com"]
        })
        
    @render_widget
    def park_map():
        df = filtered()

        # Center the map roughly on Vancouver
        m = Map(center=(49.2827, -123.1207), zoom=12)
        
        # Create a custom HTML widget to display the count of parks
        count_html = HTML(value=f"""
            <div style="
                background: rgba(255, 255, 255, 0.8); 
                backdrop-filter: blur(4px);
                padding: 10px; 
                border-radius: 8px; 
                border: 1px solid rgba(0,0,0,0.1);
                text-align: center; 
                min-width: 100px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            ">
                <div style="font-size: 10px; color: #444; font-weight: bold; letter-spacing: 1px;">COUNT</div>
                <div style="font-size: 24px; color: #2e7d32; font-weight: 800; line-height: 1;">{len(df)}</div>
            </div>
        """)
        
        # Add the control directly to the map object
        m.add_control(WidgetControl(widget=count_html, position='topright'))


        if df.empty:
            return m

        # Add a marker for each park
        for _, row in df.iterrows():
            coords = row['GoogleMapDest']
            if pd.isna(coords):
                continue
            
            lat_str, lon_str = coords.split(",")
            lat, lon = float(lat_str), float(lon_str)
            marker = Marker(
                location=(lat, lon),
                draggable=False,
            )
            popup = Popup(
                location=(lat, lon),
                child=HTML(f"""
                           <b>{row['Name']}</b><br>
                           Neighbourhood: {row['NeighbourhoodName']}<br>
                           Size: {row['Hectare']} ha
                           """),
                close_button=True,
                auto_close=False
                )
            marker.popup = popup
            m.add_layer(marker)
        return m
    
    @render_widget
    def washroom_chart():
        df = filtered()
        
        # count how many Y and N there are in df
        counts = df['Washrooms'].value_counts().reset_index()
        counts.columns = ['Washrooms', 'Count']
        
        # turn 'Y' to 'Yes' and 'N' to 'No'
        counts['Washrooms'] = counts['Washrooms'].map({
            'Y': 'Yes',
            'N': 'No'
        })
        
        # plot the pie chart
        pie = px.pie(
            counts, names='Washrooms', values='Count', color='Washrooms',
            color_discrete_map={
                "Yes": 'darkgreen',
                "No": 'lightgreen'
            }
        )
        
        return pie

app = App(app_ui, server)
