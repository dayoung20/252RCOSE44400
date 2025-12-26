FROM public.ecr.aws/lambda/python:3.13

# 필요한 라이브러리 설치 
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

# Lambda 함수 코드 복사
COPY lambda_function.py .

# Lambda 진입점
CMD ["lambda_function.lambda_handler"]
