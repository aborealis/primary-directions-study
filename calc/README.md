# The `calc` module

This directory is a placeholder. The `calc` package — the computation
engine that produces planetary and cuspal positions and the arcs of
primary directions — is part of the **Morinus astroprocessor**, a
commercial product (https://calc.morinus-astrology.com/), and is not
distributed with this repository.

Everything the analysis needs from the engine is specified by the type
stubs in `stubs/calc/`. To run the full pipeline
(`stat_analysis/generate_stat_data.py`), place the proprietary `calc`
package in this directory; no other changes are needed.

An independent implementation of the same interface — for example with
pyswisseph and standard spherical trigonometry — is sufficient to
regenerate the statistical data from the published samples.