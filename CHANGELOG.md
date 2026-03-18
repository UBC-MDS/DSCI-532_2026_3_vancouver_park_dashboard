# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] - 2026-03-17

### Added
- Interactive bar chart output with click-to-filter functionality for washroom distribution visualization. (#92)
- Automatic map zoom feature that focuses on selected parks when filters are applied. (#121)

### Changed
- Changed functionality of "reset all filters" button to include resetting the selections made on the bar chart and table of data. (#124)
- Improved Standard Explorer & AI bar chart presentation with descending order sorting. (#124)
- Switched from lazy loading to DuckDB + ibis (PR: #94)
- Changed the layout of the dashboard by putting the map output on the top in both the Standard Explorer tab and AI tab (PR: #122)

### Fixed
- Fixed table and bar chart layout issues in the Standard Explorer to properly fit within UI cards. (#124)
- Removed unused AI pie chart code. (#124)
- **Feedback prioritization issue link:** #97

### Known Issues

### Release Highlight: Interactive Bar Chart for Facility Discovery

The dashboard now features an interactive bar chart visualization where users can directly click on bars representing washroom availability by neighborhood. This click-to-filter functionality seamlessly integrates with the existing filter system, allowing neighborhoods to be added to the active filter selection through intuitive chart interaction. This enhancement improves the discoverability of parks with specific facilities and provides an alternative interaction pattern to traditional dropdown menus.

- **Option chosen:** Component click event interaction
- **PR:** #92
- **Why this option over the others:** We chose the component click event interaction option and implemented an interactive bar chart and table row selection. We chose to implement these over other options because they deliver the most direct value to our target user in the Standard Explorer tab. Together, these two interactions form a cohesive workflow: users can click a bar in the washroom chart to filter by neighbourhood, then click a specific park in the table to zoom the map to its exact location. Option A (QueryChat Customization) would improve the AI tab experience, but based on our user needs, we think that park discovery based on amenities is better suited to direct visual exploration than natural language querying — users looking for "a park with washrooms nearby" are more likely to scan a chart than type a question. Options B (Persistent LLM Logging) and C (Custom RAG Knowledge Base) both require significant backend infrastructure and domain knowledge curation respectively, with benefits that are indirect and harder to validate within the scope of this milestone. We believe that both interactions that we implemented help close a genuine UX gap. Previously, the washroom chart was read-only and the map always showed all filtered parks at once, meaning users had to mentally cross-reference chart and map to find a specific park. The new interactions collapse that multi-step process into a single fluid workflow and allows the user to better explore the relationship between park amenities and locations.

### Collaboration

- **CONTRIBUTING.md:** Updates pending for M4 retrospective and collaboration norms.
- **M3 retrospective:** Focus shifted to refining user interactions and improving component layouts based on M3 feedback.
- **M4:** Emphasis on enhancing interactivity, optimizing layouts, and implementing automatic map behavior for better user experience.

### Reflection
Reflection
The dashboard excels at providing direct, intuitive exploration of Vancouver parks through layered filtering and visual feedback. The interactive bar chart where users click neighborhoods to filter parks creates a discovery workflow that integrates seamlessly with existing controls (dropdown, slider). By repositioning the map to the top, we've clarified the information hierarchy: the map shows the results, while the charts and tables guide the search. The addition of the automatic zoom-on-select behavior reduces cognitive load, allowing users to explore relationships between facilities, locations, and park details without toggling between views.

Current limitations: Our washroom bar chart aggregates binary values of whether or not a park has a washroom or not. This masks variation within areas and doesn't illustrate the total number of washrooms in a neighbourhood, but rather the number of parks that have at least one washroom. The LLM chat, while functional, remains a secondary discovery tool compared to direct visual filtering; without persistent logging or knowledge base customization (options B and C), it struggles to build context across queries.

Intentional deviations from DSCI 531 best practices: We prioritized interactive discovery over traditional dashboard design (see Release Highlight). Rather than a dashboard-as-report that presents pre-computed summaries, we built a tool for exploration, where user input directly shapes the map and chart. This shifts the design from "here are the key insights" to "here's your data; find your parks." This is intentional and aligns with our user personas (exploratory search, local planners) but means the dashboard requires engagement rather than supporting passive reading.

Feedback prioritization and trade-offs: We focused M4 on three critical items: clarifying the AI chat interface (one conversation thread, no sidebar duplication), repositioning the map for visual prominence, and making the outputs interactive (bar chart and table of data clickable). We deprioritized extending the washroom metric (e.g., washrooms-per-park) because it would require additional datasets and the current neighborhood view still allows users to understand the general distribution of washrooms across neighbourhoods. The full rationale is in issue #97: we chose visual interactivity over backend complexity, believing park discovery via clicking is more valuable than deeper facility metrics. We also decided not to prioritize feedback that was about visual aesthetics like the colours used in the dashboard as we felt this was more a matter of personal preference.

Most useful guidance: The M3 collaboration feedback (issue #57) helped reshape how we approached M4. We made specification updates before code (PR reviewing the m4_specifications before implementation), required review comments on all PRs above modest size, and rotated responsibilities so each team member touched multiple components. The lectures on geospatial visualization and LLMs were the most helpful in building out our dashboard.

## [0.3.0] - 2026-03-08

### Added
- Integrated LLM/AI features for enhanced user interactions. (#74, #75, #73)
- Added new dependencies including `anthropic` and `libsass` to support AI functionality and styling improvements. (#77, #78, #80)
- Created AI-powered features architecture including prompts framework. (#75, #73)
- Added a Shiny theme to dashboard UI to enhance visual hierarchy and cohesion. (#71, #79).

### Changed
- Migrated map component from `ipyleaflet` to `folium` for improved performance and compatibility. (#58)
- Updated environment packages and added `dotenv` for configuration management. (#76, #80)
- Refactored visualization: converted pie chart to comparison bar chart for better data representation and alignment with visualization best practices. (#67)
- Enhanced park details display: made URLs clickable in park information popup for improved usability. (#63)
- Improved dashboard styling and visual hierarchy: made dashboard title more visually prominent. (#66)

### Fixed
- Resolved map update issues when filtering was applied simultaneously. (#53)
- Fixed map rendering to properly reflect all active filter selections. (#58)

### Known Issues
- LLM features require active API configuration via `.env` file for full functionality.
- Limited automated testing for new AI components.

### Reflection
Milestone 3 marked a significant pivot toward integrating artificial intelligence capabilities into the dashboard. The addition of LLM/AI features represents an intentional deviation from traditional dashboarding, opting instead to provide intelligent assistance for park exploration and discovery. This decision reflects the evolving landscape of data applications where AI augmentation enhances user experience without replacing core visualization principles.

The refactoring of the pie chart to a comparison bar chart addressed peer feedback about data representation clarity. The migration from `ipyleaflet` to `folium` improved the dashboard's stability and extensibility. Moving forward, the dashboard now balances traditional BI best practices (clear visualizations, intuitive filtering) with modern AI-driven features (natural language assistance, smart recommendations) to create a more engaging park discovery tool.

Note: this entry was prepared with the assistance of GitHub Copilot.

## [0.2.0] - (2026-02-28)

### Added
- Added the changelog to document project changes up to version v0.2.0 (PR #49)
- Added a demo GIF to the README to show the dashboard in use. (PR #46)
- Created dedicated documentation pages for both users and contributors, improving onboarding experience. (PR #46)
- Added a reactivity diagram showing how dashboard inputs and outputs are connected. (PR #44)
- Added job stories to the milestone 2 proposal to better capture user needs and motivations. (PR #36)
- Added a rendered feature comparison table to the proposal documentation. (PR #34)
- Added a neighbourhood filter dropdown, allowing users to filter parks by neighbourhood. (PR #32)
- Added a count widget to display the number of parks matching the current filter selection. (PR #32)
- Added a pie chart to visualize the distribution of park facilities across the dataset. (PR #29)
- Added DataFrame filtering based on selected facilities. (PR #27)
- Added a direct park search bar. (PR #27)
- Added `requirements.txt` file for easier dependency setup. (PR #19)

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
- The app has not been deployed publicly, runs only on local.

### Reflection
- Milestone 2 significantly expanded the dashboard's interactivity, moving from a static map skeleton to a fully filterable, multi widget interface.
- The conversion from `shiny.express` to `shiny` was an important early refactor that set a more stable foundation for adding subsequent features.
- Job Stories 1, 2, and 3 are fully implemented along with better utilization of story 3.
- Comparing M1 sketch and M2 sketchs, we tried to match our M1 mission and went on to direct M2 to focus more on user functionality, interactivity and practicality. 
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
