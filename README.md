# codenames-workshop
## Requirements for provided AI client (word2vec)
* Install scipy **version 1.12** (not current version)
  * `pip install scipy==1.12`
* Download https://www.kaggle.com/datasets/leadbest/googlenewsvectorsnegative300
  * Extract .bin and place in client/ folder

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
