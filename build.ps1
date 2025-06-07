uv add -r ./requirements.txt
#pyinstaller --onefile -w --add-data="./400.html;./" --add-data="./homepage.html;./" --add-data="./not_found.html;./" --add-data="./template.html;./" .\potdict.py --ico="./ico.png" --distpath="./"
# pyinstaller ./potdict.spec
pyinstaller --windowed --add-data="./data/*;./data" --ico='./data/app.ico' --name='potdict' --noconfirm ./app.py

<# Remove-Item -Path "E:/apps/potdict/" -Recurse -Force
copy-item './dist/potdict/*' 'E:/apps/potdict/' -Recurse -Force #>