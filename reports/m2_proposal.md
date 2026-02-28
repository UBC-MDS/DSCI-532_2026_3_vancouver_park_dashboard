<h1 align="center"> App Specification: The Vancouver Park Dashboard</h1>


**2.1 Updated Job Stories**

| # | Job Story | Status | Notes |
| :--- | :--- | :--- | :--- |
| **1** | When I am looking for a park that fits my needs, I want to filter parks by amenities such as washrooms, accessibility, facilities, and special features, so I can quickly find suitable options. | ✅ Implemented | Filters for "Facilities," "Washrooms," and "Special Features" are active in the sidebar. A pie chart dynamically updates to show washroom availability for the filtered set. |
| **2** | When I am planning a small meetup or birthday, I want to compare parks by size, so I can choose a park that has enough space. | ✅ Implemented | The **Hectare slider** allows users to filter parks by size, and the map popup shows each park’s size in hectares. This supports comparing parks based on space, although a direct size-sorting feature in the table is not explicitly coded beyond standard table display. |
| **3** | When I am in a new area or unfamiliar neighbourhood, I want to explore filtered parks on a map with clear details, so I can decide quickly without switching between multiple tools. | ✅ Implemented | Integrated `ipyleaflet` for a full-screen interactive map. Popups provide name, neighbourhood, and size details without requiring a separate page. |

---