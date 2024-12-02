# Tucana by Sibel Health 
# QA Automation


### Pre-requisites
- Install Python 3.10: https://www.python.org/downloads/release/python-3100/
- Install Poetry: https://python-poetry.org/docs/
- On Windows if you need Microsoft Visual C++ 14.0 https://learn.microsoft.com/en-US/cpp/windows/latest-supported-vc-redist?view=msvc-170 


### Installing dependencies
 ```poetry install```

### To execute tests locally:
Execute the following command, by replacing \<TAG\> by any scenario tags you would like to execute, the environment by default is dev but if you want to specify it, you can use the env parameter inside the command line:
```
behavex -t API -t HEALTH -D browser=chrome -D env=<qa or dev>
```

### To execute tests inside a CI env:
Execute the following command, by replacing \<TAG\> by any scenario tags you would like to execute:

```
behavex -t API -t HEALTH -D browser=chrome -D headless_browser -D env=<qa or dev>
```

### Sending a final resume to your Slack channel 

First you need to configure your webhook inside Slack and add a system variable called
```
SLACK_WEBHOOK = "XXXXX_your_webhook"
```
Then add -D always_notify_slack inside the command when you run behavex 

Example:
```
behavex -t API -t HEALTH -D browser=chrome -D always_notify_slack -D env=<qa or dev>
```

### Testing solution documentation
As the testing solution consists of a wrapper (called BehaveX) on top of Python Behave, please take a look at the Behave documentation:
https://behave.readthedocs.io/en/stable/

