# OpenFDA Morphine Milligram Equivalent (MME) Scraper

The goal of this project was to calculate an MME factor for every known drug containing an Opioid ingredient.
We use data dumps from OpenFDA to scrape all drugs containing an Opioid and then calculate an MME factor using the CDC conversion rates.


## Data Sources
- [OpenFDA - US Food and Drug Administration Public Data]()
- [MME Conversion Rates - Centers for Disease Control]()

## Dependencies
- Python >= 3.6

## Execution
1. Download Drug Label dumps from [OpenFDA - [/drug/label]](https://open.fda.gov/downloads/#Human%20Drug%20Label) into the `./raw_data` directory
2. Execute `MME_Scraper.py`
3. Review parsed data and skipped drugs in `./py_exports` directory