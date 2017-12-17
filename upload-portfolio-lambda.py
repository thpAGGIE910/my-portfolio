import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    s3 = boto3.resource('s3')
    sns = boto3.resource('sns')
    
    try:
        topic = sns.Topic('arn:aws:sns:us-east-1:069481480662:deployPortfolioTopic')
        portfolio_bucket = s3.Bucket('portfolio.travis-payne.com')
        build_bucket = s3.Bucket('portfoliobuild.travis-payne.com')
        
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)
        
        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
                
        print "Delpoy finished!"
        topic.publish(Subject="Portfolio Delpoyed", Message="Portfolio deployed successfully!")
    except:
        topic.publish(Subject="Portfolio Delpoy Failed", Message="The portfolio was NOT deployed successfully")
        raise
    
    return 'Hello from Lambda'
