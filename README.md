# NYPD Shootings API 
A Flask-based REST API that provides access to NYPD shooting incident data from a CSV file.

### Installation
1. Clone the repository and navigate into the project folder
2. Create a virtual environment
3. nstall dependencies in the requirements.txt

### Run the API
'python app.py'

The API will run locally at: http://127.0.0.1:5000

## API Documentation
### 1. Welcome

**Method**: GET
**Path**: /
#### Query Parameters: None

Returns a welcome message.
Example: http://127.0.0.1:5000/

### 2. Sum

**Method**: GET
**Path**: /sum

#### Query Parameters
- a (integer)
- b (integer)

Returns the sum of two integers in JSON format.
Example: http://127.0.0.1:5000/sum?a=3&b=4

### 3. Factorial

**Method**: GET
**Path**: /factorial
#### Query Parameters
- n (integer, optional, default = 10)
Returns n! in JSON format.

Example: http://127.0.0.1:5000/factorial?n=6

### 4. List NYPD Shooting Records

**Method**: GET
**Path**: /api/list
#### Query Parameters
- format — json or csv (default: json)
- filterby — column name to filter by
- filtervalue — value to filter
- limit — number of rows to return (default: 20)
- offset — starting row (default: 0)

#### Example Queries
- Return first 20 records (default):
http://127.0.0.1:5000/api/list

- Filter by borough:
http://127.0.0.1:5000/api/list?filterby=BORO&filtervalue=MANHATTAN

- Filter + limit + offset:
http://127.0.0.1:5000/api/list?filterby=BORO&filtervalue=MANHATTAN&limit=5&offset=2

- CSV output:
http://127.0.0.1:5000/api/list?format=csv

### 5. Retrieve Single Record

**Method**: GET
**Path**: /api/record/<INCIDENT_KEY>
#### Query Parameters
- format — json or csv (default: json)

Example:
http://127.0.0.1:5000/api/record/297623042

CSV format:
http://127.0.0.1:5000/api/record/297623042?format=csv

## Features Implemented

- Read CSV data using pandas
- Filtering by column
- Pagination (limit and offset)
- JSON and CSV output formats
- Retrieve single record by identifier
- Additional utility endpoints (sum, factorial)