# codenames-workshop

# Deploying changes to production server
After you have pushed changes to the repository on Github, you can deploy that code to the production server following these instructions.
## Connect to production server
On Linux:

`ssh -i path/to/production.pem ubuntu@codenames.click`
## Pull code from Github repository
`git pull`
## Reload daemon and restart codenames service
```
sudo systemctl daemon-reload
sudo systemctl restart codenames
```

*That's it!*