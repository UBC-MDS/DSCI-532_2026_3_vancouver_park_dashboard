<h1 align="center">Project Proposal: The Vancouver Park Dashboard</h1>

**Motivation and Purpose**

People in Vancouver look for parks in everyday situations, not just for “green space”. Someone might be walking around downtown and want the nearest park to sit for a bit, or a family might want a park with washrooms, or a group might be planning a small birthday and wants a park that’s large enough compared to other options. Right now, that kind of search usually means jumping between maps and long lists, and it’s not always obvious which park meets a specific need. This project is meant to make that process easier for the general public by letting people search parks based on simple requirements and immediately see the best options.

For this dashboard, the goal is straightforward: help users find parks and compare them quickly. The dashboard will focus on practical questions a normal person would ask, such as “which park is closest”, “which parks have washrooms”, “which ones are accessible”, and “how big is this park compared to others”. Instead of making users interpret raw tables or maps, the dashboard will turn the data into something visual and interactive so decisions can be made in a few clicks.

**Description of Data**

We will be visualizing the City of Vancouver Parks dataset, which contains 218 parks and 15 variables. Each park has associated variables that describe the following characteristics, which we believe will be helpful for users when searching for and comparing parks:
	•	Park identification and neighbourhood context (Name, NeighbourhoodName, NeighbourhoodURL)
	•	Park location for public lookup (StreetNumber, StreetName, GoogleMapDest)
	•	Park size (Hectare)
	•	Amenity availability (Y/N flags) (Washrooms, Facilities, SpecialFeatures, Accessibility)

As part of our EDA and data cleaning, we will remove fields that do not add value for a public facing park search experience: ParkID (internal identifier), Official and Advisories (not informative since they have a single value), and EWStreet and NSStreet (not needed since street and neighbourhood fields already provide enough location context). We will also combine StreetNumber and StreetName into a single Address field to make searching and reading park locations easier for users.

**Researching Components**

A typical user of this dashboard is a Vancouver resident or visitor who wants to quickly find a park that fits their situation. For example, someone might be in an unfamiliar neighbourhood and want the nearest park to relax for a while, but they may also need accessibility and prefer a park with washrooms. In practice, the user would open the app, apply a few filters (washrooms, accessibility, facilities, special features), check the map to see nearby options, and then use the park list to compare parks—especially by size—before choosing where to go.

This leads to the main question for the dashboard: how can we help the public search and compare Vancouver parks by location, size, and Y/N amenities in the simplest way possible? To support this, the app should allow users to (1) filter parks by amenities so they can find places that meet their needs, (2) compare parks by size when planning a small meetup or birthday, and (3) explore filtered parks on a map with clear details so they can decide quickly without switching between multiple tools.

The EDA addresses the second user story (compare park size). In the histogram, it can be shown that the size distribution is highly right-skewed. The vertical dashed line is located at the size of the selected park. By inspecting the visualization, we can see that the selected park size is together with the majority instead of being a large outlier. In the summary table, this selected park size is on the 70% percentile of all park sizes, which means its size exceeds roughly 70% of all parks. By this comparison, it can be concluded that this park is relatively large, though still being close to the majority.
