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

# Table vi_01_q: Entry clearance visa applications and resolution by category

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
    sheet = scraper.distribution(
        title='Entry clearance visas granted outside the UK data tables immigration statistics October to December 2017 volume 1'
    ).as_pandas(sheet_name='vi_01_q')
sheet
# -

sheet.rename(columns=sheet.iloc[3], inplace=True)
sheet.drop([0,1,2,3], inplace=True)
sheet.drop(sheet.index[sheet['Quarter'] == ''], inplace=True)
sheet

# Let's consider the columns up to 'Category' to be the main dimensions, ignore the derived % calculations and collapse down the various types of applications under a 'Resolution' column:

tidy = pd.wide_to_long(
    sheet.drop(columns=['%']).rename(columns={'Applications': 'Applications All',
                    'Resolved': 'Applications Resolved',
                    'Granted': 'Applications Granted',
                    'Refused': 'Applications Refused',
                    'Withdrawn': 'Applications Withdrawn',
                    'Lapsed': 'Applications Lapsed'}),
                stubnames='Applications',
                i=['Quarter', 'Type', 'Broad category', 'Applicant type', 'Category'],
                sep=' ',
                suffix='.*',
                j='Resolution').reset_index()
tidy

# Consider `*Total` to be `All` and rename `Applications` to `Value`

tidy.replace(r'^\*Total', 'All', regex=True, inplace=True)
tidy.rename(columns={'Applications': 'Value'}, inplace=True)
tidy

# Turn the `Quarter` into a standard `Period`, e.g. quarter/2005-Q1

tidy.replace(
    {'Quarter': r'([0-9]{4}) (Q[1-4])'},
    {'Quarter': r'quarter/\1-\2'}, regex=True, inplace=True)
tidy.rename(
    columns={'Quarter': 'Period'}, inplace=True)
tidy

# Todo: data markers, `z` means `not applicable` and `:` means `not available`

import numpy as np
tidy.drop(tidy.index[~tidy['Value'].map(np.isreal)], inplace=True)
tidy['Value'] = tidy['Value'].astype(int)
tidy

# There are some labels that are the same but with different case or hyphenation in the `Category` column:

sorted(tidy['Category'].unique())

tidy.replace({
    'Category': {
        'All (excluding visitors and transit)': 'All (excluding Visitors and Transit)',
        'Tier 2 Dependant': 'Tier 2 - Dependant',
        'Tier 5 Dependant': 'Tier 5 - Dependant'
    }}, inplace=True)

# Category and broad category need to go into a codelist.

# +
unique_pairs = set(zip(tidy['Broad category'], tidy['Category']))

# Where category = 'All', the category should be the 'broad category'
unique_pairs = [(broad, cat if cat != 'All' else broad) for (broad, cat) in unique_pairs]

# does the category uniquely determine the broad category?
cat2broad = {}
for (broad, cat) in unique_pairs:
    if cat in cat2broad:
        assert cat2broad[cat] == broad, f'{broad} != {cat2broad[cat]}'
    else:
        cat2broad[cat] = broad
        
# assumption is ok, so work out a codelist

code2label = {'all': 'All'}
code2parent = {}

for broad in sorted(set(cat2broad.values())):
    if broad == 'All':
        continue
    if pathify(broad) in code2label:
        display(f"Warning: '{broad}' already in codelist as '{code2label[pathify(broad)]}'")
    else:
        code2label[pathify(broad)] = broad

for cat, broad in sorted(cat2broad.items()):
    if cat == 'All' or cat == broad:
        continue
    if pathify(cat) in code2label:
        display(f"Warning: '{cat}' already in codelist as '{code2label[pathify(cat)]}'")
    else:
        code2label[pathify(cat)] = cat
        code2parent[pathify(cat)] = pathify(broad)

codelist = [(code2label[code], code, code2parent.get(code, '')) for code in code2label.keys()]

codelist_df = pd.DataFrame.from_records(codelist,
                                       columns=('Label', 'Notation', 'Parent Notation'))
codelist_df['Sort Priority'] = codelist_df.index + 1
codelist_df['Description'] = ''
codelist_df

# +
# and write out the codelist and update the tidy table.

tidy['Application category'] = tidy.apply(
    lambda row: row['Category'] if row['Category'] != 'All' else row['Broad category'],
    axis=1)
tidy.drop(columns=['Category', 'Broad category'], inplace=True)

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)

codelist_df.to_csv(out / 'ho-application-categories.csv', index=False)

# Type -> Application type
tidy.rename(columns={'Type': 'Application type'}, inplace=True)
tidy
# -


