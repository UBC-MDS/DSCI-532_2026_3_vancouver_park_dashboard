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

A typical user of this dashboard is someone who wants to quickly find a park that matches their situation. For example, a person could be visiting a new neighbourhood and wants the nearest park to relax for a while, but they may specifically need accessibility and prefer a park with washrooms. In that moment, the user’s goal is not to “analyze data,” but to make a practical decision fast. This leads to our main question for the dashboard: how can we help the public filter and compare Vancouver parks based on location, size, and amenity availability in the simplest way? In other words, when a user is deciding where to go, the dashboard should help them narrow options confidently using the Yes/No features and park size, so they can pick a suitable park without spending time searching across multiple tools.

Overall, this project is meant to be practical and user-focused: a simple tool that helps Vancouver residents and visitors find the right park based on what they actually care about, without making them dig through complicated data or multiple websites.


