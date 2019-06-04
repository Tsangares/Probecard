### How to create a new daq

 1) Duplicate and rename the file `ExampleDaq.py` from the `probecard/daq/` folder and use it as a template daq.
 2) Write the protocol of the daq using the functions available to you from the `BaseProbecardThread.py`. Note there are some functions only avialable to you in the `probecard/daq/utilities/controller.py` like `setGroundMode` that you can acces from your daq code by referencing `self.controller` like `self.controller.setGroundMode(False)` or `self.controller.getResistance()`. Look at `probecard/daq/SinglePixelDaq.py` as an example.
 3) Once you have created your daq filem you need to attach it to the main menu at `probecard/probecard.py`. In the function `startExperiment` located in the class definition of `Gui`, find the state you want your daq to run on like `msg=='all'` or `msg=='calib'` and create an instance of your daq, and connect `newData`,`done`, and `log` signals to the window functions `addPoint`, `finalize`, `log` respectivly. You can look at `msg=='single'` as an example. Then start your daq.
 4) If you need some unique parameters from the main menu, then add a state widget after the `TwoPaneWindow` is instantiated. Example: ```menuWindow.addStateWidget(states['single'],(QLabel('Channel Number (N)'),menuWindow.getLineEdit('channel_number')))```.

