from wtforms.widgets.core import html_params
import string
from wtforms import widgets
import random

class ChosenSelectWidget(widgets.Select):
    """
        `Chosen <http://harvesthq.github.com/chosen/>`_ styled select widget.

        You must include chosen.js for styling to work.
    """

    def __call__(self, field, **kwargs):
        if field.allow_blank and not self.multiple:
            kwargs['data-role'] = u'chosenblank'
        else:
            kwargs['data-role'] = u'chosen'

        return super(ChosenSelectWidget, self).__call__(field, **kwargs)


class JsonWidgetBase(object):
    
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        super(JsonWidgetBase, self).__init__()
    
    def __call__(self, field, **kwargs):
        kwargs.update(self.kwargs)
        
        kwargs.setdefault('id', field.id)
        html = [
            # read file embed its content
            # or create url_for
            # <style> + file content + </style>
            """<!-- You should include jsonTree, jsonCss
            download it  from
            https://raw.githubusercontent.com/summerstyle/jsonTreeViewer/master/libs/jsonTree/jsonTree.js
            https://raw.githubusercontent.com/summerstyle/jsonTreeViewer/master/libs/jsonTree/jsonTree.css
            
            "<link href='libs/jsonTree/jsonTree.css' rel ='stylesheet' />",
            "<script src ='libs/jsonTree/jsonTree.js' ></script>" */ -->
            """
        ]
        # render the select
        # html.append(super(JsonWidget, self).__call__(field, **kwargs))
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        
        kwargs["data-id"] = ''.join(random.choices(string.digits, k=15))
        kwargs["data-json"] = "true"
        html.append ('<textarea %s>\r\n%s</textarea>' % (
            html_params(name=field.name, **kwargs),
            
            field._value()
        )
        )
        html.append("<script>"+
            """\ndocument.addEventListener(
                "DOMContentLoaded",
                () => {"""
                +
                """var wrapper = document.body.querySelector("""
                +
                    "'[data-id=\"" + kwargs["data-id"] + "\"]')"
                +
                """\n 
                console.log(wrapper, wrapper.value)
                var dataStr = wrapper.value
                try {
                    var data = JSON.parse(dataStr);
                    var tree = jsonTree.create(data, wrapper);
                    tree.expand()
                    console.log(tree)
                } catch (e) {
                    console.log(e)
                }
                // Create json-tree
                
                }
            )
            </script>\n""")
        
        # return the HTML (as safe markup)
        return'\n'.join(html)

    
class JsonWidget(JsonWidgetBase):
    def __init__(self, *args, **kwargs) -> None:
        if not kwargs.get("rows"):
            kwargs["rows"]=20
        
        super(JsonWidget, self).__init__(args, kwargs)
