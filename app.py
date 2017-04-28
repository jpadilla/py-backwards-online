import textwrap

from flask import Flask, render_template, request
from py_backwards.transformers import transform
from py_backwards.const import TARGETS


app = Flask(__name__)

SOURCE_CODE = textwrap.dedent(
    """
    def returning_range(x: int):
        yield from range(x)
        return x


    def x_printer(x):
        val: int
        val = yield from returning_range(x)
        print(f'val {val}')


    def formatter(x: int) -> dict:
        items: list = [*x_printer(x), x]
        print(*items, *items)
        return {'items': items}


    result = {'x': 10, **formatter(10)}
    print(result)


    class NumberManager:
        def ten(self):
            return 10

        @classmethod
        def eleven(cls):
            return 11


    class ImportantNumberManager(NumberManager):
        def ten(self):
            return super().ten()

        @classmethod
        def eleven(cls):
            return super().eleven()


    print(ImportantNumberManager().ten())
    print(ImportantNumberManager.eleven())
    """
)


@app.route('/', methods=['POST', 'GET'])
def index():
    source = SOURCE_CODE
    target = request.args.get('target', '2.7')

    if request.method == 'POST':
        source = request.form['source']
        target = request.form['target']

    try:
        path = '/tmp/file.py'
        transformed = transform(path, source, TARGETS[target]).strip()
        error = None
    except Exception as exc:
        transformed = ''
        error = exc

    data = {
        'source': source,
        'transformed': transformed,
        'error': error,
        'targets': TARGETS.keys(),
        'selected_target': target
    }

    return render_template('index.html', **data)


if __name__ == '__main__':
    app.run(debug=True)
