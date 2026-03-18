from shiny import App, ui, render, reactive
from shinywidgets import render_widget, output_widget
import pandas as pd
import plotly.express as px
import folium
from folium import Popup
from chatlas import ChatAnthropic
from querychat import QueryChat
import os
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go
import ibis
from ibis import _


# load DuckDB connection
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "parks.parquet"
_ui_df = pd.read_parquet(DATA_PATH)

# con = ibis.duckdb.connect()
# parks = con.read_parquet(str(DATA_PATH))

# adding neighbourhood best match for random prompts
VALID_NEIGHBOURHOODS = (
    _ui_df["NeighbourhoodName"]
    .dropna()
    .sort_values()
    .unique()
    .tolist()
)

HECTARE_MIN = float(_ui_df["Hectare"].min())
HECTARE_MAX = float(_ui_df["Hectare"].max())

# # adding the maximum range of park size to be filtered later
# HECTARE_RANGE = (
#     parks.agg(
#         min_h=_.Hectare.min(),
#         max_h=_.Hectare.max() 
#     ).execute()
# )
# HECTARE_MIN = float(HECTARE_RANGE['min_h'][0])
# HECTARE_MAX = float(HECTARE_RANGE['max_h'][0])

def apply_dashboard_filters(expr, search_text="", neighbourhoods=None, size_range=None, facilities=None):
    if search_text:
        expr = expr.filter(_.Name.ilike(f"%{search_text}%"))

    if neighbourhoods:
        expr = expr.filter(_.NeighbourhoodName.isin(neighbourhoods))

    if size_range is not None:
        min_size, max_size = size_range
        expr = expr.filter((_.Hectare >= min_size) & (_.Hectare <= max_size))

    if facilities:
        for facility in facilities:
            expr = expr.filter(_[facility] == "Y")

    return expr

# function to create a folium map with circle markers for each park
def folium_map(df):
    # Default center if no valid coords
    default_location = (49.275, -123.12)
    default_zoom = 12

    # Filter rows with valid coordinates
    valid_rows = []
    for _, row in df.iterrows():
        coords = row["GoogleMapDest"]
        if pd.isna(coords):
            continue
        try:
            lat, lon = map(float, coords.split(","))
            valid_rows.append((lat, lon, row))
        except Exception:
            continue

    fmap = folium.Map(
        location=default_location,
        zoom_start=default_zoom,
        tiles="OpenStreetMap"
    )

    if valid_rows:
        lats = [r[0] for r in valid_rows]
        lons = [r[1] for r in valid_rows]

        if len(valid_rows) == 1:
            # Single park: center and zoom in closely
            fmap.location = [lats[0], lons[0]]
            fmap.zoom_start = 16
        else:
            # Multiple parks: fit the map to their bounding box
            fmap.fit_bounds(
                [[min(lats), min(lons)], [max(lats), max(lons)]],
                padding=[30, 30]  # pixels of padding around the bounds
            )

    for lat, lon, row in valid_rows:
        popup_html = f"""
            <b>{row['Name']}</b><br>
            Neighbourhood: {row['NeighbourhoodName']}<br>
            Size: {row['Hectare']} ha
        """
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

# Load API key before chat model initialization.
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found! Check your .env file.")

anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-0")

# parks_df_full = parks.execute()

# chat agent initialization with system prompt to guide user input parsing for filtering the parks dataframe
chat_agent = ChatAnthropic(
    model=anthropic_model,
    api_key=api_key,
        system_prompt="""
        You are helping filter a DataFrame of Vancouver parks.

        Return ONLY valid JSON (no markdown, no backticks, no explanation).
        Schema:
        {
            "name_contains": string or null,
            "neighbourhoods": list of strings or [],
            "hectare_min": number or null,
            "hectare_max": number or null,
            "flags": {
                "Washrooms": "Y"|"N"|null,
                "Facilities": "Y"|"N"|null,
                "SpecialFeatures": "Y"|"N"|null
            }
        }

        Rules:
        - If user doesn't specify a field, set null (or [] for neighbourhoods).
        - flags values must be only Y, N, or null.
        - Never return keys outside this schema.
        """,
)

qc = QueryChat(
    pd.DataFrame({"place_hoder": []}),  # empty placeholder
    "parks",
    id="park_chat_ui",
    greeting="",
    client=chat_agent,
    tools=("update", "query"),
)

# Initialize QueryChat with the full parks DataFrame and the chat agent
# qc = QueryChat(
#     parks_df_full,
#     "parks",
#     id="park_chat_ui",
#     greeting=(
#         "Hi! Ask me about Vancouver parks and I can filter the dashboard data for you. "
#         "For example: 'parks in Kitsilano larger than 2 hectares with washrooms'."
#     ),
#     client=chat_agent,
#     tools=("update", "query"),
# )

app_ui = ui.page_navbar(
ui.nav_panel(
    "Standard Explorer",
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_action_button("reset_all", "Reset all filters"),
            ui.input_text("search", "Search Park by Name", placeholder="Enter park name..."),
            ui.input_selectize(
                "neighbourhood", 
                "Neighbourhood",
                choices=VALID_NEIGHBOURHOODS,
                selected="Downtown",
                multiple=True
            ),
            ui.input_slider("size", "Hectare", 
                            HECTARE_MIN, HECTARE_MAX, 
                            [HECTARE_MIN, HECTARE_MAX]),
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
            title="Filters",
        ),
        # Flat layout_column_wrap, same structure as AI tab
        ui.layout_column_wrap(
            # Row 1: Map full width
            ui.card(
                ui.card_header("Map"), 
                ui.tags.div(
                    {"style": "position: relative;"},
                    ui.output_ui("park_map"),
                    ui.tags.div(
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
            ),
            # Row 2: Table + Chart side by side
            ui.layout_column_wrap(
                ui.card(
                    ui.card_header("Table of data"),
                    ui.output_data_frame("table_out"),
                    style="height: 300px; overflow-y: auto;"
                ),
                ui.card(
                    ui.card_header("Washroom Distribution by Neighbourhood"),
                    ui.tags.div(
                        output_widget("washroom_chart"),
                        style="width: 1200px; height: 100%;"
                    ),
                    style="height: 300px; overflow-x: auto; overflow-y: hidden;"
                ),
                width=1/2
            ),
            width=1
        )
    )
),
    
    # AI power tab
    ui.nav_panel(
        "AI Query Chat",
        ui.layout_sidebar(
            ui.sidebar(
                ui.markdown("### AI Assistant"),
                ui.markdown("Ask your question directly in the chat widget."),
                ui.hr(),
                ui.download_button("download_ai_data", "Download Filtered Data"),
                title="AI Controls"
            ),
            ui.layout_column_wrap(
                # Row 1: Chat Log full width
                ui.card(
                    ui.card_header("Chat Log"),
                    qc.ui(id="park_chat_ui"),
                    style="height: 400px;"
                ),
                # Row 2: Map full width
                ui.card(
                    ui.card_header("AI Map"),
                    ui.tags.div(
                        {"style": "position: relative;"},
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
                    ),
                    full_screen=True
                ),
                
                # Row 3: Table + Chart side by side (nested 50/50)
                ui.layout_column_wrap(
                    ui.card(
                        ui.card_header("AI Filtered Data"),
                        ui.output_data_frame("ai_table_out"),
                        style="height: 300px; overflow-y: auto;"
                    ),
                    ui.card(
                        ui.card_header("Washroom Distribution by Neighbourhood"),
                        ui.tags.div(
                            output_widget("ai_bar_chart"),
                            style="width: 1200px; height: 100%;"
                        ),
                        style="height: 300px; overflow-x: auto; overflow-y: hidden;"
                    ),
                    width=1/2
                ),
                width=1  # outer wrap is full width, controls Row 1 and Row 3
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
    con = ibis.duckdb.connect()
    parks = con.read_parquet(str(DATA_PATH))
    
    # Original Dashboard Reactive Logic
    session.on_ended(lambda: con.disconnect()) # clean up after leaving
    
#     VALID_NEIGHBOURHOODS = (
#     parks.select("NeighbourhoodName")
#     .distinct()
#     .execute()['NeighbourhoodName']
#     .dropna()
#     .sort_values()
#     .tolist()
#     )

# # adding the maximum range of park size to be filtered later
#     HECTARE_RANGE = (
#         parks.agg(
#             min_h=_.Hectare.min(),
#             max_h=_.Hectare.max() 
#         ).execute()
#     )
#     HECTARE_MIN = float(HECTARE_RANGE['min_h'][0])
#     HECTARE_MAX = float(HECTARE_RANGE['max_h'][0])
    
    parks_df_full = parks.execute()
    
    qc = QueryChat(
        parks_df_full,
        "parks",
        id="park_chat_ui",
        greeting=(
            "Hi! Ask me about Vancouver parks and I can filter the dashboard data for you. "
            "For example: 'parks in Kitsilano larger than 2 hectares with washrooms'."
        ),
        client=chat_agent,
        tools=("update", "query"),
    )

    # Reactive expression to filter the parks data frame based on user inputs
    @reactive.calc
    def filtered():
        """
        Filter once for all outputs
        """
        return apply_dashboard_filters(
            parks,
            search_text=input.search(),
            neighbourhoods=input.neighbourhood(),
            size_range=input.size(),
            facilities=input.facilities(),
        )

    selected_park_name = reactive.Value(None)

    @reactive.calc
    def final_filtered():
        # Apply the global selected park filter if a table row was clicked
        expr = filtered()
        name = selected_park_name()
        if name:
            expr = expr.filter(_.Name == name)
        return expr

    @render.data_frame
    def table_out():
        df = filtered().execute()
        
        display_df = pd.DataFrame({
            'Name': df['Name'],
            'Address': df['StreetNumber'].astype(str) + ' ' + df['StreetName'],
            'Neighbourhood': df['NeighbourhoodName'],
            'URL': [ui.HTML(f'<a href="{url}" target="_blank">{url}</a>') if pd.notna(url) else "" for url in df['NeighbourhoodURL'].tolist()]
            })
        return render.DataGrid(display_df, selection_mode="row", width="100%")

    @reactive.effect
    @reactive.event(input.table_out_selected_rows)
    def _row_clicked():
        idx = input.table_out_selected_rows()
        if idx:
            # Re-execute just the exact current filter block to match row indexes!
            df = filtered().execute() 
            name = df.iloc[idx[0]]['Name']
            selected_park_name.set(name)

    @render.ui
    def park_map():
        df = final_filtered().execute()
        html_str = folium_map(df)
        
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 50vh; width: 100%; border: none;"
        )
        
    @render.text
    def park_count():
        return f"Park Count: {final_filtered().count().execute()}"
    
    @render_widget
    def washroom_chart():
        # Override chart targeting if a park is selected
        target_neighbourhood = None
        if selected_park_name():
             target_neighbourhood = final_filtered().select("NeighbourhoodName").execute().iloc[0,0]

        # calculate total number of washrooms per neighbourhood across ALL parks
        all_counts = (
            parks.filter(_.Washrooms == "Y")
            .group_by("NeighbourhoodName")
            .agg(Count=_.count())
            .order_by(_.Count.desc())
            .execute()
        )
    
        # extract selected neighbourhoods from the drop-down input
        selected = list(input.neighbourhood())
        
        # If a park is selected via clicking, highlight ONLY its neighbourhood
        if target_neighbourhood:
            all_counts['Color'] = all_counts['NeighbourhoodName'].apply(
                lambda n: '#285F2A' if n == target_neighbourhood else '#bdbdbd'
            )
        else:
            # color: dark green if selected (or none selected), grey otherwise
            all_counts['Color'] = all_counts['NeighbourhoodName'].apply(
                lambda n: '#285F2A' if (not selected or n in selected) else '#bdbdbd'
            )
    
        # average washroom counts across all parks
        avg = all_counts['Count'].mean()
    
        # plot a bar chart
        fig = go.FigureWidget(
            data=[go.Bar(
                x=all_counts['NeighbourhoodName'],
                y=all_counts['Count'],
                marker_color=all_counts['Color'],
            )],
            layout=go.Layout(
                xaxis=dict(tickangle=-45, tickfont=dict(size=10), title="Neighbourhood"),
                yaxis=dict(title="Total Washrooms"),
                height=350,
                width=1200,
                shapes=[dict(
                    type='line', x0=0, x1=1, xref='paper',
                    y0=avg, y1=avg, yref='y',
                    line=dict(dash='dot', color='#ef9a9a')
                )]
            )
        )
    
        def on_click(trace, points, state):
            if points.point_inds:
                neigh = all_counts['NeighbourhoodName'].iloc[points.point_inds[0]]
                current = list(input.neighbourhood())
                if neigh not in current:
                    current.append(neigh)
                    ui.update_selectize("neighbourhood", selected=current)

        fig.data[0].on_click(on_click)
        
        return fig
    
    @reactive.effect
    @reactive.event(input.reset_all)
    def _reset_filters():
        # Reset selected line in table
        selected_park_name.set(None)
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
            value=[HECTARE_MIN, HECTARE_MAX]
        )
        # Reset facilities (none selected)
        ui.update_checkbox_group(
            "facilities",
            selected=[]
        )

    qc_vals = qc.server(id="park_chat_ui")

    @reactive.calc
    def ai_filtered_data():
        df = qc_vals.df()
        if isinstance(df, pd.DataFrame):
            return df
        if hasattr(df, "to_pandas"):
            return df.to_pandas()
        try:
            return pd.DataFrame(df)
        except Exception:
            return parks.limit(0).execute()

    @render.download(filename="vancouver_parks_ai_export.csv")
    def download_ai_data():
        """Download the data currently shown in the AI tab"""
        yield ai_filtered_data().to_csv(index=False)

    # AI rendered table output
    @render.data_frame
    def ai_table_out():
        df = ai_filtered_data()
        if df.empty:
            return render.DataGrid(pd.DataFrame({"Message": ["No results found."]}))
        
        display_df = df[["Name", "NeighbourhoodName", "Hectare", "Washrooms"]]
        return render.DataGrid(display_df, selection_mode="row")
    
    @reactive.effect
    @reactive.event(input.ai_table_out_selected_rows)
    def _ai_row_clicked():
        idx = input.ai_table_out_selected_rows()
        if idx:
            df = ai_filtered_data()
            name = df.iloc[idx[0]]['Name']
            selected_park_name.set(name)

    # AI rendered map
    @render.ui
    def ai_park_map():
        df = ai_filtered_data()
        html_str = folium_map(df)
        
        return ui.tags.iframe(
            srcdoc=html_str,
            style="height: 50vh; width: 100%; border: none;"
        )
    
    # AI rendered text for 'No results'
    @render.text
    def ai_park_count():
        df = ai_filtered_data()
        
        if df.empty:
            return "Park Count: 0 (No results)"
        return f"Park Count: {len(df)}"

    # Ai rendered bar chart
    @render_widget
    def ai_bar_chart():
        df = ai_filtered_data()

        target_neighbourhood = None
        if selected_park_name() and not df.empty:
            target_neighbourhood = df.iloc[0]['NeighbourhoodName']

        # calculate total washrooms per neighbourhood across ALL parks (same as washroom_chart)
        all_counts = (
            parks.filter(_.Washrooms == "Y")
            .group_by("NeighbourhoodName")
            .agg(Count=_.count())
            .order_by(_.Count.desc())
            .execute()
        )

        if all_counts.empty:
            tmp = pd.DataFrame({"NeighbourhoodName": ["No results"], "Count": [0], "Color": ["#bdbdbd"]})
            fig = px.bar(tmp, x="NeighbourhoodName", y="Count",
                        labels={"NeighbourhoodName": "Neighbourhood", "Count": "Total Washrooms"})
            fig.update_traces(marker_color=tmp["Color"])
            fig.update_layout(width=1200, height=350)
            return fig

        # extract neighbourhoods from AI-filtered results
        if df.empty:
            ai_neighbourhoods = set()
        else:
            ai_neighbourhoods = set(df["NeighbourhoodName"].unique())

        # highlight AI-matched neighbourhoods in green, grey out the rest
        if target_neighbourhood:
             all_counts["Color"] = all_counts["NeighbourhoodName"].apply(
                lambda n: "#285F2A" if n == target_neighbourhood else "#bdbdbd"
            )
        else:
            all_counts["Color"] = all_counts["NeighbourhoodName"].apply(
                lambda n: "#285F2A" if (not ai_neighbourhoods or n in ai_neighbourhoods) else "#bdbdbd"
            )

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
            xaxis_tickfont=dict(size=10),
            xaxis_title_font=dict(size=14),
            yaxis_title_font=dict(size=14),
            height=350,
            width=1200,
        )

        return fig
        

app = App(app_ui, server)
