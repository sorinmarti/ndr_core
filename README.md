# ndr_core
NDR-Core django libraries

- Create virtualenv
- install requirements (pip install -r requirements.txt)

```
python manage.py collectstatic
python manage.py runserver
```
Note: If templates change, no action is needed.If static files change, the 'collectstatic' command has to be executed.

If you want to use gunicorn with WSGI, use the following command:
```
gunicorn ndr_core.wsgi -b 127.0.0.1:PORT -D
```
(Where PORT is the port you want it to run on. Be aware that 8001 and 8002 are used for divisive-power.org and asia-directories.org)
The -D option starts it as a daemon. It may be better to do it without to easily start and stop it.


In general, all static templates for dpcl are in ```main/templates/main/```, all ndr_core templates are in ```ndr_core_api/templates/ndr_core_api/```.In the same fashion, static files (images, js, css) are in ```main/static/main/```and ```ndr_core_api/static/ndr_core_api/```.

The basic page for ndr_core is  ```ndr_core_api/templates/ndr_core_api/base/base_default.html```. ```main/templates/main/base.html``` extends this template and is the base for all dpc pages.

Jumbotrons, forms and cards are rendered by ndr_core. The templates are to be found there.
The resultlines are rendered with ```main/templates/main/result_line_xy.html``` (where xy is dpc, asiadir or haka for the three result types)
