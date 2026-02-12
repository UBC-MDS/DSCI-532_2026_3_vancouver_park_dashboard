from shiny.express import ui

ui.page_opts(title="Vancouver Park Dashboard", fillable=True)
with ui.sidebar(title="Filters"):
    ui.input_text("search", "Search Parks", placeholder="Enter keywords...")
    ui.input_select("area", "Select Park area", choices=["All", "Downtown"])
    ui.input_slider("size", "Hectair", 0.5, 40, [20, 40])
    ui.input_radio_buttons(
        "data_source", 
        "Data Source", 
        {"official": "Official Records", "user": "User Submitted"}
    )
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
 
    ui.input_selectize(
        "specific_park", 
        "Search Specific Park", 
        choices=["Stanley Park", "Queen Elizabeth Park", "Kitsilano Beach"]
    )
    ui.hr()
    ui.markdown("Adjust filters to update the charts.")

# with ui.card(full_screen=True):
#     ui.card_header("Card 2")

with ui.layout_column_wrap(width=1/2, fill=True):
        
    with ui.card():
        ui.card_header("Table of data")
            # Add table content here

    with ui.card():                
        ui.card_header("Bar chart")
            # Add chart content here

        # The 'width=1' here ensures the map spans both columns
    with ui.card(full_screen=True, fill=True, fillable=True, width="100px"):
        ui.card_header("Map")

