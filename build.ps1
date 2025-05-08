pip install -r ./requirements.txt
#pyinstaller --onefile -w --add-data="./400.html;./" --add-data="./homepage.html;./" --add-data="./not_found.html;./" --add-data="./template.html;./" .\potdict.py --ico="./ico.png" --distpath="./"
pyinstaller ./potdict.spec

Remove-Item "./build" -Recurse -Force -Confirm:$false