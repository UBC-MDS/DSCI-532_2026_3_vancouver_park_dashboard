from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px
from ipyleaflet import Map, Marker
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
        ui.input_slider("size", "Hectare", 0, 40, [0, 40]),

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
        # filters the parks data frame for facilities selection
        filtered_df = parks_df.copy()
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

app = App(app_ui, server)
