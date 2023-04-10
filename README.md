This is the database, listener, and matcher for Alt Viewer.

# Set-up

- [Obtain a service ID](https://census.daybreakgames.com/#devSignup)
- Create a `.env` file at the project root
  - Add `SERVICE_ID=s:YOUR-ID-HERE`
- Run `sudo scripts/create-container.sh` and `scripts/create-db.py`
  - `sh scripts/create-container.sh && python scripts/create-db.py`
  - This only needs to be done once. Use `scripts/run-db.sh` to start the database from now on
- If you want to populate the database with test data, run `scripts/populate.py`
  - The population data can be modified in `data/db/population.json`
