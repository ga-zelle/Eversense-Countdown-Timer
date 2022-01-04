# Count down timer for re-attaching the ES transmitter
#
#   Author  Gerhard                 Started 19.Dec.2021
#   adapted from Scan_APS_reasons.py
#
# save this py in the ".../qpython/scripts3/" folder

#import json
import glob, sys, os
import time
from datetime import datetime   #, timedelta

global  maxGapSecs

timeSteps = [120, 60, 30, 20, 15, 10, 5, 1, 0]    # list of countdown announcements to be made
text_no_loop = 'no loop data in fresh logfile.\nUse manual method'
text_gap     = 'How many seconds for gap\n  (0 closes app;  (default: '
text_pause   = 'next reminder in '
text_attach  = 'attach in '
text_Unit    = ' seconds'
text_Check   = '\nactivate location service\n'
text_late    = 'time is up, enter "0" to exit or time gap to rerun this app'

def mydialog(title,buttons=["OK"],items=[],multi=False,default_pick=[0,1]):
    # adapted from "https://stackoverflow.com/questions/51874555/qpython3-and-androidhelper-droid-dialogsetsinglechoiceitems"
    title = str(title)
    droid.dialogCreateAlert(title)
    if len(items) > 0:
        if multi:
            droid.dialogSetMultiChoiceItems(items, default_pick)   # incl. list of defaults
        else:
            droid.dialogSetSingleChoiceItems(items, default_pick[0])
    if len(buttons) >= 1:
        droid.dialogSetPositiveButtonText(buttons[0])
    if len(buttons) >= 2:
        droid.dialogSetNegativeButtonText(buttons[1])
    if len(buttons) == 3:
        droid.dialogSetNeutralButtonText(buttons[2])
    droid.dialogShow()
    res0 = droid.dialogGetResponse().result
    res = droid.dialogGetSelectedItems().result
    if "which" in res0.keys():
        res0={"positive":0,"neutral":2,"negative":1}[res0["which"]]
    else:
        res0=-1
    return res0,res

#Settings for usage on Android:
test_dir  = '/storage/emulated/0/Android/data/info.nightscout.androidaps/files/'
test_file = 'AndroidAPS.log'
inh = glob.glob(test_dir+'*')

if len(inh) > 0:
    IsAndroid = True
    import androidhelper
    droid = androidhelper.Android()
    inh = glob.glob(test_dir+'files/AndroidAP*.log')
    fn = test_dir + test_file
    #fn = inh[0]
    ClearScreenCommand = 'clear'

    ###########################################################################
    #   the language dialog
    ###########################################################################
    btns = ["Next", "Exit", "Test"]
    items = ["Dieses Smartphon spricht Deutsch", "This smartphone speaks English"]
    pick = 0
    while True:                                                             # how the lady speaks ...
        default_pick = [pick]
        pressed_button, selected_items_indexes = mydialog("Pick Language", btns, items, False, default_pick)
        pick = selected_items_indexes[0]
        if   pressed_button ==-1:           sys.exit()                      # external BREAK
        elif pressed_button == 0:           break                           # NEXT
        elif pressed_button == 1:           sys.exit()                      # EXIT
        elif pressed_button == 2:           droid.ttsSpeak(items[pick])     # TEST
    if   pick == 0:
        text_no_loop = 'Keine Loopdaten in frischem Logfile.\nVerwende manuelle Methode.'
        text_gap     = 'Wieviel Sekunden vor dem Loop\n  (0 beendet app; Default: '
        text_pause   = 'nächste Erinnerung in '
        text_attach  = 'Aufsetzen in '
        text_Unit    = ' Sekunden'
        text_Check   = '\nStarte Platzierungshilfe\n'
        text_late    = 'Zeit ist um, gib "0" ein zum Beenden oder Zeit für erneuten Versuch'
    #elif pick == 1:    set as default, also for Windows
    #else:15
    #    Speaker = 'nobody'
    pass
else:
    IsAndroid = False
    test_dir  = 'L:/Dev_Last10/'
    test_file = 'AndroidAPS._2021-12-11_00-00-00_.2'
    fn = test_dir + test_file
    ClearScreenCommand = 'cls'

def new_msg(txt):
    print(txt)
    if IsAndroid:
        droid.ttsSpeak(txt)

def getGapSecs(defaultGap):
    global   maxGapSecs
    #defaultGap = '95'
    maxGap = input(text_gap + str(defaultGap) + ') ? ')
    if maxGap == '':
        maxGap = defaultGap
    if not maxGap.isnumeric():
        print (maxGap + ' was not numeric')
        maxGap = defaultGap
    maxGapSecs = eval(maxGap)


getGapSecs('95')
lcount = 0
thisTime = 'no loop'
lf = open(fn, 'r')
for zeile in lf:
    lcount = lcount + 1
    was_reason = zeile.find('"reason":"')
    
    if was_reason>0:
        was_delivered = zeile.find('"deliverAt":"')
        was_timestamp = zeile[was_reason:].find('"timestamp":"') + was_reason
        if was_delivered>0:                                                     # used in case of SMB
            thisTime = zeile[was_delivered+13:was_delivered+37]                 # incl milliseconds
lf.close()
if thisTime == 'no loop':
    print(text_no_loop)
    maxGapSecs = 0
    
#os.system('cls')    #ClearScreenCommand)    
print ('=== last loop: '+thisTime)
lastLoop = datetime.strptime(thisTime[:-5], '%Y-%m-%dT%H:%M:%S')

while maxGapSecs > 0:
    nowTime = datetime.now()
    nextLoop = nowTime - lastLoop
    secPause = ( - maxGapSecs - nextLoop.total_seconds()) % 300
    if secPause<1:
        time.sleep(2)           # too close for comfort
        new_msg(text_late)
        getGapSecs('0')         # use "0" as normal termination
    else:
        for stepID in range(len(timeSteps)-1):
            if timeSteps[stepID] < secPause:
                waitPause = - timeSteps[stepID] + secPause
                eventInSecs = int(secPause+0.5)
                if IsAndroid:
                    if eventInSecs > 21:
                        droid.ttsSpeak(text_attach + str(eventInSecs) + text_Unit)
                    else:
                        droid.ttsSpeak(str(eventInSecs)+ text_Unit)
                print(text_pause + str(int(waitPause+0.5))+'s, ' + text_attach + str(eventInSecs)+'s')
                if eventInSecs == 30:
                    new_msg(text_Check)
                time.sleep(waitPause)
                break


#################################################
if IsAndroid:       os._exit(os.EX_OK)          # terminate this script OK, but keep others alive
else:               sys.exit()                  # seems to end all python scripts