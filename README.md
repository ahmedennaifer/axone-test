# axone-test

## Technical take-home test for axone data:

### Question 3:
    - `extract.py` : parsers facebook, extracts posts and related images. specify `query` and `num_scrolls`
    - `transform.py`: removes duplicates from parsed data
    - `load_to_db`: load the data into a mongodb collection
    - `docker-compose.yaml`: for local mongodb setup

Result :
![Collection](static/mongo.png)


