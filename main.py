import json
from flask import Flask, jsonify, request
from typing import List, Dict, Any

app = Flask(__name__)

# Load data from JSON file
with open('asset-management-products-json.json', 'r') as file:
    data = json.load(file)

def investment_product_api(request):
    """Responds to any HTTP request."""
    if request.method != 'GET':
        return jsonify({"error": "Only GET requests are supported"}), 405
    print(request)
    path = request.path
    if path == '/products':
        return get_products(request)
    elif path.startswith('/products/'):
        product_name = path.split('/')[-1].replace('%20', ' ')
        return get_product(product_name)
    elif path == '/performance':
        return get_performance(request)
    elif path == '/fees':
        return get_fees(request)
    elif path == '/risks':
        return get_risks(request)
    elif path == '/liquidity':
        return get_liquidity(request)
    else:
        return jsonify({"error": "Not found"}), 404

def get_products(request):
    asset_class = request.args.get('assetClass')
    min_return = request.args.get('minReturn')
    max_risk = request.args.get('maxRisk')

    filtered_products = data['products']

    if asset_class:
        filtered_products = [p for p in filtered_products if p['assetClass'].lower() == asset_class.lower()]
    
    if min_return:
        min_return = float(min_return)
        filtered_products = [p for p in filtered_products if p['returns']['oneYear'] >= min_return]

    if max_risk:
        risk_levels = {"Low": 1, "Low to Moderate": 2, "Moderate": 3, "Moderate to High": 4, "High": 5, "Very High": 6}
        max_risk_level = risk_levels.get(max_risk.capitalize(), 6)
        filtered_products = [p for p in filtered_products if risk_levels.get(p['risk']['riskLevel'], 6) <= max_risk_level]

    return jsonify(filtered_products)

def get_product(product_name):
    product = next((p for p in data['products'] if p['name'] == product_name), None)
    if product:
        return jsonify(product)
    return jsonify({"error": "Product not found"}), 404

def get_performance(request):
    product_name = request.args.get('productName')
    timeframe = request.args.get('timeframe')

    if product_name:
        product = next((p for p in data['products'] if p['name'] == product_name), None)
        if not product:
            return jsonify({"error": "Product not found"}), 404
        
        if timeframe:
            if timeframe in ['oneYear', 'threeYear', 'fiveYear']:
                return jsonify({timeframe: product['returns'][timeframe]})
            else:
                return jsonify({"error": "Invalid timeframe"}), 400
        else:
            return jsonify(product['returns'])
    else:
        return jsonify([{
            'name': p['name'],
            'returns': p['returns']
        } for p in data['products']])

def get_fees(request):
    product_name = request.args.get('productName')

    if product_name:
        product = next((p for p in data['products'] if p['name'] == product_name), None)
        if product:
            return jsonify(product['feeStructure'])
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify([{
        'name': p['name'],
        'feeStructure': p['feeStructure']
    } for p in data['products']])

def get_risks(request):
    product_name = request.args.get('productName')

    if product_name:
        product = next((p for p in data['products'] if p['name'] == product_name), None)
        if product:
            return jsonify(product['risk'])
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify([{
        'name': p['name'],
        'risk': p['risk']
    } for p in data['products']])

def get_liquidity(request):
    product_name = request.args.get('productName')

    if product_name:
        product = next((p for p in data['products'] if p['name'] == product_name), None)
        if product:
            return jsonify(product['liquidity'])
        return jsonify({"error": "Product not found"}), 404
    
    return jsonify([{
        'name': p['name'],
        'liquidity': p['liquidity']
    } for p in data['products']])

