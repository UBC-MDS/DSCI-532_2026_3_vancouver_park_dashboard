from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px
from ipyleaflet import Map, Marker, WidgetControl
from ipyleaflet import Popup
from ipywidgets import HTML
import folium
from folium import Popup
from chatlas import ChatOpenAI

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
            color="#285F2A",
            fill=True,
            fill_color="#285F2A",
            fill_opacity=0.8,
            popup=Popup(popup_html, max_width=250)
        ).add_to(fmap)

    return fmap.get_root().render()

# chat = ChatOpenAI()

parks_df = pd.read_csv("data/raw/parks.csv", sep=';')

app_ui = ui.page_navbar(
    # original dashboard tab
    ui.nav_panel(
        "Standard Explorer",
        ui.layout_sidebar(
            # Sidebar with filters
            ui.sidebar(
                # Search input for parks
                ui.input_text("search", "Search Park by Name", placeholder="Enter park name..."),
                
                # Dropdown for neighbourhood selection
                ui.input_selectize(
                    "neighbourhood", 
                    "Neighbourhood",
                    choices=sorted(parks_df['NeighbourhoodName'].dropna().unique().tolist()),
                    selected="Downtown",
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
                ui.markdown("Facilties may include playgrounds, soccer fields, tennis courts or field houses."),
                ui.markdown("Special Features may include exercise stations, gardens, picnic benches or perimeter walking paths."),
                ui.input_action_button("reset_all", "Reset all filters"),
                title="Filters",
            ),
            ui.card(
                ui.card_header("Park Overview"),
                ui.layout_column_wrap(
                    ui.card(ui.card_header("Table of data"), ui.output_table("table_out")),
                    ui.card(
                        ui.card_header("Washroom availability"),
                        ui.tags.div(
                            output_widget("washroom_chart"),
                            style="width: 1200px; height: 100%"
                        ),
                        style="overflow-x: auto; width: 100%; height:100%"
                    ),
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
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("AI Filtered Data"),
                    ui.output_data_frame("ai_table_out")
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
                    width=1
                ),
                width=1
            )
        )
    ),
    title="Vancouver Park Dashboard",
    id="main_tabs",
    theme=(ui.Theme("flatly")
    .add_defaults(primary="#285F2A",
                  secondary="#4d8a50",
                  background="#b1ceb1",
                  text="#2e2e2e")
    .add_rules("""
        h1 { letter-spacing: 0.05em; }

        /* navbar tab text color */
        .navbar-nav .nav-link {
            color: #95a395 !important;
            font-weight: 600;
        }

        /* active tab color */
        .navbar-nav .nav-link.active {
            color: #beccbe !important;
        }
        
        /* link color */
        a {
            color: #4d8a50;
            font-weight: 500;
        }
    """)
    )
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
    
    @render.ui
    def table_out():
        df = filtered()
        
        display_df = pd.DataFrame({
            'Name': df['Name'],
            'Address': df['StreetNumber'].astype(str) + ' ' + df['StreetName'],
            'Neighbourhood': df['NeighbourhoodName'],
            'URL': df['NeighbourhoodURL'].apply(lambda x: f'<a href="{x}" target="_blank">{x}</a>')
            })
        html_table = display_df.to_html(
            escape=False,
            index=False,
            classes="table table-striped table-hover table-sm"
            )
        return ui.HTML(html_table)
        
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
            lambda n: '#285F2A' if (not selected or n in selected) else '#bdbdbd'
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
            xaxis_tickfont=dict(size=10),
            xaxis_title_font=dict(size=14),
            yaxis_title_font=dict(size=14),
            height=260,   # slightly smaller than card height
            width=1200
        )
    
        return fig
    
    @reactive.effect
    @reactive.event(input.reset_all)
    def _reset_filters():
        # Reset search box
        ui.update_text("search", value="")
        # Reset neighbourhoods (default = Downtown)
        ui.update_selectize(
            "neighbourhood",
            selected=["Downtown"]
        )
        # Reset slider to full range
        ui.update_slider(
            "size",
            value=[parks_df['Hectare'].min(), parks_df['Hectare'].max()]
        )
        # Reset facilities (none selected)
        ui.update_checkbox_group(
            "facilities",
            selected=[]
        )

app = App(app_ui, server)
