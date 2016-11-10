# About

[![forthebadge](http://forthebadge.com/images/badges/built-with-love.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/powered-by-oxygen.svg)](http://forthebadge.com)
[![forthebadge](http://forthebadge.com/images/badges/fuck-it-ship-it.svg)](http://forthebadge.com)

This is the Python version of [ebs-snapshot](https://github.com/jpdoria/ebs-snapshot). This function can be deployed to AWS Lambda.

# What is AWS Lambda?

AWS Lambda lets you run code without provisioning or managing servers. You pay only for the compute time you consume - there is no charge when your code is not running. With Lambda, you can run code for virtually any type of application or backend service - all with zero administration. Just upload your code and Lambda takes care of everything required to run and scale your code with high availability. You can set up your code to automatically trigger from other AWS services or call it directly from any web or mobile app

## Lambda Pricing

With AWS Lambda, you pay only for what you use. You are charged based on the number of requests for your functions and the time your code executes. The Lambda free tier includes 1M free requests per month and 400,000 GB-seconds of compute time per month.

- First 1 million requests per month are free
- $0.20 per 1 million requests thereafter ($0.0000002 per request)

## FAQs 

https://aws.amazon.com/lambda/faqs/

# Prerequisite

IAM Role Policy for AWS Lambda

# How to use this in AWS Lambda?

## IAM Setup

1. AWS Management Console > Identity and Access Management
2. Role > Create New Role
3. Give your role a name
4. Select AWS Lambda in AWS Service Roles
5. Just skip Attach Policy by click Next Step
6. Find your new role then click on it
7. Permissions > Inline Policies > Create a new one
8. Custom Policy > Select
9. Give your policy a name
10. Copy the policy below and paste it there

    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "Stmt0123456789012",
                "Effect": "Allow",
                "Action": [
                    "ec2:CreateSnapshot",
                    "ec2:CreateTags",
                    "ec2:DeleteSnapshot",
                    "ec2:DescribeSnapshots",
                    "ec2:DescribeVolumes",
                    "ses:SendRawEmail"
                ],
                "Resource": [
                    "*"
                ]
            }
        ]
    }
    ```

11. Validate Policy > Apply Policy

## Lambda Setup

1. Clone or download the code as zip
2. Change directory to `ebs-snapshot-python`
3. Open and edit `user_vars.py`

    ```python
    # Modify me
    domain = 'domain.com'
    ret_period = 7  # day(s)
    mail_from = 'AWS Notification <aws@{}>'.format(domain)
    mail_to = ['jpdoria@{}'.format(domain)]  # single recipient
    # mail_to = ['admin@company.com', 'user@company.com']  # multiple recipients
    ```

4. Then save and exit from the editor
5. Compress `ebs-snapshot.py` and `user-vars.py` into one zip file (ebs-snashot.zip)
6. AWS Management Console > Lambda
7. Create a Lambda function > Blank function
8. Skip Configure triggers by clicking Next button
9. Give your function a name and description
10. Choose Python 2.7 as Runtime
11. Code entry type: Upload a .ZIP file, then click Upload
12. Upload the ebs-snapshot.zip you created in Step 13
13. Handler: ebs-snapshot.main
14. Role: Choose an existing role, then find the role you created in IAM Setup section
15. Memory: 128 MB and Timeout: 5 mins
16. Click Next > Create function

# How to use this Lambda function with CloudWatch Events (daily snapshots)?

1. AWS Management Console > CloudWatch
2. Events > Rules > Create a new rule
3. Event selector: Schedule, fixed rate of 1 Day
4. Target: Lambda function, then select your ebs-snapshot function
5. Click Configure details
6. Give your a name and description
7. State should be Enabled
8. Click Create rule button