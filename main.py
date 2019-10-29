# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# +
from gssutils import *

scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
scraper

# +
dist = scraper.distribution(
    title='Entry clearance visas granted outside the UK data tables immigration statistics October to December 2017 volume 1'
)
book = dist.as_pandas()
sheet = book['vi_05']
# %run "Entry clearance visas granted by country of nationality(Vi_05).ipynb"
entry_1 = tidy.copy()

sheet = book['vi_01_q']
# %run "Entry clearance visa applications and resolution by category ( vi_01_q).ipynb"
entry_2 = tidy.copy()
entry_1.rename(columns={
    'Year': 'Period',
    'Country of nationality': 'HO Country of Nationality'}, inplace=True)
entry_1['Period'] = entry_1['Period'].astype(str)
entry_1.replace(
    {'Period': {r'([0-9]{4})': r'year/\1'}}, regex=True, inplace=True
)
for col in ['Application type', 'Applicant type', 'Application category', 'Resolution']:
    entry_1[col] = 'All'
# Todo: "World" or "Not UK"?
entry_2['HO Country of Nationality'] = 'Rest of world'
combined = pd.concat([entry_1, entry_2], sort=True)
combined['Measure Type'] = 'Count'
combined['Unit'] = 'Applications'
# -

# Use notation rather than label for codelists

for col in ['HO Country of Nationality', 'Applicant type', 'Application category',
            'Application type', 'Resolution']:
    combined[col] = combined[col].map(pathify)

# +
from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)

combined.to_csv(out / 'observations.csv', index=False)

scraper.dataset.family = 'migration'
scraper.dataset.theme = THEME['population']

with open(out / 'dataset.trig', 'wb') as metadata:
    metadata.write(scraper.generate_trig())
# -


