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

TODO
