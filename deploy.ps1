# FinSight AI - Serverless Deployment Script
# Deploys: Lambda (backend) + S3/CloudFront (frontend)

$ErrorActionPreference = "Stop"
$REGION = "us-east-1"
$STACK_NAME = "finsight-ai"
$BACKEND_BUCKET = "finsight-ai-lambda-deploy-466742534146"
$FRONTEND_BUCKET = "finsight-ai-frontend-466742534146"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " FinSight AI - Serverless Deployment" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create S3 bucket for Lambda deployment package
Write-Host "[1/7] Creating deployment S3 bucket..." -ForegroundColor Yellow
aws s3 mb "s3://$BACKEND_BUCKET" --region $REGION 2>$null
Write-Host "  Done." -ForegroundColor Green

# Step 2: Package Lambda function
Write-Host "[2/7] Packaging Lambda function..." -ForegroundColor Yellow
Set-Location "backend"

# Create a clean package directory
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
New-Item -ItemType Directory -Path "package" | Out-Null

# Install dependencies into package
pip install -r requirements.txt -t package --quiet --no-deps 2>$null
pip install fastapi pydantic pydantic-settings python-dotenv boto3 httpx mangum python-multipart -t package --quiet 2>$null

# Copy application code
Copy-Item -Recurse "app" "package/app"
Copy-Item "lambda_handler.py" "package/"

# Create zip
Set-Location "package"
Compress-Archive -Path * -DestinationPath "..\lambda-package.zip" -Force
Set-Location "..\.."

Write-Host "  Lambda package created ($('{0:N1}' -f ((Get-Item 'backend\lambda-package.zip').Length / 1MB)) MB)" -ForegroundColor Green

# Step 3: Upload Lambda package to S3
Write-Host "[3/7] Uploading Lambda package to S3..." -ForegroundColor Yellow
aws s3 cp "backend\lambda-package.zip" "s3://$BACKEND_BUCKET/lambda-package.zip" --region $REGION
Write-Host "  Done." -ForegroundColor Green

# Step 4: Deploy Lambda function
Write-Host "[4/7] Deploying Lambda function + API Gateway..." -ForegroundColor Yellow

# Create/Update Lambda directly (simpler than SAM for this case)
$LAMBDA_EXISTS = aws lambda get-function --function-name finsight-ai-backend --region $REGION 2>&1
if ($LASTEXITCODE -eq 0) {
    # Update existing
    aws lambda update-function-code `
        --function-name finsight-ai-backend `
        --s3-bucket $BACKEND_BUCKET `
        --s3-key lambda-package.zip `
        --region $REGION | Out-Null
    Write-Host "  Lambda function updated." -ForegroundColor Green
} else {
    # Create IAM role
    $ROLE_ARN = aws iam get-role --role-name finsight-ai-lambda-role --query "Role.Arn" --output text 2>$null
    if (-not $ROLE_ARN) {
        $TRUST_POLICY = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
        aws iam create-role --role-name finsight-ai-lambda-role --assume-role-policy-document $TRUST_POLICY --region $REGION | Out-Null
        aws iam attach-role-policy --role-name finsight-ai-lambda-role --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
        aws iam attach-role-policy --role-name finsight-ai-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess
        aws iam attach-role-policy --role-name finsight-ai-lambda-role --policy-arn arn:aws:iam::aws:policy/AmazonPollyFullAccess
        Start-Sleep -Seconds 10  # Wait for role propagation
        $ROLE_ARN = aws iam get-role --role-name finsight-ai-lambda-role --query "Role.Arn" --output text
    }

    # Create Lambda function
    aws lambda create-function `
        --function-name finsight-ai-backend `
        --runtime python3.11 `
        --role $ROLE_ARN `
        --handler lambda_handler.handler `
        --code "S3Bucket=$BACKEND_BUCKET,S3Key=lambda-package.zip" `
        --timeout 30 `
        --memory-size 512 `
        --environment "Variables={BEDROCK_MODEL_ID=amazon.nova-lite-v1:0,CORS_ORIGINS=*,AWS_REGION_NAME=us-east-1}" `
        --region $REGION | Out-Null
    Write-Host "  Lambda function created." -ForegroundColor Green
}

# Step 5: Create/Update API Gateway (HTTP API)
Write-Host "[5/7] Setting up API Gateway..." -ForegroundColor Yellow

$API_ID = aws apigatewayv2 get-apis --region $REGION --query "Items[?Name=='finsight-ai-api'].ApiId" --output text 2>$null
if (-not $API_ID) {
    $API_RESULT = aws apigatewayv2 create-api `
        --name finsight-ai-api `
        --protocol-type HTTP `
        --cors-configuration "AllowOrigins=*,AllowMethods=GET,POST,PUT,DELETE,OPTIONS,AllowHeaders=*" `
        --region $REGION
    $API_ID = ($API_RESULT | ConvertFrom-Json).ApiId

    # Create Lambda integration
    $LAMBDA_ARN = aws lambda get-function --function-name finsight-ai-backend --region $REGION --query "Configuration.FunctionArn" --output text
    
    $INTEGRATION = aws apigatewayv2 create-integration `
        --api-id $API_ID `
        --integration-type AWS_PROXY `
        --integration-uri $LAMBDA_ARN `
        --payload-format-version "2.0" `
        --region $REGION
    $INTEGRATION_ID = ($INTEGRATION | ConvertFrom-Json).IntegrationId

    # Create default route
    aws apigatewayv2 create-route `
        --api-id $API_ID `
        --route-key "`$default" `
        --target "integrations/$INTEGRATION_ID" `
        --region $REGION | Out-Null

    # Create stage
    aws apigatewayv2 create-stage `
        --api-id $API_ID `
        --stage-name prod `
        --auto-deploy `
        --region $REGION | Out-Null

    # Add Lambda permission
    aws lambda add-permission `
        --function-name finsight-ai-backend `
        --statement-id apigateway-invoke `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:466742534146:${API_ID}/*" `
        --region $REGION 2>$null | Out-Null
}

$API_URL = "https://$API_ID.execute-api.$REGION.amazonaws.com/prod"
Write-Host "  API Gateway: $API_URL" -ForegroundColor Green

# Step 6: Build and deploy frontend
Write-Host "[6/7] Building frontend..." -ForegroundColor Yellow
Set-Location "frontend"

# Update API URL in frontend
$env:VITE_API_URL = $API_URL
npm install --silent 2>$null
npm run build

Set-Location ".."
Write-Host "  Frontend built." -ForegroundColor Green

# Step 7: Deploy frontend to S3 + CloudFront
Write-Host "[7/7] Deploying frontend to S3..." -ForegroundColor Yellow

# Create frontend bucket
aws s3 mb "s3://$FRONTEND_BUCKET" --region $REGION 2>$null

# Enable static website hosting
aws s3 website "s3://$FRONTEND_BUCKET" --index-document index.html --error-document index.html --region $REGION

# Set public access
$BUCKET_POLICY = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$FRONTEND_BUCKET/*"
        }
    ]
}
"@

aws s3api put-public-access-block --bucket $FRONTEND_BUCKET --public-access-block-configuration "BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false" --region $REGION
aws s3api put-bucket-policy --bucket $FRONTEND_BUCKET --policy $BUCKET_POLICY --region $REGION

# Upload frontend files
aws s3 sync "frontend\dist" "s3://$FRONTEND_BUCKET" --delete --region $REGION
Write-Host "  Frontend deployed." -ForegroundColor Green

# Done!
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " DEPLOYMENT COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend API:  $API_URL" -ForegroundColor Cyan
Write-Host "Frontend URL: http://$FRONTEND_BUCKET.s3-website-$REGION.amazonaws.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test backend: curl $API_URL/" -ForegroundColor Gray
Write-Host ""

# Cleanup
Remove-Item -Recurse -Force "backend\package" -ErrorAction SilentlyContinue
Remove-Item "backend\lambda-package.zip" -ErrorAction SilentlyContinue
