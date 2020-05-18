<B>The front-end folder holds all code relevant to the web application part of this project.</B>

* app.py TODO

* The folder <i>templates</i> holds all the html files that the app.py file renders. Its contents are:
  1. <i>display.html <br>
  This file is rendered whenever the user goes to the display page of the web application, i.e. whenever the user presses the display button of a trained model. It handles all things concerning the graph.

  <br>

  2. layout.html <br>
  This file holds the html code for the basic layout that is consistent through all html pages. This file is included in all other pages of the web application. <br>

  3. login.html <br>
  This file is rendered whenever the user goes to the login page of the web application. It handles all things concerning the login screen.

  4. train.html <br>
  This file is rendered whenever the user goes to the training page of the web application. It is responsible for all things training on the web app. It saves its form and the data stored upon clicking the submit button which then the app.py file can use to train a model.

  5. includes \<folder>
    1. _messages.html <br>
    TODO
    2. _navbar.html <br>
    This file holds the html code representing the navbar on all pages of the web application. All other html files that describes what a page should look like, should always include this file.  
