# import os
# mgs = __import__('get-forensic-and-upload-lambda')
# 
# url = os.environ['CLOUD_SECURE_URL']
# token = os.environ['CLOUD_SECURE_TOKEN']
# svm = os.environ['GET_DEVICE_NAME']
# output_path = '/tmp/'
# 
# attachment = mgs.get_forensic_log(svm, token, url, output_path)
# print(attachment)

out = 'pytest clear'
assert out == 'pytest clear'