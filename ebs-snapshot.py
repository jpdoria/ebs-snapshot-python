import boto3
import logging
import os
import time

from user_vars import ret_period
from user_vars import mail_from
from user_vars import mail_to
from datetime import datetime
from email.mime.text import MIMEText
from random import randint

script_name = 'ebs-snapshot.py'
description = 'Created by {}'.format(script_name)

rand = randint(0, 9999999)
log_file = '/tmp/aws-ebs-snapshot-{}.log'.format(rand)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler(log_file)
fh.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s - %(funcName)s - %(message)s',
    datefmt='%Y-%b-%d %I:%M:%S %p'
)
fh.setFormatter(formatter)
logger.addHandler(fh)


def notify():
    """
    Notify recipients
    """
    try:
        ses = boto3.client('ses')
        subject = '{0} {1}'.format(
            script_name,
            datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        )

        with open(log_file) as my_file:
            msg = MIMEText(my_file.read())

        msg['From'] = mail_from

        if len(mail_to) > 1:
            msg['To'] = ', '.join(mail_to)
        elif len(mail_to) == 1:
            msg['To'] = mail_to[0]

        msg['Subject'] = subject

        logger.info('Sending \'{0}\' to {1}'.format(subject, mail_to))

        ses.send_raw_email(
            Source=mail_from,
            Destinations=mail_to,
            RawMessage={
                'Data': msg.as_string()
            }
        )

        logger.info('Message sent!')
    except Exception as e:
        logger.error(e, exc_info=True)
    finally:
        os.remove(log_file)


def delete_snapshots(aws_regions):
    """
    Delete EBS Snapshots
    """
    try:
        snapshots = []

        for region in aws_regions:
            ec2 = boto3.client('ec2', region_name=region)
            response = ec2.describe_snapshots(
                Filters=[
                    {
                        'Name': 'description',
                        'Values': [
                            description
                        ]
                    }
                ]
            )

            logger.info('Fetching snapshot(s) in {}...'.format(region))

            for key in response['Snapshots']:
                pattern = '%Y-%m-%d %H:%M:%S.%f'
                snap_id = key['SnapshotId']
                snap_date = key['StartTime'].strftime(pattern)
                cur_date = datetime.utcnow().strftime(pattern)
                epoch_snap_date = int(
                    time.mktime(time.strptime(snap_date, pattern))
                )
                epoch_cur_date = int(
                    time.mktime(time.strptime(cur_date, pattern))
                )
                difference = (epoch_cur_date - epoch_snap_date) / (60*60*24)
                day_diff = int(difference)

                logger.info('SnapshotId: {}'.format(snap_id))
                logger.info('SnapshotDate: {}'.format(snap_date))
                logger.info('CurrentDate: {}'.format(cur_date))
                logger.info('Difference: {} day(s)'.format(day_diff))
                logger.info('RetentionPeriod: {} day(s)'.format(ret_period))

                if day_diff >= ret_period:
                    logger.info('snap_date >= ret_period')
                    logger.info('Deleting {}...'.format(snap_id))
                    ec2.delete_snapshot(
                        SnapshotId=snap_id
                    )
                    snapshots.append(snap_id)

                    logger.info('{} removed!'.format(snap_id))

            logger.info('Task completed in {}!'.format(region))

        if snapshots:
            logger.info('Snapshot(s): {}'.format(snapshots))

        logger.info(
            'Total number of snapshot(s) deleted: {}'.format(len(snapshots))
        )
    except Exception as e:
        logger.error(e, exc_info=True)


def create_snapshots(aws_regions):
    """
    Create EBS Snapshots
    """
    try:
        snapshots = []

        for region in aws_regions:
            snaps_region = []
            ec2 = boto3.client('ec2', region_name=region)
            response = ec2.describe_volumes()

            logger.info('Fetching EBS volume(s) in {}...'.format(region))

            for key in response['Volumes']:
                vol_id = key['VolumeId']

                logger.info('Creating snapshot for {}...'.format(vol_id))

                create_snap_response = ec2.create_snapshot(
                    VolumeId=vol_id,
                    Description=description
                )
                snap_id = create_snap_response['SnapshotId']
                snaps_region.append(snap_id)
                snapshots.append(snap_id)

                logger.info('{} created!'.format(snap_id))

            if snaps_region:
                ec2.create_tags(
                    Resources=snaps_region,
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': 'AWS EBS Snapshot'
                        },
                        {
                            'Key': 'Expiration',
                            'Value': 'This snapshot will expire in {} day(s)'
                            .format(ret_period)
                        }
                    ]
                )

            logger.info('Task completed in {}!'.format(region))

        if snapshots:
            logger.info('Snapshot(s): {}'.format(snapshots))

        logger.info(
            'Total number of snapshot(s) created: {}'.format(len(snapshots))
        )
    except Exception as e:
        logger.error(e, exc_info=True)


def describe_regions():
    """
    List the available regions in AWS then add them to aws_regions list
    """
    try:
        ec2 = boto3.client('ec2')
        regions = ec2.describe_regions()['Regions']
        region_list = []

        for region in regions:
            region_list.append((region['RegionName']))

        return region_list
    except Exception as e:
        logger.error(e, exc_info=True)


# noinspection PyUnusedLocal,PyUnusedLocal
def main(event, context):
    """
    Main function that will invoke other functions
    """
    aws_regions = describe_regions()
    create_snapshots(aws_regions)
    delete_snapshots(aws_regions)
    notify()
