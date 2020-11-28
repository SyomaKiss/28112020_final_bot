sudo apt update
sudo apt install ffmpeg
# BIG model
#wget https://alphacephei.com/vosk/models/vosk-model-ru-0.10.zip
#unzip vosk-model-ru-0.10.zip
wget https://alphacephei.com/vosk/models/vosk-model-small-ru-0.4.zip
unzip vosk-model-small-ru-0.4.zip
mv vosk-model-small-en-us-0.4 model
pip install pyTelegramBotAPI vosk

