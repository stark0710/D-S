# VTOL CAD Generation Framework

## VTOL CAD Generation Philosophy
CAD generation is the bridge between numerical sizing and structural fabrication. Automatically generating parametric 3D models enforces:
1. **Consistency by Design**: Wing chord lengths, fuselage battery bays, and motor tilt brackets adjust automatically when aerodynamics or weights shift.
2. **Manufacturing Readiness**: Designing with fastener patterns, clearance slots, and material volumetric properties to prevent downstream assembly mismatches.
3. **Collision & Interference Avoidance**: Ensuring that dynamic rotor tips clear wings (minimum 5 cm) and parts have zero overlapping volumes before sending designs to CNC or 3D printers.

---

## Parametric Modeling Methodology
Models are generated parametrically by defining dimensions as variables rather than hardcoded bounds:
- **Fuselage Bay Volume**: Sized based on battery cell packaging volumes and payload cameras dimensions.
- **Spar & Wing Profiles**: Interpolated chordwise from airfoil data curves and spans.
- **Motor Mounts**: Auto-positioned at coordinates derived from transition tilt mechanics and thrust lines.

---

## Assembly Hierarchy & Reference Geometry
- **Assembly Hierarchy**: Structured as:
  $$\text{Root Aircraft Assembly} \rightarrow \text{Wing Assembly, Fuselage Assembly, Tail Assembly, Motors, Batteries, Payloads}$$
- **Reference Geometry**: Generates Mean Aerodynamic Chord (MAC) lines, chord reference planes, lateral symmetry datums, and thrust vectors to align component parts cleanly.

---

## CAD Export Pipeline
Generated files can be converted and exported to industry formats:
- **STEP (.step) & IGES (.iges)**: Standard formats for CNC milling and import into SOLIDWORKS or Fusion 360.
- **Parasolid (.x_t)**: Native kernels.
- **STL (.stl) & 3MF (.3mf)**: Triangle meshes optimized for rapid prototyping/3D printing.
- **DXF (.dxf)**: 2D vectors for laser/waterjet sheet metal cuts.

---

## Validation Assumptions
The validator asserts:
- **Interference volumes**: Interferences between components must be $0.0\text{ mm}^3$ (collision-free).
- **Rotor clearance margins**: Actual clearances must meet or exceed minimum safety constraints (e.g. 50 mm).

---

## Extension Mechanism
To extend the framework:
1. **Create new CAD templates**: Update `geometry_generator.py` to add new custom mechanical parts (e.g. landing gears, sensor gimbals).
2. **Implement new output formats**: Extend `cad_exporter.py` to translate boundary representation (B-Rep) parameters to custom export definitions.
3. **Customize categories**: Create strategies implementing the `CADStrategy` interface in `cad_strategy.py` and register them in `cad_registry.py`.
