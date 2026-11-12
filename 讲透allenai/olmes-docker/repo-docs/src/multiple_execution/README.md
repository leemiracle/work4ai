# Code execution lambda for multiple programming languages

This code is adapted from https://github.com/nuprl/MultiPL-E/tree/main/evaluation
to handle invocations from a task running in oe-eval.

- currently deployed at arn:aws:lambda:us-east-1:896129387501:function:multiple-ex

To update this deployed version:
- from within multiple_execution directory, build and tag image

```sh
docker buildx build --platform linux/amd64 -t codex/multiple_ex:latest .
docker tag codex/multiple_ex:latest 896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/multiple_ex:latest
```

- authenticate to ECR registry and push image

```sh
aws ecr get-login-password --region us-east-1 | sudo docker login --username AWS --password-stdin 896129387501.dkr.ecr.us-east-1.amazonaws.com
docker push 896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/multiple_ex:latest
```

- deploy new image via aws cli (can also accomplish this via aws console)

```sh
aws lambda update-function-code \
--function-name multiple-ex \
--image-uri 896129387501.dkr.ecr.us-east-1.amazonaws.com/codex/multiple_ex:latest \
--region us-east-1
```

Note that multiple-ex:dev alias points at latest version, and multiple-ex:prod is pinned to a known stable version. To update prod, publish and pin the new version:

```sh
NEW_VERSION=$(aws lambda publish-version \
    --function-name multiple-ex \
    --description "<identifying information for new release>" \
    --region us-east-1 \
    --query 'Version' --output text)

aws lambda update-alias \
--function-name multiple-ex \
--name prod \
--function-version $NEW_VERSION \
--region us-east-1
```
