from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px
from ipyleaflet import Map, Marker, WidgetControl
from ipyleaflet import Popup
from ipywidgets import HTML
import folium
from folium import Popup

parks_df = pd.read_csv("data/raw/parks.csv", sep=';')

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

app_ui = ui.page_sidebar(
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

    # Main Content Area
    ui.card(
        ui.card_header("Park Overview"),
        
        # Top level, Table and Pie Chart
        # We use height=300 to ensure the top row doesn't crowd the map
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
        df = filtered()
        
        display_df = pd.DataFrame({
            'Name': df['Name'],
            'Address': df['StreetNumber'].astype(str) + ' ' + df['StreetName'],
            'Neighbourhood': df['NeighbourhoodName'],
            'URL': df['NeighbourhoodURL']
            })
        return display_df
        
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
            line_color="#ef9a9a",
            # annotation_text=f"Avg: {avg:.1f}",
            # annotation_position="top right"
        )
    
        fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_tickfont=dict(size=6.5),
            xaxis_title_font=dict(size=12),
            yaxis_title_font=dict(size=12)
        )
    
        return fig

app = App(app_ui, server)
