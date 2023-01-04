## Junior-Jobs API
___
> https://jun-jobs-api.online/

### Description

HTTP API which provide data about junior-vacancies.

### Installation

1. Clone repo: ``$ git clone https://github.com/seeu359/junior-jobs-api.git``
2. Go to the directory with code: ``$ cd junior-jobs-api``
3. Set the dependencies:
   1. If you're using poetry, run command: ``$ make p_install``
   2. Else: ``$ make install``
---
### Dependencies

| Library | Version |
|---------|---------|
| python  | 3.10    |
 | FastAPI| 0.88.0  | 
 | request | 3.8.3   | 
 | sqlalchemy | 1.4.44  |
 |uvicorn | 0.20.0  |
 |psycopg2 | 2.9.5   |
|fastapi-pagination | 0.11.1  |
---
### End-points

``GET /stat/{language}/`` - return array of stats by select language. Available languages:
1. Python
2. Php
3. Ruby
4. JavaScript
5. Java

``GET /stat/{language}/{compare_type}/`` - returns the comparison of today's vacancies with the number of vacancies depending on the type of comparison. Available comapre type:
1. week
2. month
3. 3month
4. 6month
5. year

Example request: ``https://jun-jobs-api.online/stat/python/week/``

Response: <a href="https://imgbb.com/"><img src="https://i.ibb.co/Pmt2M5c/week.png" alt="week" border="0"></a><br /><a target='_blank' href='https://imgbb.com/'>плакала на русском скачать бесплатно</a><br />

``GET /stat/{language}/custom/?date1={value}&date2={value}`` - logic is similar with regular request by compare type. First date must be less than second date for the gap will be correct. Otherwise will be raised exception. 

Request example:
``https://jun-jobs-api.online/stat/python/custom/?date1=2022-11-13&date2=2023-01-02``

Response: <a href="https://imgbb.com/"><img src="https://i.ibb.co/hgZ6VJL/custom.png" alt="custom" border="0"></a>

