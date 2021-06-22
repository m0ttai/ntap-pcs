import os
from urllib import request, parse
import json
from pprint import pprint
import datetime
import time
import pandas
import boto3

### 検索条件 定義 ###
url = os.environ['CLOUD_SECURE_URL']
token = os.environ['CLOUD_SECURE_TOKEN']
svm = os.environ['GET_DEVICE_NAME']
from_date = '20210601'
to_date = '20210630'
output_path = '/tmp/'
output_file = from_date + '_' + svm + '_' + 'output.csv'
upload_bucket = 'myuichi-python-upload-test-bucket'

def conv_epochtime(date):
	date_time = datetime.datetime.strptime(date, '%Y%m%d')
	date_time = date_time.astimezone(datetime.timezone(datetime.timedelta(hours=-9)))
	epochtime = int(time.mktime(date_time.timetuple()) * 1000)
	return epochtime

### S3 オブジェクト情報取得 ###
s3 = boto3.resource('s3')
bucket = s3.Bucket(upload_bucket)

### Get Request クエリストリング & ヘッダ 定義 ###
from_epochtime = conv_epochtime(from_date)
to_epochtime = conv_epochtime(to_date)
param = {
	'deviceName': svm,
	'fromTime': from_epochtime,
	'toTime': to_epochtime
}
headers = {
	'x-cloudinsights-apikey': token
}

### クエリストリングのParse処理 ###
query_strings = parse.urlencode(param)
get_url = url + query_strings

### Get Request 生成・実行 ###
req = request.Request(get_url, headers=headers)
with request.urlopen(req) as res:
	body = json.loads(res.read())
	output_body = pandas.json_normalize(body['results'])
	output_body.to_csv(output_path + output_file, encoding='utf-8')
	bucket.upload_file(output_path + output_file, output_file)