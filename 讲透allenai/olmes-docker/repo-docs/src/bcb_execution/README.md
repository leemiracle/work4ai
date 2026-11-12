Deploy a lambda verifier for BigCodeBench. Based on [MultiPL-E](../multiple_execution/README.md).

### Setup

Make sure you have credentials for the S2 account in `~/.aws/credentials`:

```sh
[s2]
aws_access_key_id=...
aws_secret_access_key=...
```

### Build and deploy

```sh
# Build + tag docker
docker buildx build --platform linux/amd64 -t codex/bcb:latest .
docker tag codex/bcb:latest 896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/bcb:latest

# (One time setup) Create ECR registry
aws ecr create-repository --repository-name codex/bcb --region us-east-1 --profile s2

# Push to ECR
aws ecr get-login-password --region us-east-1 --profile s2 | docker login --username AWS --password-stdin 896129387501.dkr.ecr.us-east-1.amazonaws.com
docker push 896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/bcb:latest

# (One time setup) Create lambda func
aws lambda create-function \
    --profile s2 \
    --function-name bcb \
    --package-type Image \
    --code ImageUri=896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/bcb:latest \
    --role arn:aws:iam::896129387501:role/lambda-ex \
    --region us-east-1

# Deploy to lambda
aws lambda update-function-code \
    --profile s2 \
    --function-name bcb \
    --image-uri 896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/bcb:latest \
    --region us-east-1

# Update and pin the production lambda
NEW_VERSION=$(aws lambda publish-version \
    --profile s2 \
    --function-name bcb \
    --description "<identifying information for new release>" \
    --region us-east-1 \
    --query 'Version' --output text)

# (One time setup) Create lambda alias
aws lambda create-alias \
  --profile s2 \
  --function-name bcb \
  --name prod \
  --function-version $NEW_VERSION \
  --region us-east-1

aws lambda update-alias \
    --profile s2 \
    --function-name bcb \
    --name prod \
    --function-version $NEW_VERSION \
    --region us-east-1
```