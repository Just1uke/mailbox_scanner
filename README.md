# Mailbox Scanner

#### Setup: 

##### Installation

```commandline
cp config.yaml.example config.yaml
vi config.yaml
pip install -r requirements.txt
```

##### Authorization

You will need to register your application at Microsoft Apps(https://apps.dev.microsoft.com/). Steps below

You will need to register your application at Microsoft Apps(https://apps.dev.microsoft.com/). Steps below
1. Login to https://apps.dev.microsoft.com/
2. Create an app. Your AppID should be recorded in your configuration file under application_id
3. Under "Application Secrets", click "Generate New Password". Record this password in your configuration under client_secret
4. Under the "Platform" section, add a new Web platform and set "https://outlook.office365.com/owa/" as the redirect URL
5. Under "Microsoft Graph Permissions" section, Add the below delegated permission
    1. email
    2. Mail.ReadWrite
    4. User.Read

#### Running

```commandline
python main.py ./config.yaml
```