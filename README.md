# A Statistical Test of Primary Directions in Predicting Violent Death

This repository contains the research code and data for the study **“A Statistical Test of Primary Directions in Predicting Violent Death: A Null Result,”** published in *Correlation — The Astrological Association Journal of Research in Astrology*, 38(2), 2026, pp. 89–102. Full text is available here: https://alexeyborealis.com/blog/primary-directions-study/

The repository documents the study design, the simplified model for selecting death-related primary directions, the statistical data of the study, and the scripts that reproduce every number published in the paper.

**The purpose of this repository is the reproducibility of the statistical analysis.** The statistical part is complete and self-contained: anyone can re-run the Monte Carlo test, the bootstrap estimation, and the power analysis on the published data files and obtain the paper's results exactly. The astronomical computation part is published in full except for one proprietary module, whose small interface is fully specified by the type stubs in `stubs/`, so that the omitted computation module can be independently reimplemented.

## 1. Purpose of the Repository

The repository provides:

* documentation of how the study was designed and how the samples were selected;
* the simplified astrological model of death-related primary directions, as it was used in the study;
* the statistical data files, preserved exactly as they were analyzed for the published paper;
* scripts that reproduce the published results, with the original seeds and settings;
* information needed for an independent implementation of the proprietary computation module;
* the study's original samples with natal chart data — the model code of this repository regenerates the paper's statistical data from them byte-exactly.

## 2. Research Question

The study examined whether primary directions — the classical technique of advancing the chart by the rotation of the celestial sphere — can, on their own (without corroboration from life context or other forecasting techniques), predict the timing of violent death better than chance. The study was retrospective — conducted on the charts of deceased people — and had no formal preregistration of the protocol.

## 3. Data

The study data are the natal charts of people who died a violent death with a known death date, drawn from Astro-Databank: birth years 1900–2025, "violent death" defined as an Astro-Databank event in the categories *Death by Accident* or *Death by Homicide*.

Of the 1,103 such charts in the source data, 1,102 were usable — the single excluded chart is the one whose recorded lifespan is zero (death on the date of birth).

The three data sets below correspond to the three stages of the study:

* an *a priori* pilot of 100 charts drawn randomly from the full pool of 1,102 eligible charts;
* the main test on 400 charts (the size selected by the study's power analysis); and
* the final analysis of all 1,102 eligible charts.

**Statistical data (the study's exact data).** The files

* `stat_analysis/p0_y-100-fixed.txt` (pilot, 100 rows)
* `stat_analysis/p0_y-400-fixed.txt` (400 rows)
* `stat_analysis/p0_y-max-fixed.txt` (1,102 rows)

contain, for each chart included in the original samples, the pair

* `p0` — the probability that death lands on a fatal direction by pure chance, and
* `y = 1|0` — an event label indicating whether death did or did not occur on a fatal direction.

These files are preserved exactly as they were analyzed for the published paper, and all published numbers are reproduced from them by the scripts in Section 6.

**Data provenance.** The samples published in this repository

* `samples/sample-100-violent-death-public.json`
* `samples/sample-400-violent-death-public.json`
* `samples/sample-max-violent-death-public.json`

are the study's exact samples — the same charts, in the same order, with the same birth and death data, from which the paper's statistical data were generated. The sample data were drawn once and never altered. 

**The malefic exception in the model.** Among the death-promissor rules, the paper lists an exception for malefic planets: any aspect of a malefic planet to a malefic house can signify death, regardless of the planet's celestial condition or the nature of the aspect. Since the present study examines violent death specifically, the model applies this exception — for zodiacal aspects to the house cusp — to Mars alone, the natural ruler of violent death: its aspects to the 8 house cusp are always counted, while the aspects of the remaining planets are filtered by their score. For antiscia, the exception is applied to both malefics, Mars and Saturn, which are exempt from the brightness filter.

**Known issue (data-leakage bug).** The paper states that the 400-chart stage was drawn excluding the pilot charts. In the original statistical data this exclusion did not take effect: 37 of the 100 pilot charts ended up in the main 400-chart test (there was a hidden bug in the code at the time of writing, which has since been fixed). Excluding those 37 charts shifts the p-value of the main 400-chart test from 0.11 to ≈ 0.07 — still above 0.05 — and the conclusions of the study stand.

This discovered data leakage is deliberately left unchanged in the `stat_analysis/p0_y-*-fixed.txt` files, for the full reproducibility of the paper's result.

**Data source and licensing.** The sample data are derived from Astro-Databank (astro.com) and are used under its research-use policy, with attribution: *Data source: Astro-Databank (astro.com), Rodden Rating system.* The Astro-Databank Rodden ratings are not part of the published sample records. Astro-Databank retains all rights to the underlying data.

## 4. The Astrological Model

The model that selects the directions for the statistical test — the *simplified model* — is contained in `direction_analysis/simplified_astro_model/`. In outline:

* **Technique.** Primary directions are computed in the Morinus tradition: a directed promissor is brought, by the rotation of the celestial sphere, to the circle of position of the significator according to the Regiomontanus computation. The circle of aspects is constructed as described in https://alexeyborealis.com/blog/circle-of-aspects/. The arc of direction is converted to time with the Naibod key: 365.24/360 ≈ 1.0146 years per degree of arc.

* **Significators of death.** The significators of the 8th house: the house cusp, the planets in the house, and the house ruler, taken by domicile only (exaltation is not used). Mars is added as the natural ruler of violent death.

* **Death promissors.** Aspects and antiscia of the planets become death promissors when their score reaches the threshold set by `BRIGHTNESS` in `params.py` (the value used for the study data is 3; see the note in that file). Scoring uses the classical essential dignities and debilities at the promissor's degree.

* **Activity period.** A direction is considered active within a tolerance of ±6 months (±180 days) around its date of perfection.

The parameters used for the study data are set in `direction_analysis/simplified_astro_model/params.py` and are listed in Section 7.

## 5. Chart Computation

Planetary and cuspal positions, and the arcs of direction, are computed by the `calc/` module — the computation engine of the Morinus astroprocessor (a commercial product; https://calc.morinus-astrology.com/), built on the Swiss Ephemeris (swisseph). **This module is proprietary and is not included in the repository.**

The engine interface consumed by the model is small — a `Sphere` object describing the positions of the planets and cusps on the celestial sphere, together with the computation of directions in the Morinus tradition — and is fully specified by the type stubs in `stubs/`.

The statistical layer (`stat_analysis/`) does not depend on the engine at all: it reads the `p0_y` data files and runs on numpy (CPU) or cupy (GPU, for speed), selected by `USE_GPU` in `stat_analysis/params.py`.

## 6. Reproducing the Analysis

The code runs in a virtual environment:

```bash
pipenv install
pipenv shell
```

**Statistical layer** (no `calc/` engine is needed — the scripts run on the published data files, with seeds and settings preserved in their original form). The model's main results are reproduced by the following commands:

```bash
# Pilot relative risk: RR = 1.154, 95% CI [0.930, 1.388]
python stat_analysis/estimate_r.py

# Final relative risk (1M bootstrap): RR = 0.990, 95% CI [0.922, 1.058]
python stat_analysis/estimate_r.py --file p0_y-max-fixed.txt --n-bootstrap 1000000

# Monte Carlo p-value on the 400-stage data: p = 0.1077 (GPU) / 0.107 (CPU)
python stat_analysis/estimate_p_value.py

# Power analysis: 34.0 / 57.0 / 72.7 / 83.8% at k = 100 / 200 / 300 / 400, stop at k = 400
python stat_analysis/estimate_power.py
```

**GPU acceleration.** The Monte Carlo and power-analysis scripts run on the GPU when `USE_GPU = True` in `stat_analysis/params.py` (the default) and a working CuPy installation is available; otherwise they fall back to NumPy on the CPU automatically, with a warning.

GPU runs need one component that the `cupy-cuda12x` wheel itself does not ship: the *headers* of the CUDA toolkit, which CuPy uses to compile its kernels on first use. The Pipfile therefore installs CuPy with its `ctk` extra — `cupy-cuda12x[ctk]`. Here `ctk` ("CUDA toolkit") is the *name* of a group of optional dependencies: it is written literally, not a placeholder to substitute. The extra pulls the CUDA runtime wheels from PyPI, headers included, so after the plain

```bash
pipenv install
```

above, GPU runs work out of the box — no system packages and no environment variables are needed. When installing with pip instead of pipenv, keep the extra and quote the whole specifier, since square brackets are special characters in the shell:

```bash
pip install 'cupy-cuda12x[ctk]'
```

If you prefer to use a CUDA toolkit already installed on the system (for example, the `nvidia-cuda-toolkit` package on Debian/Ubuntu), you can skip the `ctk` extra and instead point the `CUDA_PATH` environment variable at the toolkit root — the prefix whose `include/` subdirectory holds the headers (CuPy's default is `/usr/local/cuda`; on Debian/Ubuntu the package installs the headers into `/usr/include`, so the root is `/usr`).

## 7. Model Configuration

The parameters of the simplified model (`direction_analysis/simplified_astro_model/params.py`), as used for the study data:

| Parameter | Value | Meaning |
| --- | --- | --- |
| `IS_EVENT_FAVORABLE` | `False` | The directed event (death) is unfavourable |
| `HOUSE` | `7` | The 8th house (0-indexed) |
| `BRIGHTNESS` | `3` | The essential-score threshold at which an aspect/antiscion becomes a death promissor (the value the study data was generated with) |
| `NATURAL_RULER` | `4` | Mars, the natural ruler of violent death |
| `ALLOWANCES` | `[-6, 6]` | Active window: ±6 30-day months (±180 days) around the direction's date of perfection |

Statistical settings (seeds, grid, thresholds) are set in the corresponding scripts and in `stat_analysis/params.py`; the defaults reproduce the published analysis.

The per-planet zodiacal orbs are `ORBS = [18, 12, 8, 13, 6.5, 8, 7]` (Sun through Saturn) in `direction_analysis/simplified_astro_model/basic_astro_functions.py`. A zodiacal aspect to the house cusp is counted within the full orb of the aspecting planet, and a planet is treated as conjunct the cusp — and thus determined by that house — within half of its orb.

## License

The data and code in this repository are published under the Creative Commons Attribution 4.0 International license (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/. You are free to share and use this material for any purpose, provided that you give appropriate credit with a reference (link) to this repository.

This license applies to the research data, code, and documentation in this repository. It does not apply to the commercial software mentioned in the documentation (the Morinus astroprocessor), nor to the Astro-Databank data from which the sample data are derived; Astro-Databank retains all rights to it.

## Contact

**Alexey Borealis**
Astrologer, researcher, educator, and software developer

https://alexeyborealis.com/