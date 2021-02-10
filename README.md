# Pony-WTF
# This package is dead prematurely, still you can use in your own responsibility. PR is most welcomed

Pony-WTF is an integration library for Ponyorm and WTF-Forms.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install pony_wtf
```

## Usage


```
# imports from pony-wtf
from pony_wtf import model_form
from pony_wtf.utils import get_attrs_dict


# declare database entities
class User(db.Entity):
    id = PrimaryKey(int, auto=True)
    email = Required(str, unique=True)
    age = Optional(int)

form_cls = model_form(User, ) 
form = form_cls()

def get_form_values(entity, form_data):
    """ Get form values and return them as dict """
    d = {}
    adict = get_attrs_dict(entity)
    for k in adict:
        if k in form_data:
            d[k] = form_data.get(k)
    return d


@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form_cls = model_form(User)
    form = form_cls()  # instaniatte the class

    if request.method == 'POST' and form.validate_on_submit():
        data = get_form_values(User, form.data)
        with db_session:
            User(**data)
        flash("User Created", "success")
        return redirect(url_for("index"))
    return render_template('create_user.html',  form=form)
```

You can render the form as you prefer in the jinjaHTML.
Ex:
``` {# Use Flask-WTF and Flask-Bootstrap #}
    {{ wtf.quick_form(form) }}
```

## Requirements
```
pony
pony_wtf
Flask_WTF
WTForms
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)
