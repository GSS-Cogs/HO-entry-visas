# -*- coding: utf-8 -*-
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

# Vi_05 – Entry clearance visas granted by country of nationality

# +
from gssutils import *

if is_interactive():
    scraper = Scraper('https://www.gov.uk/government/statistics/immigration-statistics-october-to-december-2017-data-tables')
    sheet = scraper.distribution(
        title='Entry clearance visas granted outside the UK data tables immigration statistics October to December 2017 volume 1'
    ).as_pandas(sheet_name='vi_05')

sheet
# -

sheet.rename(columns=sheet.iloc[3], inplace=True)
sheet.drop([0,1,2,3], inplace=True)
sheet.drop(sheet.index[sheet['Geographical region'] == ''], inplace=True)
sheet

# +
tidy = pd.melt(sheet,
               ['Geographical region','Country of nationality'],
               var_name="Year",
               value_name="Value")

# Clean up *Total strings
tidy.replace({'Country of nationality': {
    r'^\*Total$': 'Rest of world',
    r'^\*Total ': ''
}}, regex=True, inplace=True)

# While nationality and citizenship are different things, can we use the same citizenship details
# derived from IPS?
from io import BytesIO
import requests
import re
citizenship_csv = 'https://raw.githubusercontent.com/ONS-OpenData/ref_migration/master/codelists/citizenship.csv'
citizenship = pd.read_csv(BytesIO(requests.get(citizenship_csv).content))

# See https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/734677/user-guide-immigration-statistics.pdf
# section 19 for more details.

#display(list(set(tidy['Country of nationality'].unique()) - set(citizenship['Label'].unique())))

# The names don't directly match and while some are obvious 1-1, others aren't (e.g. St. Maarten & St. Martin)
# So keep track of countries and areas to create a separate codelist, then drop the areas/regions from this
# tidy table as they're determined by nationality.

countries = set(tidy['Country of nationality'].unique())
parents = {}
for country in countries:
    regions = tidy[tidy['Country of nationality'] == country]['Geographical region'].unique()
    assert len(regions) <= 1
    if len(regions) == 1 and country != regions[0] and regions[0] != '*Total':
        parents[country] = regions[0]

codelist = [('World', 'world', '')]
for region in sorted(set(parents.values())):
    codelist.append((region, pathify(region), pathify('World')))
for country in sorted(countries - set(parents.values())):
    if country in parents:
        codelist.append((country, pathify(country), pathify(parents[country])))
    else:
        codelist.append((country, pathify(country), pathify("World")))

tidy.drop(columns=['Geographical region'], inplace=True)

from pathlib import Path
out = Path('out')
out.mkdir(exist_ok=True)
codelist_df = pd.DataFrame.from_records(codelist,
                                        columns=('Label', 'Notation', 'Parent Notation'))
codelist_df['Sort Priority'] = codelist_df.index + 1
codelist_df['Description'] = ''
if not codelist_df['Notation'].is_unique:
    display(codelist_df[codelist_df.duplicated('Notation', keep='first')])
    assert False, "Notation not unique for countries codelist"
codelist_df.to_csv(out / 'ho-country-of-nationality.csv', index=False)
# -

# Todo: data markers, `z` means `not applicable` and `:` means `not available`

import numpy as np
tidy.drop(tidy.index[~tidy['Value'].map(np.isreal)], inplace=True)
tidy['Value'] = tidy['Value'].astype(int)
tidy




