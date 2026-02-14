from shiny.express import ui, input, render
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px

ui.page_opts(title="Vancouver Park Dashboard", fillable=True)

# create the side bar with filters
with ui.sidebar(title="Filters"):

    # Search input for parks
    ui.input_text("search", "Search Parks", placeholder="Enter keywords...")

    # Dropdown for neighbourhood selection
    ui.input_selectize(
        "neighbourhood", 
        "Neighbourhood", 
        choices=["Downtown", "Kitsilano"],
        multiple=True
    )

    # Slider for park size
    ui.input_slider("size", "Hectair", 0, 40, [0, 40])

    # Checkbox group for facilities
    ui.input_checkbox_group(
        "facilities",
        "Select Facilities",
        {
            "official": "Official",
            "washroom": "Washrooms",
            "facility": "Facility",
        },
        selected=["official", "washroom", "facility"] # Default selected options
    )
 
    # Dropdown for specific park selection
    ui.input_selectize(
        "specific_park", 
        "Search Specific Park", 
        choices=["Stanley Park", "Queen Elizabeth Park", "Kitsilano Beach"]
    )

    ui.hr()

    # info text
    ui.markdown("Adjust filters to update the charts.")

# create the main content area with charts and tables
with ui.card(fill=True):

    # header for the card
    ui.card_header("Park Overview")

    # layout for the charts and tables
    with ui.layout_column_wrap(width=1/2, height=1/2, fill=True):

        # table of data
        with ui.card():
            ui.card_header("Table of data")
            @render.table
            def table():
                return pd.DataFrame({
                    "Name": ["Stanley Park"], 
                    "Neighbourhood": ["Downtown"], 
                    "Address" : ["1234 Park Ave"], 
                    "Email": ["info@stanley-park.com"]
                    })
        # pie chart for washroom availability
        with ui.card():
            ui.card_header("Washroom availability")
            ui.markdown("Washroom availability content pie chart.")

    # Map for park location
    with ui.card(fill=True):
        ui.card_header("Map")
        ui.markdown("Map will be here, with the selected parks location.")

        
    