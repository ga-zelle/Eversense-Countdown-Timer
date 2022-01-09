# Eversense-Countdown-Timer
Tells you when to attach the reloaded Transmitter so it is best synchronised with AAPS

You need to have python on the AAPS phone, e.g. QPython3L.
You put the script in the scripts folder, e.g. scripts3 for above example

Method:

The transmitter should be placed 90-120 sec before the regular loop event extrapolated from recent logfile history.
After starting the script you enter your favorite time gap. Mine is 95 sec, therefore the default setting.
However, it could be different for you and also depends on how quickly you find the optimal position above the sensor.

Limitations:
- new logfile started and no loop executed since then : not fatal
- last loop was at irregular time due to special event like target change or profile change: wrong synschronisation
- Android 11+ : crashes; you may use an AAPS3.0dev version in other branch 
