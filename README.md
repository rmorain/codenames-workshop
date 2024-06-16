# codenames-workshop
## Requirements for provided AI client (word2vec)
* Install requirements: `pip install -r requirements.txt`
  * Requires scipy **version 1.12** (included in requirements.txt)
* Download https://www.kaggle.com/datasets/leadbest/googlenewsvectorsnegative300
  * Extract .bin and place in client/ folder

# Deploying changes to production server
After you have pushed changes to the repository on Github, you can deploy that code to the production server following these instructions.
## Connect to production server
On Linux:

`ssh -i path/to/production.pem ubuntu@codenames.click`
## Pull code from Github repository
`git pull`
## Restart codenames service
```
sudo systemctl restart codenames
```

*That's it!*
