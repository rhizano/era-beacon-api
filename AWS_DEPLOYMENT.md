# AWS Deployment Guide

This guide covers deploying the BLE Beacon Presence Tracking API to AWS using free tier services.

## AWS Free Tier Deployment Options

### Option 1: AWS Lambda + API Gateway (Recommended for Free Tier)
- **Cost**: Free for up to 1M requests/month
- **Best for**: Low to moderate traffic
- **Database**: RDS Free Tier (PostgreSQL) or DynamoDB

### Option 2: AWS EC2 + RDS
- **Cost**: Free for 12 months (t2.micro instance)
- **Best for**: Full control, traditional deployment
- **Database**: RDS Free Tier PostgreSQL

### Option 3: AWS App Runner
- **Cost**: Pay-per-use (minimal cost for low traffic)
- **Best for**: Easiest deployment from container
- **Database**: RDS Free Tier PostgreSQL

## Prerequisites

1. AWS Account with free tier access
2. AWS CLI installed and configured
3. Docker installed (for some deployment options)

## Option 1: Serverless Deployment (Lambda + API Gateway)

### 1.1 Install Serverless Framework

```bash
npm install -g serverless
npm install -g serverless-python-requirements
```

### 1.2 Configure Serverless

Create `serverless.yml` in project root (see deployment files).

### 1.3 Deploy

```bash
# Install dependencies
npm install

# Deploy to AWS
serverless deploy
```

## Option 2: EC2 Deployment

### 2.1 Launch EC2 Instance

1. **Instance Type**: t2.micro (free tier)
2. **AMI**: Amazon Linux 2
3. **Security Group**: 
   - HTTP (80)
   - HTTPS (443)
   - SSH (22)
   - Custom TCP (8000) for development

### 2.2 Setup EC2 Instance

```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Update system
sudo yum update -y

# Install Python 3.9
sudo yum install python3.9 python3.9-pip git -y

# Clone repository
git clone <your-repo> era-beacon-api
cd era-beacon-api

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn supervisor
```

### 2.3 Setup Database (RDS PostgreSQL)

1. **Create RDS Instance**:
   - Engine: PostgreSQL
   - Instance Class: db.t3.micro (free tier)
   - Storage: 20 GB (free tier limit)
   - Public Access: Yes (for setup, restrict later)

2. **Configure Database**:
   ```bash
   # Update .env file with RDS endpoint
   DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/beacon_api
   ```

### 2.4 Production Deployment

See `deployment/ec2_setup.sh` for complete setup script.

## Option 3: AWS App Runner

### 3.1 Prepare Container

App Runner will use the existing `Dockerfile`.

### 3.2 Create App Runner Service

1. Go to AWS App Runner console
2. Create service from source code repository
3. Connect to your GitHub repository
4. Configure:
   - Runtime: Docker
   - Build command: Use Dockerfile
   - Port: 8000

## Database Options

### RDS PostgreSQL (Recommended)
- **Free Tier**: 750 hours/month, 20GB storage
- **Setup**: See RDS configuration in deployment files

### DynamoDB (Alternative)
- **Free Tier**: 25GB storage, 25 read/write capacity units
- **Note**: Requires code modifications for NoSQL

## Environment Variables for Production

```bash
# Production .env
DATABASE_URL=postgresql://username:password@rds-endpoint:5432/beacon_api
SECRET_KEY=generate-strong-random-key-here
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Security Considerations

1. **Environment Variables**: Use AWS Secrets Manager or Parameter Store
2. **Database**: Restrict access to application subnet only
3. **API**: Use HTTPS with SSL certificate (AWS Certificate Manager)
4. **Authentication**: Consider AWS Cognito integration

## Monitoring and Logging

- **CloudWatch**: Monitor application logs and metrics
- **Health Checks**: Implement `/health` endpoint monitoring
- **Alarms**: Set up CloudWatch alarms for failures

## Cost Optimization

1. **Use free tier resources**:
   - EC2 t2.micro (750 hours/month)
   - RDS db.t3.micro (750 hours/month)
   - 20GB RDS storage
   - Lambda 1M requests/month

2. **Monitor usage**:
   - Set up billing alerts
   - Use AWS Cost Explorer
   - Stop/start EC2 instances when not needed

## Scaling Considerations

### Auto Scaling (Post Free Tier)
- Application Load Balancer
- Auto Scaling Groups
- Multi-AZ RDS deployment

### Performance Optimization
- CloudFront CDN for static content
- ElastiCache for caching
- Read replicas for database

## Troubleshooting

### Common Issues
1. **Database Connection**: Check security groups and RDS accessibility
2. **Memory Issues**: t2.micro has limited memory, optimize application
3. **Timeout Issues**: Increase Lambda timeout for serverless deployment

### Debugging
```bash
# Check application logs
sudo tail -f /var/log/beacon-api/app.log

# Check system resources
htop
df -h

# Test database connection
python -c "from app.database.session import engine; print(engine.execute('SELECT 1').scalar())"
```

## Next Steps

1. Choose deployment option based on your needs
2. Follow the specific deployment guide
3. Configure monitoring and alerting
4. Set up CI/CD pipeline (see GitHub Actions workflows)
5. Configure domain name and SSL certificate

For detailed step-by-step instructions, see the specific deployment guides in the `deployment/` folder.
