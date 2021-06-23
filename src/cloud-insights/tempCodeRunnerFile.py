import datetime, time, calendar
from dateutil.relativedelta import relativedelta

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

today = datetime.datetime.utcnow()
begin_date, end_date = get_search_time(today)
print(begin_date)
print(end_date)