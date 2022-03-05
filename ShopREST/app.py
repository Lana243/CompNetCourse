from flask import Flask, jsonify, make_response, request
from flask import abort

app = Flask(__name__)

items = [
    {
        'id': 1,
        'name': u'Jeans',
        'description': u'Woman, dark blue, high waist, skinny',
    },
    {
        'id': 2,
        'name': u'Sweater',
        'description': u'Woman, woolen, Mickey Mouse',
    }
]


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


@app.route('/shop/api/v1.0/items', methods=['GET'])
def get_items():
    return jsonify({'items': items})


@app.route('/shop/api/v1.0/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    item = list(filter(lambda t: t['id'] == item_id, items))
    if len(item) == 0:
        abort(404)
    return jsonify({'item': item[0]})


@app.route('/shop/api/v1.0/items', methods=['POST'])
def create_item():
    if not request.json or not 'name' in request.json:
        abort(400)
    item = {
        'id': items[-1]['id'] + 1,
        'name': request.json['name'],
        'description': request.json.get('description', ""),
    }
    items.append(item)
    return jsonify({'item': item}), 201


@app.route('/shop/api/v1.0/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    item = list(filter(lambda t: t['id'] == item_id, items))
    if len(item) == 0:
        abort(404)
    items.remove(item[0])
    return jsonify({'result': True})


@app.route('/shop/api/v1.0/items/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    item = list(filter(lambda t: t['id'] == item_id, items))
    if len(item) == 0:
        abort(404)
    if not request.json:
        abort(400)
    item[0]['name'] = request.json.get('name', item[0]['name'])
    item[0]['description'] = request.json.get('description', item[0]['description'])
    return jsonify({'item': item[0]})


if __name__ == '__main__':
    app.run(debug=True)
