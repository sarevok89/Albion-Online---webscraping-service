# Albion-Online---webscraping-service
## This is a webscraping service, which allows users fetching data from Albion Online killboards page and saves it in an output Excel file. Check it out [here](http://albion-compensations-app.herokuapp.com/).

I created this web app as a hobby project for my computer game Albion Online.
Very often in this game guilds pay back for their members gear if they die in battle. Players provide their leaders links
to their "killboard" page, i.e. https://albiononline.com/en/killboard/kill/39282911.
I found it very time consuming vising every link, reading data manually and putting it in an Excel file,
so I decided to automate it for myself and soon to deplou it as a free Albion data fetching web application.

## Getting started:
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. 

### Installation of requirements:
```
pip install bs4
pip install Selenium
pip install Pandas
pip install boto3 boto botocore
pip install Django
pip install django-storages
pip install django-crispy-forms
pip install gunicorn
pip install Pillow
pip install html5lib
pip install XlsxWriter
```

## Creating this web app I learned/improved my knowledge of using following modules and packages:

### 1. BeautifulSoup and json:
To create a .json file containing all items available in Albion Online, so I could easily translate
computer generated item names, to more user friendly, i.e. "T5_2H_HOLYSTAFF_HELL" to "Fallen Staff". I took the data from
http://www.albionchest.com/

### 2. Regular Expressions module:
I decided to use it, because people could paste their links with some other random stuff, since they could be
copying them from i.e. Discord app, or online forum. To handle all exceptions I created a function,
which is looking for specified patterns in their input and if found, appends them to a list.

![screen](https://user-images.githubusercontent.com/22706780/52182193-eb082e80-27fa-11e9-9072-61fc06e96a91.jpg)

### 3. BeautifulSoup and Selenium with Selenium webdriver:
Those I had to use to actually visit every link provided by user and fetching the website data,
which was dynamically generated by javascript.

![get_links](https://user-images.githubusercontent.com/22706780/52182109-eabb6380-27f9-11e9-830d-39eae1884ef2.jpg)

### 4. Object Oriented Programming:
I created special classess as blueprints, since every "killboard" contained the same kind of data, i.e. player nickname, guild,
item power, helmet, armor etc. Doing it this way I could then easily generate a dictionary to store all data.

### 5. Json module, Pandas Dataframes and Pandas ExcelWriter:
I used prevously created .json file, to actually translate all data fetched and then saved it all in Pandas Dataframe. Then with use of Pandas ExcelWriter I put everything in an Excel file, previously configuring it, to make columns with specified width and
text centered.

![screen](https://user-images.githubusercontent.com/22706780/52182174-a5e3fc80-27fa-11e9-985d-03644988a164.jpg)

### 6. Datetime module:
Each filename is generated taking user input and also by adding current day's date e.g. 'day-month-year - <fight_name>.xlsx'

### 7. Amazon S3 server and boto, boto3, botocore modules:
Since Heroku deletes all user upload files every time it restarts we need to store our files on an outside server,
which in this case is Amazon S3. ExcelWriter doesn't allow us to directly create files on S3, so we temporarily create them on Heroku and upload to S3 right after that.

We don't want our files to get overwritten in case user provided the same names for all the files generated on the same day, so each time we check, if a file with a name we want to provide already exists on S3 server. We consecutively add a number to a file's name and check again. We keep checking until we find a name that doesn't yet exist, e.g.: '13-2-2019 - onix vs squad(3).xlsx'.

### 8. Django with Pillow and crispy-forms, HTML, CSS:
Finally I put it all together using Django. I created a website, where users can create their accounts with profiles, which later store all their generated files. All forms are nicely rendered using Django crispy-forms. Whenever users upload a profile picture it gets scaled down to required size using Pillow module.

![your_files](https://user-images.githubusercontent.com/22706780/52182123-235b3d00-27fa-11e9-888e-090c1dc978de.jpg)

## Plans and ideas:

### I started working on adding multiprocessing to actually speed it all up, since fetching data from i.e. 50 links takes about 8 minutes. Using 7 cores of my CPU I managed to get it down to less than 1 minute, but there are still some issues with it.

### I'm also working on implementing Python Celery module, so users won't need to wait for the file to generate. They are going to be moved to the main page and file creation is going to be handled as a background process. Once it's all done users will recieve a notification.

### In near future I'm going to move my website from Heroku, to a proper server.
