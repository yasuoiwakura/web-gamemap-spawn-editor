rmdir /s /q ".aws-sam"
call sam build --no-use-container
sam deploy --profile=myawsprofile --force-upload --no-confirm-changeset
