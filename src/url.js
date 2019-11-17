const uuidv4 = require('uuid/v4');
const AWS = require('aws-sdk');
const fetch = require("node-fetch");

AWS.config.update({ region: process.env.REGION || 'us-east-2' });
const s3 = new AWS.S3();

const uploadBucket = 'elasticbeanstalk-us-east-2-693859464061';
const url = "https://" + uploadBucket + ".s3.us-east-2.amazonaws.com/";
const folder = "receipts/";

exports.handler = async function(event, context) {
  console.log("got called with body (cut-off): " + String(event.body).substring(0, 1000));
  const data = JSON.parse(event.body);
  const filename = folder + uuidv4() + data.suffix;
  var result = true;
  const buffer = new Buffer(data.image, 'base64');
  try{
    var out = s3.putObject( {
      ContentType: data.type,
      Bucket: uploadBucket,
      Key: filename,
      Body: buffer,
      ContentEncoding: 'base64',
      ACL: 'public-read',
    });
    await out.promise(); // putObject is following old callback pattern.
  }
  catch(err){ result = false; }
  return {
    "statusCode": result? 200 : 500, "isBase64Encoded": false,
    "headers": { "Access-Control-Allow-Origin": "*" },
    "body": JSON.stringify({ filename, url: url + filename })
  }
};
