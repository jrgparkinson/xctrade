# XC Trade

For details of how the app works, see [https://github.com/jrgparkinson/xctrade/wiki](the wiki)

# Developer instructions
Please get involved if you have an idea to improve the app! Simply fork this repository then submit a pull request with your change. See below for more details of how the app works...

This app consist of a python backend (using [https://www.djangoproject.com/](Django)) and a JS front end ([https://reactjs.org/](ReactJS)). The design is based on [https://material-ui.com/](Material).

In production, the JS front end is compiled and minified, then served from the Django static files path.

In development, you can run the two separately to take advantage of the livereloading of JS changes.

```bash
python manage.py runserver # will typically run at http://127.0.0.1:8000/
npm run start # will typically run at http://localhost:3000/
```

Head to `http://localhost:3000/` to view the app. 

## Deploying
Following any commit to the `master` branch, the app is automatically deployed to [https://xctrade.herokuapp.com/](Heroku). 

## Prerequisites
This app requires [https://www.python.org/downloads/](Python 3) and [https://nodejs.org/en/](Node.js). 

Check these are installed and available:
```bash
node -v
npm -v
python --version
```
The app has been tested with `Python 3.6.9`, `Node v12.16.2`, `npm 6.14.4` but should work with the latest available software.

Having installed python, node, and npm:

1. Setup python virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Install node modules
```bash
npm ci
```

3. Create Django DB
```bash
python manage.py migrate
```

4. (optional) pre-populate DB with some example data
```bash
python manage.py populate
```

You should now be able to launch the app with

```bash
python manage.py runserver
npm run start
```

The `npm` command should tell you where it is running the site - head their in your browser.

## Useful commands

After changing the Django models
```bash
python manage.py makemigrations && python manage.py migrate
```

For linting the JS code
```bash
npm run lint
```

To fix issues with number of file watchers exceeded
```bash
sudo sysctl -w fs.inotify.max_user_watches=524288
```
