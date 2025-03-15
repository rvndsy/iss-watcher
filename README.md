### What?

*iss-watcher* is a CLI tool to find the following passover dates and times of the International Space Station (ISS) at any given location on Earth. A passover means you can physically see the space station as a bright white 'star' near dusk or dawn in the (clear) sky that is typically visible for a couple minutes.

### Why?

This project was originally made for a github and automatization course in university. Snippets of code are taken from the lecture materials with given permission to use the code within the project.

### Dependencies:

Currently this project only has been tested on Linux. However it should also work on Windows with minimal problems.

- [mariadb 11.2.2-1](https://archlinux.org/packages/extra/x86_64/mariadb/) (MySQL will also work)
- [python 3.11.6-1](https://archlinux.org/packages/core/x86_64/python/)

### Set-up and Running

1. Set up a MariaDB or MySQL database locally with the default port `3306`.

2. Move `./config.ini.template` to `./config.ini` and set-up necessary values. For this step you will need an N2YO API key. You do not need an API key for OSM.

3. Create a database (with SQL) according to the `mysql_db = ` variable under section `[mysql_config]` within `./config.ini`.

4. Run `./prepare_dev_env.sh`. That should automatically run database migrations, some sourcecode tests and other checks.

5. Run `./main.py`. 

### Issues when running

- If receiving code `403` from OSM API, then you may have to update the user agent to some other value in the config:

```
[request_headers]
user_agent = Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36
```

### Api's that are being used:

- To translate location names into coordinates for N2YO: https://nominatim.openstreetmap.org
- To acquire ISS passover dates and times: https://www.n2yo.com/api/#visualpasses
