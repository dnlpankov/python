# launch it to automaticall send files to github

conda activate aweber
cd aweber
pip freeze > requirements.txt
git add .
git commit -m "update requirements"
git push origin main

