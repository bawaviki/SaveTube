pip3 install pyinstaller
pyinstaller savetube.py -i icon.ico -w --uac-admin
md dist\savetube\Savetube\GUI
cd Savetube/GUI/
copy *.png ..\..\dist\savetube\Savetube\GUI\*.png
copy *.gif ..\..\dist\savetube\Savetube\GUI\*.gif
