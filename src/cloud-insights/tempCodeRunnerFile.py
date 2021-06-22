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
print("epochtime: " + from_epochtime)