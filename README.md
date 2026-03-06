# NYPD Shootings API 
A Flask-based REST API that provides access to NYPD shooting incident data from a CSV file.

### Installation
1. Clone the repository and navigate into the project folder
2. Create a virtual environment
3. Install dependencies in the requirements.txt

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

### 6. Add a User

**Method**: POST  

**Path**: `/api/users`

Adds a new user to the database.

#### Request Body (JSON)

```json
{
  "username": "Andy",
  "age": 38,
  "country": "USA"
}

Example Request:
curl -X POST http://127.0.0.1:5000/api/users \
-H "Content-Type: application/json" \
-d '{"username":"Andy","age":38,"country":"USA"}'

{
  "message": "User added"
}

### 7. Get User Statistics

**Method**: GET  

**Path**: `/api/users/stats`

Returns:
- the total number of users
- the average age of users
- the three countries with the most users

#### Example Request

http://127.0.0.1:5000/api/users/stats

#### Example Response

```json
{
  "number_of_users": 5,
  "average_age": 28.4,
  "top_countries": [
    ["USA", 2],
    ["China", 1],
    ["Italy", 1]
  ]
}

## Features Implemented

- Read CSV data using pandas
- Filtering by column
- Pagination (limit and offset)
- JSON and CSV output formats
- Retrieve single record by identifier
- Additional utility endpoints (sum, factorial)
- Add User to Database
- Access to their statistics (number of users, the average age, and the three countries with the most users).
