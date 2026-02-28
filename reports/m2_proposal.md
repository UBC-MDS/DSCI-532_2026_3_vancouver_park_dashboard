<h1 align="center">

App Specification: The Vancouver Park Dashboard

</h1>

**2.1 Updated Job Stories**

| \# | Job Story | Status | Notes |
|:-----------------|:-----------------|:-----------------|:-----------------|
| **1** | When I already have a target park to go, I want to search its name on the map and know its related details, so I can plan my trip to this specific park. | ✅ Implemented |  The target park can be searched in the search bar `Search Parks`. |
| **2** | When I have a target neighborhood in my mind, I want to search the available parks in this neighborhood, so I can plan my visit to the selected neighborhood. | ✅ Implemented |  The target neighborhood can be entered in the drop-down list `Neighbourhood`. |
| **3** | When I am looking for a park that fits my needs, I want to filter parks by amenities such as washrooms, accessibility, facilities, and special features, so I can quickly find suitable options. | ✅ Implemented | Filters for "Facilities," "Washrooms," and "Special Features" are active in the sidebar. A pie chart dynamically updates to show washroom availability for the filtered set. |
| **4** | When I am planning a small meetup or birthday, I want to compare parks by size, so I can choose a park that has enough space. | ✅ Implemented | The **Hectare slider** allows users to filter parks by size, and the map popup shows each park’s size in hectares. This supports comparing parks based on space, although a direct size-sorting feature in the table is not explicitly coded beyond standard table display. |
| **5** | When I am in a new area or unfamiliar neighbourhood, I want to explore filtered parks on a map and/or as a list with clear details, so I can decide quickly without switching between multiple tools. | ✅ Implemented | Integrated `ipyleaflet` for a full-screen interactive map. Popups provide name, neighbourhood, and size details without requiring a separate page. |

------------------------------------------------------------------------

**2.2 Component Inventory**

| ID | Type | Shiny widget \/ renderer | Depends on | Job story |
|----|------|--------------------------|------------|-----------|
| `search` | Input | `ui.input_text()` | NA | #1 |
| `neighbourhood` | Input | `ui.input_selectize()` | NA | #2 |
| `size` | Input | `ui.input_slider()` | NA | #4 |
| `facilities` | Input | `ui.input_checkbox_group()` | NA | #3 |
| `filtered_df` | Reactive calc | `@reactive.calc` | `search`, `neighbourhood`, `size`, `facilities` | #1, #2, #3, #4 |
| `table_out` | Output | `@render.table` | `filtered_df` | #5 |
| `washroom_chart` | Output | `@render_widget` | `filtered_df` | #3 |
| `park_map` | Output | `@render_widget` | `filtered_df` | #5 |
| `count_html` | Output (top right corner of the map) | `@render_widget` | `filtered_df` | #5 |
