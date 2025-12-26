### 서버리스 컴퓨팅을 활용한 리뷰 데이터 처리 파이프라인 구축

#### 개요
- 고객 리뷰 데이터를 효과적으로 처리하는 서버리스 컴퓨팅 파이프라인을 AWS로 설계 및 구현
- 이벤트 기반 데이터 처리, AWS의 다양한 서버리스 관련 서비스를 통합하여 시스템을 구축

#### 구현 항목
1. API Gateway
- method : HTTP POST 메서드 생성 및 Lambda 함수 통합
- 배포 : API Gateway를 prod 스테이지로 배포
- 엔드포인트 URL : 배포 후 생성된 엔드포인트 URL을 활용

2. docker container 생성 및 AWS ECR에 이미지 업로드
```
aws ecr create-repository \
    --repository-name review-processing-{number} \
    --region us-east-1 \
    --image-scanning-configuration scanOnPush=true
```

3. Lambda 함수 설정
4. DynamoDB에 데이터 저장
- 분석된 리뷰 데이터를 DynamoDB 테이블에 저장
- partition key : user_name, sort_key : timestamp
5. AWS SES 이메일 전송
- positive 리뷰로 감지된 경우 이메일로 알림을 전송
