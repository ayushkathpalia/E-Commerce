import requests
import json
import paytmchecksum
import datetime
from decouple import config


PAYTM_MID = config('PAYTM_MID')
PAYTM_MERCHANT_KEY = config('PAYTM_MERCHANT_KEY')
PAYTM_ENVIRONMENT= config('PAYTM_ENVIRONMENT')
PAYTM_WEBSITE= config('PAYTM_WEBSITE')

# amount= '1.00'
# order_id='order_'+str(datetime.datetime.now().timestamp())

def getTransactionToken(amount,order_id):
    paytmParams = dict()

    paytmParams["body"] = {
        "requestType"   : "Payment",
        "mid"           : PAYTM_MID,
        "websiteName"   : PAYTM_WEBSITE,
        "orderId"       : order_id,
        "callbackUrl"   : "http://127.0.0.1:8000/orders/app_callback/",
        "txnAmount"     : {
            "value"     : amount,
            "currency"  : "INR",
        },
        "userInfo"      : {
            "custId"    : "CUST_001",
        },
    }

    # Generate checksum by parameters we have in body
    # Find your Merchant Key in your Paytm Dashboard at https://dashboard.paytm.com/next/apikeys 
    checksum = paytmchecksum.generateSignature(json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY)

    paytmParams["head"] = {
        "signature"    : checksum
    }

    post_data = json.dumps(paytmParams)

    url = f'{PAYTM_ENVIRONMENT}/theia/api/v1/initiateTransaction?mid={PAYTM_MID}&orderId={order_id}'

    response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
    response_str = json.dumps(response)
    res = json.loads(response_str)
    print(res)
    
    #{'head': {'responseTimestamp': '1668527667342', 'version': 'v1', 'signature': 'L2b/fTylASSbYkwnhAQv41r5l57krjanRnJQsbPmBWRB/GENVHwNeH+BygHeb0+z/hinYat7jyFARPsEdPX1NmaAgi5JHmzei0qf4VqHC0c='}, 'body': {'resultInfo': {'resultStatus': 'S', 'resultCode': '0000', 'resultMsg': 'Success'},
    #  'txnToken': 'add43aece5c24ca298ad91108241abbc1668527667113', 'isPromoCodeValid': False, 'authenticated': False}}

    if res["body"]["resultInfo"]["resultStatus"]=='S':
        token=res["body"]["txnToken"]
    else:
        token=""
    return token

def transactionStatus(order_id):
    paytmParams = dict()
    paytmParams["body"] = {
        "mid" : PAYTM_MID,
        "orderId" : order_id,
    }
    checksum = paytmchecksum.generateSignature(json.dumps(paytmParams["body"]), PAYTM_MERCHANT_KEY)

    # head parameters
    paytmParams["head"] = {
        "signature"	: checksum
    }

    # prepare JSON string for request
    post_data = json.dumps(paytmParams)

    url = PAYTM_ENVIRONMENT+"/v3/order/status"

    response = requests.post(url, data = post_data, headers = {"Content-type": "application/json"}).json()
    response_str = json.dumps(response)
    res = json.loads(response_str)
    print(res)
    msg="Transaction Status Response"
    return res['body']