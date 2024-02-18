# URL Cutter

## Project description

URL Cutter is an app for shortening urls.

Application can be used without creating an account, but authenticated users can create custom short urls with custom validity date, and manage them in a dedicated panel. 

## Tech stack

- Python 3.8
- Flask
- MongoDB
- Docker

## Getting started

In the project directory, create _.env_ file and add the required values (you can see _.env.example_ file for reference).

Run `docker-compose up` to run the development server.

Open http://localhost:8000/ in your browser and see the results.

You can access the MongoDB admin console at http://localhost:8081/.
