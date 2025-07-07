# axone-test

## Technical take-home test for axone data:

### Question 3:

    - code:
        - `extract.py` : parsers facebook, extracts posts and related images. specify `query` and `num_scrolls`
        - `transform.py`: removes duplicates from parsed data
        - `load_to_db`: load the data into a mongodb collection
        - `docker-compose.yaml`: for local mongodb setup

    - results:
        - the resulting csv has:
            - post_id
            - text
            - images of the post (if exists)

        - `images` contains the images scraped from each post
        - `data` contains the data parsed and cleaned
        - our parsing got around `650` posts and our cleaning gave `259` clean post for 150 scrolls



Result :

![Scraping Logs](static/scrape_logs.png)
![Collection](static/mongo.png)
![Logs](static/mongo_logs.png)



