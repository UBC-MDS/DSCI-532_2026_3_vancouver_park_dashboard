# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - (2026-02-28)

### Added
- Added Changelog to the repository updating everything until Tag v0.2.0
- Added a demo GIF to the README to visually showcase dashboard functionality for new users. (PR #46)
- Created dedicated documentation pages for both users and contributors, improving onboarding experience. (PR #46)
- Added a reactivity diagram to illustrate how dashboard inputs and outputs are connected. (PR #44)
- Added job stories to the milestone 2 proposal to better capture user needs and motivations. (PR #36)
- Added a rendered feature comparison table to the proposal documentation. (PR #34)
- Added a neighbourhood filter dropdown, allowing users to filter parks by neighbourhood. (PR #32)
- Added a count widget to display the number of parks matching the current filter selection. (PR #32)
- Added a pie chart to visualize the distribution of park facilities across the dataset. (PR #29)
- Added map output to the dashboard, rendering filtered parks as interactive points on a map. (PR #27)
- Added DataFrame filtering logic based on user selected facilities input. (PR #27)
- Added `requirements.txt` file to make dependency installation straightforward for new contributors. (PR #19)

### Changed
- Removed the 'Data Source' radio button input selector filter from the dashboard (PR #27).
- Added the direct park 'Search Bar' for user preferring direct search interactivity (PR #27).
- Removed the 'Search Specific Park' search bar input in favour of the structured neighbourhood dropdown filter for a more consistent UX. (PR #37)
- Updated lower and upper bound logic on the park size/area slider for more accurate and interactive filtering. (PR #28)
- Updated filtered DataFrame logic to correctly reflect combined filter selections across all active widgets. (PR #29)
- Converted the app from `shiny.express` syntax to standard `shiny` for better long-term compatibility and structure. (PR #23)
- Added two reference URLs to the README for improved context and navigation. (PR #46)
- Removed redundant information from documentation to keep content concise and focused. (PR #46)
- Added more required packages to the environment to support new dashboard features. (PR #19)

### Fixed
- Fixed an issue where the filtered DataFrame was not updating correctly when multiple filters were applied simultaneously. (PR #32)

### Known Issues
- No automated tests exist yet for the dashboard interactivity and reactive components.
- The app has not been deployed publicly; runs only on local.

### Reflection
- Milestone 2 significantly expanded the dashboard's interactivity, moving from a static map skeleton to a fully filterable, multi-widget interface.
- The conversion from `shiny.express` to `shiny` was an important early refactor that set a more stable foundation for adding subsequent features.
- Job Stories 1, 2, and 3 implemented along with better utilization of story 3.
- Comparing M1 sketch and M2 sketch, we tried to match our M1 mission and went on to direct M2 to focus more on user functionality, interactivity and practicality. 
---

## [0.1.0] - (2026-02-14)

### Added
- Completed full exploratory data analysis (EDA) including summary statistics and discussion of key findings. (PR #16)
- Added dashboard skeleton with an initial interactive map component, including a fix for a map fillable rendering issue. (PR #14)
- Added dashboard sketch to document the intended layout and component structure. (PR #8)
- Finalized project proposal document outlining goals, dataset, and planned features. (PR #15)
- Updated README with project description, function details, and setup instructions. (PR #18)
- Created the conda environment file with all required packages for the project. (PR #4)

### Changed
- Set up and refined the base repository file structure to follow project conventions. (PR #8)
- Updated license with correct author names. (PR #8)
- Wrote `CONTRIBUTING.md` with guidelines for contributors, including GenAI attribution requirements. (PR #8)
- Filled in `CODE_OF_CONDUCT.md` with community standards and expectations. (PR #8)
- Added repository metadata including description, topics, and relevant configuration. (PR #8)

### Fixed
- Fixed a map fillable rendering issue in the initial dashboard skeleton that prevented the map from displaying correctly. (PR #14)

### Known Issues
- Dashboard interactivity is minimal at this stage — filters, widgets, and reactive outputs are not yet implemented.

### Reflection
- This milestone focused on laying a solid foundation: the repository structure, environment, EDA, and proposal are all in place.
- The initial map skeleton, while basic, validated that the core geographic rendering approach was feasible before building further features on top.

---

### Added
- Initial commit — repository created and base structure set up.
- Created first draft of the project, establishing folder layout and placeholder files.

### Known Issues
- No functionality implemented yet; repository contains structure and placeholders only.

---







# OLD BELOW

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - (2026-02-28)

### Added
- Added a demo GIF to the README to visually showcase dashboard functionality for new users. (PR #46)
- Created dedicated documentation pages for both users and contributors, improving onboarding experience. (PR #46)
- Added a reactivity diagram to illustrate how dashboard inputs and outputs are connected. (PR #44)
- Added job stories to the milestone 2 proposal to better capture user needs and motivations. (PR #36)
- Added a rendered feature comparison table to the proposal documentation. (PR #34)
- Added a neighbourhood filter dropdown, allowing users to filter parks by Vancouver neighbourhood. (PR #32)
- Added a count widget to display the number of parks matching the current filter selection. (PR #32)
- Added a pie chart to visualize the distribution of park facilities across the dataset. (PR #29)
- Added map output to the dashboard, rendering filtered parks as interactive points on a map. (PR #27)
- Added DataFrame filtering logic based on user-selected facilities input. (PR #27)
- Added `requirements.txt` file to make dependency installation straightforward for new contributors. (PR #19)

### Changed
- Added two reference URLs to the README for improved context and navigation. (PR #46)
- Removed redundant information from documentation to keep content concise and focused. (PR #46)
- Removed the 'Search Specific Park' free-text input in favour of the structured neighbourhood dropdown filter. (PR #37)
- Updated lower and upper bound logic on the park size/area slider for more accurate filtering. (PR #28)
- Updated filtered DataFrame logic to correctly reflect combined filter selections across all widgets. (PR #29)
- Added more required packages to the environment to support new dashboard features. (PR #19)

---
