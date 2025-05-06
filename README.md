# Portfolio Website API

This is the backend API for my online portfolio. This API includes a RESTful service for my projects, a login handler (redis session caching), and endpoints for uploading files to my GCS buckets.

## Configuration

Before the project can be built, the Google Cloud storage settings need to be configured in `app.py` and the database/redis settings must be set in a new file called `config.py`.

### Configuring `app.py`:

Find the variables `GCS_CV_BUCKET` and `GCS_CV_NAME` near the top of the module `app.py`. Set `GCS_CV_BUCKET` to a personal Google Cloud bucket that you wish to use for storing your CV/Resume and `GCS_CV_FILENAME`
configures the name to save them under.

### Configuring `config.py`:

In the root directory, create a python module called `config.py` and insert the following code:

```python
import redis

class ApplicationConfig:

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = "postgresql://username:password@your-database-endpoint:port"

    SESSION_TYPE = "redis"
    SESSION_PERMANENT = False
    SESSION_REDIS = redis.from_url("redis://your-redis-endpoint:port")

    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = False
```

There are many [configuration options](https://flask.palletsprojects.com/en/stable/config/) that can set in this file, but only `SQLALCHEMY_DATABASE_URI` and `SESSION_REDIS` must be set to valid endpoints before serving the application.

## Build Instructions

To run this server, a Google Cloud account is required. You will need a Google Cloud project id, a Google Cloud bucket set up, as well as your application default credentials JSON file.

Check https://cloud.google.com/docs/authentication/application-default-credentials for information on how to generate the credentials file.

After doing the configuration as described in the previous section, build the docker image:

```
docker build -t portfolio-api .
```
Next, save the default credentials file to the folder you will like to use as a volume for temporary storage and run the following command from that directory to start the server:

```
docker run 
-p 5000:5000 
-v .:/app/temp 
-e GOOGLE_APPLICATION_CREDENTIALS=/app/temp/[DEFAULT CREDENTIALS].json 
-e GCLOUD_PROJECT=[PROJECT ID] 
portfolio-api
```

## API

Postman collection of API calls can be forked from https://www.postman.com/gold-shadow-757137/workspace/portfolio-api

### 1. Login as Moderator

Request:
`POST /login`

Sample Body (JSON):
```json
{
    "username": "someusername",
    "password": "somepassword"
}
```
If the passed credentials are valid, the response of this request returns a session cookie that is needed for API calls that require elevation.

### 2. Logout as Moderator

Request:
`POST /logout`

This request expires the client's session cookie. When logged out, some API calls cannot be used.

### 3. Check if Logged in

Request: 
`GET /me`

This request returns a 200 code if the client making the request has a valid session cookie, otherwise a 401 code is returned.

### 4. Get Projects

Request:
`GET /projects`

Sample Response:
```json
[
    {
        "active": true,
        "demo_url": null,
        "description": "This website serves as a place to show what projects I am working on.",
        "gallery_images": [],
        "github_url": "https://github.com/Theodora605/portfolio/tree/main",
        "id": 10,
        "img_uri": "https://storage.cloud.google.com/theo-portfolio-images/preview.png",
        "name": "Personal Website",
        "server_endpoint": "127.0.0.1",
        "technologies": [
            {
                "description": "This website and the application demos hosted on it are built in React/Typescript.",
                "id": 6,
                "img_uri": "https://storage.cloud.google.com/theo-portfolio-images/react.png"
            },
            {
                "description": "The backend of this website uses a REST API written in Python for interfacing with its database.",
                "id": 8,
                "img_uri": "https://storage.cloud.google.com/theo-portfolio-images/flask.png"
            },
            {
                "description": "The website is hosted on AWS.",
                "id": 9,
                "img_uri": "https://storage.cloud.google.com/theo-portfolio-images/aws.png"
            }
        ]
    },
...
]
```

This request returns a list of all of the projects. Query parameters `demo` and `name` can be used to filter the results by the `demo_url` and `name` attributes respectively.

### 5. Get Project

Request:
`GET /projects/<id>`

This request return the project as specified by the path parameter `<id>`.

### 6. Add Project (Requires Elevation)

Request: 
`POST /projects`

Sample Body (JSON):
```json
{
    "name": "Sample Project",
    "description": "Lorem",
    "img_uri": "http://myprojectimage.com/",
    "server_endpoint": "http://123.123.123.123/endpoint",
    "github_url": "http://github.com/sample",
    "active": true,
    "technologies": [
        {
            "img_uri": "http://techimg1.com/",
            "description": "Lorem something this tech is cool."
        },
        {
            "img_uri": "http://techimg2.com/",
            "description": "This is a pretty cool thing too."
        }
    ],

    "gallery_images": [
        {
            "img_uri": "http://techimg1.com/"
        },
        {
            "img_uri": "http://techimg2.com/"
        }
    ]
}
```

This request adds a new project and its associated technologies and gallery images. Fails with a 409 code if the client does not have a valid session cookie.

### 7. Delete Project (Requires Elevation)

Request:
`DELETE /projects/<id>`

This request deletes the project specified by the `<id>` path parameter. Fails with a 409 code if the client does not have a valid session cookie.

### 8. Update Project (Requires Elevation)

Request:
`PUT /project/<id>`

Sample Body (JSON):
```json
{
    "demo_url": null,
    "description": "Lorem 1",
    "github_url": "http://github.com/sample1",
    "img_uri": "http://myprojectimage.com/1",
    "name": "Sample Project 1",
    "server_endpoint": "http://123.123.123.123/endpoint/1",
    "active": false,
    "technologies": [
        {
            "description": "Updated Lorem something this tech is cool. hi",
            "id": 1,
            "img_uri": "http://techimg1.com/1"
        },
        {
            "id": 2,
            "description": "A brand new tech 2",
            "img_uri": "http://beepboop.com/1"
        }
    ],

    "gallery_images": [
        {
            "id": 1,
            "img_uri": "http://newimagelink.com/"
        },
        {
            "id": null,
            "img_uri": "http://addednewimageitem.com/"
        }
    ]
}
```

This request updates the project as specified by the `<id>` path parameter. Items in the project's `technologies` and `gallery_images` lists must have an id associated to an existing item in the project or set as `null` if it is a new item. Any missing items in those lists from the original project and what was passed in the request body are removed. For example, a `gallery_image` item was removed and a new item was added to the list. Fails with a 409 code if the client does not have a valid session cookie.

### 9. Get Moderators (Requires Elevation)

Request:
`GET /mods`

Sample Response:
```json
[
    {
        "id": 1,
        "password": "encryptedpassword-flkdajdkgg[p.",
        "username": "someuser"
    }
]
```

This request returns a list of all the moderators. Fails with a 409 code if the client does not have a valid session cookie.

### 10. Add Moderator (Requires Elevation)

Request:
`POST /mods`

Sample Body (JSON):
```json
{
    "username": "someusername",
    "password": "somepassword"
}
```

This request adds a new moderator with the passed credentials. Fails with a 409 code if the client does not have a valid session cookie.

### 11. Delete Moderator (Requires Elevation)

Request:
`DELETE /mods/<id>`

This request removes the moderator specified by the `<id>` path variable. Fails with a 409 code if the client does not have a valid session cookie.

### 12. Upload Resume/CV (Requires Elevation)

Request:
`POST /cv`

Body (form-data)
```
key: cv
value: .pdf file
```

This request submits/updates the resume to the GCS bucket. Fails with a 409 code if the client does not have a valid session cookie.
