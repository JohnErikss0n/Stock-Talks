# Stock-Talks
A real time Google Home application that makes your portfolio more accessible, using Dialogflow.
#Inspiration
We were inspired when we were cooking chicken and wanted to check our Nvidia holdings after an earnings report. We then thought about how inaccessible stock following is, as it tends to require the user to read. Our project allows visually impaired users to gain insight into the world of finance and investing on their own.

#What it does
Stock Talks uses Natural Language Processing to generate an interactive stock following experience. The program can return a number of parameters to the user, such as return, average return, etc.

#How I built it
We built Stock Talks by using Diagflow to process user inputs, sending a POST to our webhook. We then used Flask to process the request, and returned a json file to Diagflow in order to generate an audio response at the Google home.

#Challenges I ran into
Processing the POST request was a great challenge that required the team to work together in order to solve. We were all unfamiliar with the problem, so when we managed to develop a solution it was a source of great bonding and pride.

#Accomplishments that I'm proud of
Our biggest accomplishment would be the successful training of the application to recognize the appropriate parameters (ex. being able to determine that Disney is the stock parameter in the string "Add Disney to my portfolio")

#What I learned
I learned how to develop webhooks through use of flask and ngrok libraries.

#What's next for Stock Talks
Integration of a robo-advisor using Tensorflow and matplotlib to help novice investors generate their best returns.
