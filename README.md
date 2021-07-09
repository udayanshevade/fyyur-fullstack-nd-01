## Fyyur

## Introduction

Fyyur is a musical venue and artist booking site that facilitates the discovery and bookings of shows between local performing artists and venues. This site lets you list new artists and venues, discover them, and list shows with artists as a venue owner.

- create new venues, artists, and shows.
- search for venues and artists.
- learn more about a specific artist or venue.

Project was completed as part of the Udacity Fullstack Nanodegree.

## Tech Stack (Dependencies)

### 1. Backend Dependencies

Our tech stack will include the following:

- **virtualenv** as a tool to create isolated Python environments
- **SQLAlchemy ORM** to be our ORM library of choice
- **PostgreSQL** as our database of choice
- **Python3** and **Flask** as our server language and server framework
- **Flask-Migrate** for creating and running schema migrations
  You can download and install the dependencies mentioned above using `pip` as:

```
pip install virtualenv
pip install SQLAlchemy
pip install postgres
pip install Flask
pip install Flask-Migrate
```

> **Note** - If we do not mention the specific version of a package, then the default latest stable package will be installed.

### 2. Frontend Dependencies

You must have the **HTML**, **CSS**, and **Javascript** with [Bootstrap 3](https://getbootstrap.com/docs/3.4/customize/) for our website's frontend. Bootstrap can only be installed by Node Package Manager (NPM). Therefore, if not already, download and install the [Node.js](https://nodejs.org/en/download/). Windows users must run the executable as an Administrator, and restart the computer after installation. After successfully installing the Node, verify the installation as shown below.

```
node -v
npm -v
```

Install [Bootstrap 3](https://getbootstrap.com/docs/3.3/getting-started/) for the website's frontend:

```
npm init -y
npm install bootstrap@3
```

## Main Files: Project Structure

```sh
├── README.md
├── flaskr.py *** The main directory for app files/folders
│   ├── controllers
│   │   ├── artists.py
│   │   ├── shows.py
│   │   ├── venues.py
│   ├── static *** Any static assets being served on the frontend
│   │   ├── css
│   │   ├── font
│   │   ├── ico
│   │   ├── img
│   │   └── js
│   ├── templates *** Jinja templates for rendering frontend content
│   │   ├── errors
│   │   ├── forms
│   │   ├── layouts
│   │   └── pages
│   ├── config.py *** Database URLs, CSRF generation, etc
│   ├── app.py *** Initializes the app
│   ├── db.py *** Initializes the database
│   ├── filters.py *** Defines any jinja filters
│   ├── forms.py *** Defines Form logic
│   ├── models.py *** Defines the SqlAlchemy Models
├── error.log
├── requirements.txt *** The dependencies we need to install with "pip3 install -r requirements.txt"
└── setup.py *** Optionally seeds the database
```

Overview:

1. Connecting to a local database in `flaskr/config.py`.
2. Using SQLAlchemy, generating normalized models for data.
3. Handling form submissions for creating new Venues, Artists, and Shows.
4. Handling controllers for listing venues, artists, and shows
5. Handling search for venues, artists, powering the `/search` routes.
6. Handling individual venue and artist detail pages, powering the `<venue|artist>/<id>` routes.

##### Things to add:

- Implement artist availability. An artist can list available times that they can be booked. Restrict venues from being able to create shows with artists during a show time that is outside of their availability.
- ~~Show Recent Listed Artists and Recently Listed Venues on the homepage, returning results for Artists and Venues sorting by newly created. Limit to the 10 most recently listed items.~~
- Implement Search Artists by City and State, and Search Venues by City and State. Searching by "San Francisco, CA" should return all artists or venues in San Francisco, CA.

## Development Setup

1. **Download the project starter code locally**

```
git clone https://github.com/udayanshevade/fyyur-fullstack-nd-01.git
cd fyyur-fullstack-nd-01
```

2. **Initialize and activate a virtualenv using:**

```
python -m virtualenv env
source env/bin/activate
```

> **Note** - In Windows, the `env` does not have a `bin` directory. Therefore, you'd use the analogous command shown below:

```
source env/Scripts/activate
```

3. **Install the dependencies:**

```
pip install -r requirements.txt
```

4. **Get the latest DB schemas:**

```
flask db migrate
```

5. **Populate the DB with seed data (optional):**

```
python setup.py
```

6. **Run the development server:**

```
export FLASK_APP=flaskr
export FLASK_ENV=development # enables debug mode
flask run
```

7. **Verify on the Browser**<br>
   Navigate to project homepage [http://127.0.0.1:5000/](http://127.0.0.1:5000/) or [http://localhost:5000](http://localhost:5000)
