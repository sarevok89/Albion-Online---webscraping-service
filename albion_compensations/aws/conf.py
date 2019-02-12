import datetime

AWS_FILE_EXPIRE = 200
AWS_PRELOAD_METADATA = True
AWS_QUERYSTRING_AUTH = False

DEFAULT_FILE_STORAGE = 'albion_compensations.aws.utils.MediaRootS3BotoStorage'
STATICFILES_STORAGE = 'albion_compensations.aws.utils.StaticRootS3BotoStorage'
AWS_STORAGE_BUCKET_NAME = 'albion-compensations'
S3DIRECT_REGION = 'us-east-2'
S3_URL = '//%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
MEDIA_URL = '//%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
MEDIA_ROOT = MEDIA_URL
STATIC_URL = S3_URL + 'static/'
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

two_months = datetime.timedelta(days=61)
date_two_months_later = datetime.date.today() + two_months
expires = date_two_months_later.strftime("%A, %d %B %Y 20:00:00 GMT")

AWS_HEADERS = {
    'Expires': expires,
    'Cache-Control': 'max-age=%d' % (int(two_months.total_seconds()), ),
}

aws_secret_key_id = 'AKIAJZ7G7LLNHVOEGTKA'
aws_secret_access_key = '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'

# s3 = boto3.resource('s3', aws_access_key_id='AKIAJZ7G7LLNHVOEGTKA', aws_secret_access_key='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')