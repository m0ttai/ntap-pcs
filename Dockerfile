FROM public.ecr.aws/lambda/python:3.8

COPY src/cloud-insights/ ./

RUN pip install --no-cache-dir -r requirements.txt

# CMD ["get-forensic-and-send-lambda.lambda_handler"]
CMD ["get-forensic-and-upload-lambda.lambda_handler"]