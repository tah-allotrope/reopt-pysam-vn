# REopt Vietnam: Project Walkthrough & Progress

### B. Branch Setup: `real-project-data`
A dedicated branch `real-project-data` was created to test the `REoptVietnam.jl` logic against actual project parameters from an Excel-based feasibility study.

### C. Analysis of Real Project Data
We analyzed a project dataset containing:
-   **System:** 3.2 MWp Solar, 2.2 MWh / 1 MW BESS.
-   **Tariff:** 22kV 2-component EVN tariff.
-   **Financials:** 20-year project lifetime, 20% CIT, 15% PPA discount.

**Identified Gaps:**
1.  **Missing 8760 Hourly Data:** The static Excel data provided annual yields, but REopt requires an **8760 hourly load profile (kW)** and **8760 solar generation profile** (or coordinates to fetch weather data).
2.  **Optimizer vs. Controller:** The user data included fixed BESS charge/discharge windows. REopt will instead **optimize** these windows based on the TOU tariff to maximize net present value (NPV), which may differ from the manual rules.
3.  **PPA Discounting:** We identified that the "15% discount to EVN tariff" must be pre-calculated by modifying the 8760 tariff series before optimization.

## 3. Current Thinking & Strategy
-   **Standardization:** Use `REoptVietnam.jl`'s `apply_vietnam_defaults!` as the source of truth for all Vietnam scenarios.
-   **Data-Driven:** Prioritize obtaining or synthesizing a realistic 8760 load profile to move from static Excel estimates to dynamic hourly optimization.
-   **Validation:** Use the `tests/cross_validate.py` tool to ensure that any custom project overrides don't break the consistency between the Julia and Python data layers.

## 4. Next Steps
1.  **Synthesize Load Profile:** Use REopt's `simulated_load` API to generate a representative 8760 load profile for the project.
2.  **Run Comparison Scenario:** Create a script in `scripts/julia/` that compares the 3.2 MWp / 2.2 MWh system results from REopt against the Excel feasibility study results.
3.  **Custom Constraint Exploration:** Investigate adding a custom JuMP constraint for the "20% generation export cap" if REopt's native wholesale rate settings aren't sufficient.
