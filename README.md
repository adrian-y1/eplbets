# **EPLBETS - CS50x Final Project 2021**
### Eplbets is an English Premier League betting app that lets you place bets on upcoming games. 
### Navigate [here](http://adriann.pythonanywhere.com/) to explore it and start betting!
### There are several different pages in Eplbets and they are: 
- ####   Homepage
- ####   Login
- ####   Register
- ####   Change Password
- ####   My Bets
- ####   Matches
- ####   Checkout
- ####   Leaderboard
- ####   Results

### Lets start with Homepage.

## **Homepage**

### Homepage is well... the "Homepage" when you visit the website. When users visit your website, homepage is what sets the tone of your website because its the first thing they see. Making a simple homepage with a clear message is what makes users stick around to see what your website has to offer. Finding a suitable background with the right colour schemes and font took me some time but it was worth it in the end. In the homepage, users will be able to *Login*, *Register* or *Change Password*. This brings us to the next page, Login.

## **Login**

### In *Login*, users will be able to Log into their respective accounts that they have created. Users can navigate to *register* or *Change Password* routes through the Login page.


## **Register**

### In *Register*, users will be able to create their Eplbets account and start with $1,000 to bet. Users can navigate to *Login* and *Change Password* pages through the register page.


## **Change Password**

### In *Change Password*, users will be able to change their current password if they happen to forget it or just wanting a new one. Through *Change Password*, users can navigate to *Login* or *Register* pages.


## **My Bets**

### *My Bets* is page that keeps track of every bet you have placed. There two secions to *My Bets*; **Pending** and **Resulted**. 
- ### Pending
    - #### When clicking on the **Pending** section, it will display all bets that you have placed which are still pending and have not resulted yet. This means that the games in which you have placed the bet on, have not finished playing yet.

- ### Resulted
    - #### When clicking on the **Resulted** section, it will display all bets that you have placed which are resulted in an outcome. There are 2 outcomes *Won* or *Lost*. If your status is classified as "Won", that means you have won your bet and will receive the money specified. Else if your bet's status is classified as "Lost", you will not receive anything.

### In My Bets, the information display on each bet are as follows:
- #### Leg Chosen
- #### Odds
- #### Teams Playing
- #### Match Date
- #### Stake
- #### Potential Payout
- #### Status
- #### Transaction Date


## **Matches**

### In *Matches*, users are able to view a list of upcoming English Premier League matches including other important information such as:
- ### Teams Playing
- ### Match Date
- ### Odds of each leg
- ### Flag of the teams
### To choose a leg to bet on, users will need to click the button of their desired choice which then will be redirect to...*Checkout*.

## **Checkout**

### Here, users will be able to place the amount they desire on their their respective leg that they have chosen. Through this, users will also be able to see the potential payout of the amount they type before they place the bet. There are alsoo other information displayed on this form such as:
- ### Leg
- ### Odds
- ### Teams Playing
- ### Match Date

## **Leaderboard**

### In *Leaderboard*, users will be able to compete in order to stay at the top of the leader to receive the respective prizes. Prizes vary in the Top 3. No.1 takes $150, No.2 takes $100 and No.3 takes $50. Ranking are determined by total balance. At the end of each Matchday of the English Premier League, the Top 3 users will get the rewards. This makes users think of who is the best team/leg to place a bet on in order to stay at the top of the leaderboard and win prizes.

## **Results**

### In *Results*, users will be able to view the results of all matches that have been completed and their date. This allows users check the score of the matches they have placed bets on. 

## **Design Choice**
### My design choice was inspired by the popular Australian bookmaker, [Sportsbet](https://www.sportsbet.com.au/). At first, i had designed the *Matches* and *My Bets* pages to have the data in the form of a table, however i figured that it didnt look great and users would not have been happy with that. With that, i decided to format the data in a card like design where there is one "card" for each game and/or bet. Colour schemes was the more challenging part of the design phase for me. At first, my pages were very bland with 1 background for all of them. Given that, i decided to make different colours for each section of that website.  

## **Difficulties faced**

### There were lots of ups and downs when working on this project. And at times i even questioned if i had the capability and knowledge to finish it. The main struggle i had was with using two different APIs. One of the most difficult things working with two different APIs was data comparison. Other difficulties i had was my database. Halfway through my project, i had to change my entire database design as i realised it was not fit for what i was trying to do. 

## **Future Plans**

### I have some plans for the future of this project where i want to expand the horizon. Although currently, this website strictly revolves around the English Premier League, i want to expand and implement other soccer compeitions to give users a variety of different competitions to bet on.


## **Conclusion**
### I spent a tremendous amount of time and effort on this project and it paid off. I am personally happy with what i have accomplished and seeing others like it made me even happier and motivated to keep on improving and doing better. I have learnt alot of things from this project and CS50x in general that i plan to use in the future as i will be taking the follow-up course of CS50W.

## **Reference**
### Thanks to [Sportsbet](https://www.sportsbet.com.au/) for the inspiration, and thanks to [SerpApi](https://serpapi.com/?gclid=CjwKCAiAs92MBhAXEiwAXTi250gOYFMGhpjYIHuaHpi_iLoxLRr40Vjztu4WgpDrHW3BEyiNinIaghoCTiQQAvD_BwE) and [The Odds Api](https://the-odds-api.com/) for the APIs.


