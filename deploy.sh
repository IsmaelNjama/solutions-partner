#!/bin/bash
set -e

# Configuration
AWS_REGION="us-east-1"
APP_NAME="search-companion"
ECR_REPO_NAME="solutions-partner"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
SECRET_ARN="${SECRET_ARN:?SECRET_ARN env var is required}"

VPC_STACK_NAME="${APP_NAME}-vpc-stack"
APP_STACK_NAME="${APP_NAME}-stack"

# -------------------------------------------------------
# Deploy VPC stack (if not already deployed)
# -------------------------------------------------------
if aws cloudformation describe-stacks --stack-name $VPC_STACK_NAME --region $AWS_REGION 2>/dev/null; then
  echo "VPC stack already exists, skipping..."
else
  echo "Creating VPC stack..."
  aws cloudformation create-stack \
    --stack-name $VPC_STACK_NAME \
    --template-body file://infra/vpc.yml \
    --parameters ParameterKey=FunctionName,ParameterValue=$APP_NAME \
    --region $AWS_REGION
  aws cloudformation wait stack-create-complete --stack-name $VPC_STACK_NAME --region $AWS_REGION
  echo "VPC stack created."
fi

# -------------------------------------------------------
# Build and push Docker image
# -------------------------------------------------------
echo "Building Docker image..."
docker build -t $APP_NAME .

aws ecr describe-repositories --repository-names $ECR_REPO_NAME --region $AWS_REGION 2>/dev/null || \
  aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

IMAGE_TAG=$(date +%Y%m%d-%H%M%S)
IMAGE_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:$IMAGE_TAG"
docker tag $APP_NAME:latest $IMAGE_URI
docker push $IMAGE_URI
echo "Image pushed: $IMAGE_URI"

# -------------------------------------------------------
# Deploy app stack
# -------------------------------------------------------
PARAMS="ParameterKey=FunctionName,ParameterValue=$APP_NAME \
        ParameterKey=ImageUri,ParameterValue=$IMAGE_URI \
        ParameterKey=SecretArn,ParameterValue=$SECRET_ARN"

if aws cloudformation describe-stacks --stack-name $APP_STACK_NAME --region $AWS_REGION 2>/dev/null; then
  echo "Updating app stack..."
  aws cloudformation update-stack \
    --stack-name $APP_STACK_NAME \
    --template-body file://infra/main.yml \
    --parameters $PARAMS \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION
  aws cloudformation wait stack-update-complete --stack-name $APP_STACK_NAME --region $AWS_REGION
else
  echo "Creating app stack..."
  aws cloudformation create-stack \
    --stack-name $APP_STACK_NAME \
    --template-body file://infra/main.yml \
    --parameters $PARAMS \
    --capabilities CAPABILITY_NAMED_IAM \
    --region $AWS_REGION
  aws cloudformation wait stack-create-complete --stack-name $APP_STACK_NAME --region $AWS_REGION
fi

echo "Deployment complete!"
aws cloudformation describe-stacks \
  --stack-name $APP_STACK_NAME \
  --region $AWS_REGION \
  --query "Stacks[0].Outputs" \
  --output table
