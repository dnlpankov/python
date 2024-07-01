# launch it to automaticall send files to github

# part of the code on my laptop
conda activate aweber
cd aweber
# pip freeze > requirements.txt
conda env export --from-history > environment.yml









git add .
git commit -m "update requirements"
git push origin main

# part of the code on linux droplet

sftp deploy@64.226.107.42

cd python/aweber
put /Users/danila/github/python/aweber/aweber_credentials.json
put /Users/danila/github/python/aweber/aweber_tokens.json
put /Users/danila/github/python/aweber/postgres_credentials.json



git pull
# conda create --name aweber --file ./aweber/package-list.txt
# to upgrade the environment
conda env create -f environment.yml
/home/deploy/miniconda3/envs/aweber/bin
crontab -e

#/home/yourusername/miniconda3/envs/aweber/bin/python /home/yourusername/your-repo/your_script.py >> /home/yourusername/your-repo/cron.log 2>&1


0 2 * * * /home/deploy/python/aweber/get_data.py /home/yourusername/your-repo/your_script.py >> /home/yourusername/your-repo/cron.log 2>&1
