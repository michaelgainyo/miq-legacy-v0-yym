# miq-legacy-v0-yym

## To install

1. Create a new folder in your working directory and clone the project

```
git clone https://github.com/michaelgainyo/miq-legacy-v0-yym.git
```

2. Move into the new folder

```
cd miq-legacy-v0-yym
```

3. Create a new environment in your working directory with the following commands. Replace `<env-name>` by a name of your choice.

```zsh
python3 -m venv <env-name>
source <env-name>/bin/activate
```

4. Install required dependencies

```zsh
pip3 install -r requirements.txt
```

5. Migrate and create a superuser

```zsh
./manage.py migrate
./manage.py createsuperuser
```

6. In the terminal, run the following commands.

```zsh
./manage.py shell
```

7. Paste the following code and hit enter

```zsh
from django.contrib.sites.models import Site
Site.objects.first().save()
exit()
```

8. Run the server and head over to <http://127.0.0.1:8000/>

```zsh
./manage.py runserver
```

9. Voila
