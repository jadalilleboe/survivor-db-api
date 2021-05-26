# survivor-db-api
Tools/Technologies used: Flask, Python, SQLite, SQLAlchemy, Postman, Selenium (for web scraping)

Database and API for the reality show Survivor (U.S. version only). I used selenium to scrape data from [the Surivor Wiki](https://survivor.fandom.com/wiki) about castaways who have been on the show, the show's seasons, and the tribes from each season. I then put that information in an SQLite database and built an API in flask to make requests from and to that database.

Check out the [Postman collection](https://www.postman.com/jlillebo/workspace/survivor-api/overview) and documentation to see the kind of requests this API is able to make.
