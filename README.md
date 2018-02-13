Sentry on AWS Lambda
====================

Deploy Sentry on AWS using API Gateway and Lambda via Zappa!

Based on:
- https://github.com/mocco/sentry-uwsgi
- https://github.com/ltbl/sentry-cloudformation-teamplate
- https://github.com/acervos/sentry

Requirements
------------

According to official documentation:
https://docs.sentry.io/server/installation/
Sentry requires:
- RDS PgSQL
- ElastiCache Redis

They can be created via AWS Console.

Create Cache
------------

Here provided sample CloudFormation template for creating Redis instance. But it is also 
possible to create it via Console.

    $ aws cloudformation create-stack --stack-name Sentry-Cache --template-body file://cloudformation.template

Access ElastiCache from Lambda
------------------------------

By default ElastiCache is not available in AWS Labmda.

To workaround:
- add VPC to Lambda function and add Endpoint to allow access S3.
- or forward traffic from EC2 instance to VPC with Redis as described in:
http://docs.aws.amazon.com/AmazonElastiCache/latest/UserGuide/Access.Outside.html

Configuration
-------------

All configuration settings are loaded from S3 bucket where special JSON is stored.
You can change path to it in the `zappa_settings.json`.

sentry_remote_env.json sample:

    {
        "SECRET_KEY": "foobar",
        "SENTRY_CONF": "sentry.conf.py",
        "AWS_S3_FILE_BUCKET": "foo-bar-filestore",
        "GOOGLE_CLIENT_ID": "",
        "GOOGLE_CLIENT_SECRET": "",
        "EMAIL_HOST_USER": "foo",
        "EMAIL_HOST_PASSWORD": "bar",
        "REDIS_HOST": "elsaticache.eu-west-1.ec2.amazonaws.com",
        "REDIS_PORT": "6379",
        "DB_ENGINE": "django.db.backends.postgresql_psycopg2",
        "DB_NAME": "sentry",
        "DB_USER": "root",
        "DB_PASSWORD": "bar",
        "DB_HOST": "postgresql.eu-west-1.rds.amazonaws.com",
        "DB_PORT": ""
    }

First start
-----------

Before login it is required to apply migrations:

    $ make upgrade

After than you can login and after than loaddata:

    $ make loaddata

This will create sample projects from `initial_data.json`.
