whatsapp-parser
===============

Parser to the What's App log file.

### Dependencies ###
- Python 2.*

### Input ##

A Whatsapp history file and an optional list of regular expression patterns.

### Output ##

- Several statistics about the message history and the frequency of each pattern.
- A JSON file is created within /logs/ folder.

### Usage Steps ####
- Export your Whatsapp history. (http://www.whatsapp.com/faq/general/23753886)
- Clone this repository.
- For simplicity only, put the history file in the same folder of the cloned repository.
- Open your terminal and execute:

```
python main.py TextFileNameHere.txt [regex. patterns]
```

### Example ###
```
python main.py Chat.txt sleepy yes
```

- Expected output:

```
--PROPORTIONS
 total_messages -> 32773
 total_words -> 172760
 total_chars -> 899435
 messages
   Marilia Ferreira -> 16234
   ‪Nikolas Moya -> 16539
 words
   ‪Nikolas Moya -> 72797
   Marilia Ferreira -> 99963
 chars
   ‪Nikolas Moya -> 379642
   Marilia Ferreira -> 519793

--SHIFTS
 morning -> 2581
 afternoon -> 6593
 evening -> 9736
 latenight -> 13863

--WEEKDAY
 Wednesday -> 4155
 Thursday -> 4319
 Monday -> 4638
 Saturday -> 4650
 Tuesday -> 4730
 Friday -> 4874
 Sunday -> 5407

--AVERAGE MESSAGE LENGTH
 ‪Nikolas Moya -> 4.40153576395
 Marilia Ferreira -> 6.1576321301

--PATTERNS
  sleepy
   ‪Nikolas Moya -> 10
   Marilia Ferreira -> 5
 yes
   ‪Nikolas Moya -> 98
   Marilia Ferreira -> 87

--TOP 15 MOST USED WORDS (length >= 3)
não
amor
mais
hahaha
sim
muito
isso
amo
para
tudo
hahah
acho
agora
aqui
tava
./logs/Chat.txt.json