pip install -r ./requirements.txt
#pyinstaller --onefile -w --add-data="./400.html;./" --add-data="./homepage.html;./" --add-data="./not_found.html;./" --add-data="./template.html;./" .\potdict.py --ico="./ico.png" --distpath="./"
pyinstaller ./potdict.spec

try 
{
    Remove-Item "./PotDict.exe" -Force -Confirm:$false    
}
catch 
{
    Write-Host "./PotDict.exe not found"
}
Move-Item "./dist/PotDict.exe" "./"

Remove-Item "./build" -Recurse -Force -Confirm:$false
Remove-Item "./dist" -Recurse -Force -Confirm:$false