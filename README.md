<p align="center"><h1>SpaceBot&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://image.flaticon.com/icons/svg/2111/2111370.svg" alt="drawing" width="100"/></h1></p>

<!-- # SpaceBot  -->
**A Discord bot for fun using the [discord.py API](https://discordpy.readthedocs.io/en/latest/index.html#)**

## Demo (more coming soon)
<p align="center"><img src="./assets/demo1.png" alt="graph"/>
  <p align="center"><i>roll, max, and 8b commands</i></p><br/>
</p>
<p align="center"><img src="./assets/demo2.png" alt="graph"/>
  <p align="center"><i>flip, scramble, and ping commands</i></p><br/>
</p>

## Commands
**/ping** - Ping SpaceBot's latency <br/>
**/max** - Display @user's most commonly used phrase <br/>
**/8b** - Ask the magic 8ball a question <br/>
**/say** - Tell SpaceBot something to say <br/>
**/flip** - Flip a coin <br/>
**/roll** - Roll up to 163 die <br/>
**/scoreboard** - Display the die-rolling leaderboard <br/>
**/scramble** - Scramble @user's messages for up to 60 seconds <br/>
<br/>
*And more...*

## Tech
- [discord.py API](https://discordpy.readthedocs.io/en/latest/index.html#)
- [MongoDB](https://www.mongodb.com/)
  - [BSON Custom Encoder](https://api.mongodb.com/python/current/examples/custom_type.html)
- [Google Text-to-Speech](https://pypi.org/project/gTTS/)
- [Heroku](https://www.heroku.com/)
- Automated data collection and other background tasks

## Running the bot
- SpaceBot is not available for public use
  - Feel free, however, to use the source code in your own `discord.py` bots

<p align="center"><h2>Heroku&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<img src="https://www.flaticon.com/svg/static/icons/svg/873/873120.svg" alt="drawing" width="50"/></h2></p>

<!-- ## Heroku Commands  -->
- Deploy: `git push heroku master`
- ssh: `heroku ps:exec --dyno=worker.1`
  - With `vim`: `heroku vim`
    - [Source](https://stackoverflow.com/questions/12666799/what-text-editor-is-available-in-heroku-bash-shell) (`heroku plugins:install @jasonheecs/heroku-vim`)
- Logs: `heroku logs --tail`
- Config Vars: `heroku config`, `heroku configt:get {VAR}` `heroku config:set {VAR}={VAL}`
- Copy remote files: `heroku ps:copy {FILENAME}`
- [Dyno management](https://devcenter.heroku.com/articles/dynos)


### Resources
  - Credits go to [@Lucas](https://www.youtube.com/watch?v=nW8c7vT6Hl4) and [@Tech With Tim](https://www.youtube.com/watch?v=xdg39s4HSJQ&) for the Discord Bot tutorials.
  - Credits go to [@Tech With Tim](https://www.youtube.com/watch?v=rE_bJl2GAY8&) for the MongoDB/PyMongo tutorial.
