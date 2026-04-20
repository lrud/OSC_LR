# Bureau of Tax and Economic Analysis - Quantitative Research Project

The Bureau of Tax and Economic Analysis is looking for an individual who can provide support on its quantitative research pertaining to issues facing New York City.

## Data Sources

- **New York State Department of Labor, Current Employment Statistics**
  - https://dol.ny.gov/current-employment-statistics-0
  - https://dol.ny.gov/statistics-ceszip ("ces.csv")

- **NYC OpenData, 311 Service Requests from 2010 to Present**
  - https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9

## Questions

### Question 1: NYS Department of Labor Employment Statistics

Using the New York State Department of Labor's employment statistics data for the latest available month:

**1a)** Discuss which major industries (by 2-digit NAICS) in New York City changed the most over the prior year. Describe possible reasons why these industries experienced greater change than other industries.

**1b)** How was the change that these industries experienced over the last year different from what they experienced over the last five years? Please include all analysis (calculations, tables, charts, etc.) in your response to this question.

### Question 2: NYC 311 Service Requests

Using NYC OpenData for 311 service requests:

**2a)** Using the API docs, pull and export only the following data. Please include the exact query that you used (in the form of https://...) in your response to this question.
1. `created_date` = all dates between 12/15/2021 and 3/15/2022
2. `agency_name` = New York City Police Department or Department of Housing Preservation and Development
3. `complaint_type` = noise or illegal parking

**2b)** Based on the data you pulled, how many complaints were there for each agency and complaint type? Please include all analysis (calculations, tables, charts, etc.) in your response to this question.

**2c)** Describe one way to visualize this data and include the visualization in your response. What do you want policymakers to know about your findings?

**2d)** Ask one research question about this data; discuss additional data that you would merge with this dataset to answer your question and write a simple equation that shows the relationship. Why is studying that relationship important for policymaking?
