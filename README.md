# dnd-5e-monster-maker

# What I built and who it's for
A tool for Dungeon Masters running Dungeons and Dragon's 5th Edition 2014 rules to find creatures, view their stats and abilities, and easily make custom monsters either from scratch or using other creatures as a base.

Making a homebrew monster for DnD from scratch can be a difficult and time consuming effort. This app makes that process easier by allowing the user to use aspects of other creatures as a base. 

- Search Functionality: Users can search for monsters and view their statblocks in detail, filtering by specific features such as creature types, sizes, condiiton immunities, challenge rating, damage immunities, or the environments in which they're found.
- References: Provides descriptions and other information on certain aspects of statblocks to help users know the correct choices to make.
- Custom Creature Creation: Allows the user to create and save a creature with custom stats and any combination of traits from existing creatures. Also allows the user to take the stats from another creature as a base, either as a starting point or to create a variant of that creature.

# The data
I utilised the Open5e API version 2 for this project. It is free, and requires no API key to use. The main bulk of the data I use comes from querying the creatures endpoint, but I also used data from the creaturetypes, damagetypes, languages, conditions, sizes, and environments endpoints.

All of these endpoints had to be filtered on either the document key "srd-2014" or the document gamesystem key "5e-2014" to ensure only data from the correct ruleset was used. 

One quirk worth noting was that the built in filtering on the creature type and damage type endpoints does not function correctly, so filtering had to be performed during data transformation using SQL instead. Additionally while the filtering did work on the conditions endpoint, the returned data was structured in such a way that additional filtering had to be done using SQL to remove more unwanted data.

Documentation: https://open5e.com/api-docs
API: https://api.open5e.com/v2/
# How it works
1. `api.py` extracts data from the API endpoints and stores them as json files. Data is not touched.
2. `create_db.py` performs 5 steps to transform the data correctly.
 i. `sqlCTAS.sql` is run, loading the raw jsons into the database, one row per record. Each endpoint has its own table. Then, it creates 2 additional tables from the `traits` and `actions` fields of the `creatures` table. The data in these tables is still not staged.
 ii. `sqlTables.sql` is run, creating al other tables in the database but not populating it with data yet. Fields, data types, and relationships are explicitly defined. Data is cleaned and structured.
 iii. `sqlParents.sql` is run, populating any tables that have no foreign keys. Any duplicates are removed and necessary filtering is performed.
 iv. `sqlDependants.sql` is run, populating the remaining tables that use foreign keys. Any duplicates are removed and the constraints and relationships are defined properly.
 v. `attackparsing.py` is run in order to populate the `CreatureActions` and `Attacks` tables. This has to be done using a python script as many attacks are missing important data fields and every attack has its damage type labelled as "Thunder" no matter what, so the app uses a script to read the description of the attacks and parses the correct information from it using pattern matching. It then uses this data to populate the tables correctly.
 3. `CCHome.py` is run as a streamlit app, using the page in `search.py` as its home page. The user can navigate to other pages contained in the other python files. `database.py` contains the database querying code used by the other pages, while `reference_page.py` contains a default blueprint shared by the `creaturetypes.py`, `damagetypes.py`, and `conditions.py` pages. All of the pages perform read only operations on the database, except for `createcreature.py` which performs a number of `INSERT` operations on various tables to save the creature.

sqlCTAS uses `CREATE OR REPLACE` for tables, rebuilding them every run. The largest amount of data comes from the creatures endpoints, which returns 325 results in total, so this is not particularly costly to do everytime.
sqlTables uses `CREATE IF NOT EXIST` for tables, only creating them on the first run of a fresh application. This is done as this file does not insert any data into the tables, so it simply ensures they exist for the files that do. The only issue that would arise with this is if a table's structure is changed, as this would require a fresh run to replace the old table. The creation and population of tables is done seperately to ensure that, on a fresh run, no errors occur due to a table trying to insert data or replace a table when a foreign key it references doesn't exist yet. 
sqlParents and sqlDependants both use `INSERT OR REPLACE` to insert data into the tables. This means that new data is added, and any data that has been updated since the last API pull is replaced with the updated version. The exceptions to these are `Attacks` and `TraitsFiltered`. Since these do not have an existing field to use as the primary key and DuckDB only allows for autoincrementing of values via sequences, they both have an additional `UNIQUE` contraint to prevent duplicates. This means they use an `INSERT INTO` with an `ON CONFLICT` clause that prevents the duplicate from being added.

# How to run it
'''
git clone https://github.com/jward1305/dnd-5e-monster-maker.git
cd dnd-5e-monster-maker
python -m venv .venv
source .venv/bin/activate  #or .venv/Scripts/activate
pip install -r requirements.txt

python api.py               #extract data
python create_db.py         #transform data
streamlit run app/CCHome.py #runs streamlitapp

'''
# What I would do next
- Allow users to create their own custom attacks, actions, and traits.
- Automaticlly calculate creature HP based on their Hit Die and Constitution score when creating.
- Automaticlly update trait and action descriptions to try and match the creature they are applied to.

# Where AI helped
AI was used in the form of VSCode's inline suggestions, which would automatically complete similar code or point out errors before runtime.