### Label Studio

Need to make sure that data in the s3 bucket are:
1. Public
2. The bucket has a CORS policy set so that label studio can remotely load tasks.

Check the CORS policy with:
```sh
 s3cmd -c ~/s3/s3cfg.stfc info s3://mast 
```

Set the CORS policy with:
```sh
s3cmd -c ~/s3/s3cfg.stfc setcors cors.xml s3://mast 
```