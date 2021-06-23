import os
from urllib import request, parse
import json
from pprint import pprint
import datetime, time, calendar
from dateutil.relativedelta import relativedelta
import pandas
import boto3
from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

### APIリクエスト条件 ###
url = os.environ['CLOUD_SECURE_URL']
token = os.environ['CLOUD_SECURE_TOKEN']
svm = os.environ['GET_DEVICE_NAME']

### データ一時保存先 ###
output_path = '/tmp/'
# upload_bucket = 'myuichi-python-upload-test-bucket'

### メール送信条件 ###
sender = "y1.mashimo@gmail.com"
recipient = "Yuichi.Mashimo@netapp.com"
region = "us-west-2"
subject = "ファイルサーバ アクセスログの定期送信 - "
# attachment = "/root/test.txt"
body_text = """
ファイルサーバのアクセスログをお送りします。
"""
body_html = """
<html>
<head></head>
<body>
<p>
	ファイルサーバのアクセスログをお送りします。
</p>
</body>
</html>
"""
charset = "utf-8"

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

### アクセスログ取得 ###
def get_forensic_log(svm, token, url, output_path):
	### S3 オブジェクト情報取得 ###
	# s3 = boto3.resource('s3')
	# bucket = s3.Bucket(upload_bucket)

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
		attachment = output_path + output_file
		output_body.to_csv(attachment, encoding='utf-8')
		# bucket.upload_file(output_path + output_file, output_file)
	
	return today, attachment

def send_search_result(sender, recipient, region, subject, body_text, body_html, charset, attachment, today):
	### AWS SES 情報取得 ###
	client = boto3.client('ses', region_name=region)

	### メール本文 生成 ###
	textpart = MIMEText(body_text.encode(charset), 'plain', charset)
	htmlpart = MIMEText(body_html.encode(charset), 'html', charset)
	msg_body = MIMEMultipart('alternative')
	msg_body.attach(textpart)
	msg_body.attach(htmlpart)

	### ファイルの添付 ###
	msg_att = MIMEApplication(open(attachment, 'rb').read())
	msg_att.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))

	### メール作成 ###
	msg = MIMEMultipart('mixed')
	msg['Subject'] = subject + str(today.year) + str(today.month)
	msg['From'] = sender
	msg['To'] = recipient
	msg.attach(msg_body)
	msg.attach(msg_att)
	print(msg)

	try:
		response = client.send_raw_email(
			Source=sender,
			Destinations=[
				recipient
			],
			RawMessage={
				'Data':msg.as_string(),
			},
		)

	except ClientError as e:
		print(e.response['Error']['Message'])
	else:
		print("Email sent! Message ID: ")
		print(response['MessageId'])
	
	return

def lambda_handler(event, context):
	today, attachment = get_forensic_log(svm, token, url, output_path)
	send_search_result(sender, recipient, region, subject, body_text, body_html, charset, attachment, today)