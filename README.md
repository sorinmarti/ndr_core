# ndr_core
NDR-Core django libraries

- Create virtualenv
- install requirements (pip install -r requirements.txt)

```
python manage.py collectstatic
python manage.py runserver
```

In general, all static templates for this page are in ```main/templates/main/```, all ndr_core templates are in ```ndr_core_api/templates/ndr_core_api/```.In the same fashion, static files (images, js, css) are in ```main/static/main/```and ```ndr_core_api/static/ndr_core_api/```.

The basic page for ndr_core is  ```ndr_core_api/templates/ndr_core_api/base/base_default.html```. ```main/templates/main/base.html``` extends this template and is the base for all dpc pages.
