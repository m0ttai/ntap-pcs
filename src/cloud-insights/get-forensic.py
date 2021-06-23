import os
from urllib import request, parse
import json
from pprint import pprint
import datetime, time, calendar
from dateutil.relativedelta import relativedelta
import pandas
import boto3

### 検索条件 定義 ###
url = os.environ['CLOUD_SECURE_URL']
token = os.environ['CLOUD_SECURE_TOKEN']
svm = os.environ['GET_DEVICE_NAME']
output_path = '/tmp/'
upload_bucket = 'myuichi-python-upload-test-bucket'

### 検索レンジ生成 ###
def get_search_time(date):
	last = date - relativedelta(months=1)
	begin_date = datetime.datetime(last.year, last.month, 1)
	begin_date = int(time.mktime(begin_date.timetuple()) * 1000)
	end_date = datetime.datetime(date.year, date.month, 1)
	end_date = int(time.mktime(end_date.timetuple()) * 1000)
	### 月末日の取得 ###
	# last_end_date = datetime.datetime(last.year, last.month, calendar.monthrange(last.year, last.month)[1])
	# last_end_date = int(time.mktime(last_end_date.timetuple()) * 1000)
	return begin_date, end_date

### S3 オブジェクト情報取得 ###
s3 = boto3.resource('s3')
bucket = s3.Bucket(upload_bucket)

### Get Request クエリストリング & ヘッダ 定義 ###
today = datetime.datetime.utcnow()
begin_date, end_date = get_search_time(today)
param = {
	'deviceName': svm,
	'fromTime': begin_date,
	'toTime': end_date
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
	output_file = str(today.year) + str(today.month) + '_' + svm + '_' + 'output.csv'
	output_body.to_csv(output_path + output_file, encoding='utf-8')
	bucket.upload_file(output_path + output_file, output_file)