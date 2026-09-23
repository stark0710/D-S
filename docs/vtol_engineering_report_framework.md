# VTOL Engineering Report Framework

## VTOL Engineering Reporting Philosophy
Engineering documentation consolidates complex, multi-disciplinary sizing outputs into a structured, exportable format. Sizing a report:
1. **Ensures Accountability**: Compiles clear revision history trails, tracking document authors and update dates.
2. **Closes the Sizing Loop**: Generates a Requirements Traceability Matrix mapping design inputs directly to actual verified parameters.
3. **Serves Certification Authorities**: Outlines flight envelope bounds, safety margins, and structural features in compliance with regulatory bodies (FAA, EASA).

---

## Report Structure & Traceability Methodology
The generated document is structured as follows:
1. **Executive Summary**: Core metrics (takeoff weight, cruise range, status).
2. **Engineering Sections**: Wing configurations, fuselage bay dimensions, and propulsion parameters.
3. **Performance Sections**: Hover disk area loading, transition Schedules, and cruise limits.
4. **Verification & Optimization**: MTBF reliability, Pareto front curves, and sensitivity rates.
5. **CAD & Manufacturing**: Clearance fits, BOM hardware sheets, and unit costs.
6. **Appendices**: Reference math equations and revision logs.

The **Traceability Matrix** maps requirements IDs to verified performance actuals (e.g. `REQ_RANGE_15KM` linked to `Verified (Actual: 32.5 km)`).

---

## Exporters & Formats
The report exporter supports formatting sections into several file envelopes:
- **PDF**: Page layout margins (2.5 cm) and header logo styling for printing.
- **HTML**: Dynamic web pages.
- **Markdown & JSON**: Raw text representations for databases.
- **DOCX**: Editable office documents.

---

## Validation & Revision Handling
- **Section check**: Rejects reports missing critical chapters.
- **Traceability check**: Enforces that matrix tables are generated.
- **Revision Control**: Enforces set version tags (e.g., `v1.0`) and author metadata fields.

---

## Extension Mechanism
To extend the framework:
1. **Add new report sections**: Modify strategy classes in `report_strategy.py` to compile custom pages.
2. **Integrate new export writers**: Update `report_exporter.py` to pipe text arrays to other format engines (e.g., LaTeX).
3. **Extend constraints**: Adjust validation thresholds in `report_constraints.py` or modify rules inside `report_validator.py`.
