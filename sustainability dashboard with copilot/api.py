from flask import Blueprint, request, Response, stream_with_context, jsonify
from copilot.copilot import openai_call
from copilot.history import add_history, init_history
from utils.jwt_config import custom_jwt_required, user_id_in_token
from pdf_generator.pdf_generator import DATA_REQUEST, AGGREGATE_PDF, ENTITTY_PDF, FRAMEWORK_SFDR
from datatools.semantic_search import filtered_semMeta, semantic_metricMeta_ids
from datatools.analyser_classes import Exchange, Dashboard, Export
from datatools.google_cloud_storage import GoogleCloudStorage
import logging
from utils.limiter_config import limiter

bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

"""
1. Test
-------------------------------------------------------------------------------------------------------------------
"""

@bp.route('/hello')
@custom_jwt_required
def hello():
    return 'Hello, World!', 200

"""
1. Copilot
-------------------------------------------------------------------------------------------------------------------
"""
@bp.route('/chat_stream', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def chat_stream():    
    prompt = request.json.get('prompt')
    # page = request.json.get('page') # optional and unused atm
    user_id = user_id_in_token()
    message = {"role": "user", "content": prompt}
    add_history(user_id, message)
    
    @stream_with_context
    def generate(): 
        yield from openai_call(user_id, prompt)
    return Response(generate(), content_type="application/json", status=200)

@bp.route('/reinit_chat')
@limiter.limit("5 per minute")
@custom_jwt_required
def reinit_chat():
    user_id = user_id_in_token()  
    init_history(user_id)
    return jsonify('success!'), 200


"""
2. download pdf buttons
-------------------------------------------------------------------------------------------------------------------
"""
@bp.route('/entity_pdf', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def entity_pdf():
    logging.info('An entity_pdf came in')
    metricValue_id = request.json.get('metricValue_id')
    if metricValue_id is None:
        return jsonify({'error': 'Missing metricValue_id'}), 400
    AggregatePDF = ENTITTY_PDF(metricValue_id)
    buffer = AggregatePDF.entity_pdf()
    return Response(buffer, content_type='application/pdf', status=200)

@bp.route('/aggregate_pdf', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def aggregate_pdf():
    logging.info('An aggregate_pdf came in')
    metricMeta_id = request.json.get('metricMeta_id')
    if metricMeta_id is None:
        return jsonify({'error': 'Missing metricMeta_id'}), 400
    exchange_id = request.json.get('exchange_id')
    if exchange_id is None:
        return jsonify({'error': 'Missing exchange_id'}), 400
    AggregatePDF = AGGREGATE_PDF(metricMeta_id, exchange_id)
    buffer = AggregatePDF.aggregate()
    return Response(buffer, content_type='application/pdf', status=200)

@bp.route('/data_request_pdf', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def data_request_pdf():
    logging.info('A data_request_pdf came in')
    exchange_id = request.json.get('exchange_id')
    if exchange_id is None:
        return jsonify({'error': 'Missing exchange_id'}), 400
    DataRequest = DATA_REQUEST(exchange_id)
    buffer = DataRequest.data_request()
    return Response(buffer, content_type='application/pdf', status=200)

@bp.route('/Framework_SFDR', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def Framework_SFDR():
    logging.info('A Framework_SFDR came in')
    exchange_id = request.json.get('exchange_id')
    if exchange_id is None:
        return jsonify({'error': 'Missing exchange_id'}), 400
    FrameworkSFDR = FRAMEWORK_SFDR(exchange_id)
    buffer = FrameworkSFDR.framework_sfdr()
    return Response(buffer, content_type='application/pdf', status=200)

"""
3. semantic search
-------------------------------------------------------------------------------------------------------------------
"""

@bp.route('/semantic_search', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def semantic_search():
    logging.info('A semantic_search came in')
    query = request.json.get('query')
    if query is None:
        return jsonify({'error': 'Missing query'}), 400
    response = filtered_semMeta(query)
    return jsonify({'response': response}), 200

@bp.route('/semantic_search_id', methods=['POST'])
@limiter.limit("3 per minute")
@custom_jwt_required
def semantic_search_id():
    logging.info('A semantic_search_id came in')
    query = request.json.get('query')
    if query is None:
        return jsonify({'error': 'Missing query'}), 400
    response = semantic_metricMeta_ids(query)
    return jsonify({'response': response}), 200


"""
4. dashboard
-------------------------------------------------------------------------------------------------------------------
"""

@bp.route('/dashboard', methods=['POST'])
@limiter.limit("5 per minute")
@custom_jwt_required
def dashboard():
    portfolio_id = request.json.get('portfolio_id')
    if portfolio_id is None:
        return jsonify({'error': 'Missing portfolio_id'}), 400
    exchange = Exchange(portfolio_id)
    dashboard = Dashboard(exchange)
    export = Export(exchange, dashboard)
    return jsonify({'response': export.to_restructured_json()}), 200

"""
5. Visualiser
-------------------------------------------------------------------------------------------------------------------
"""
@bp.route('/add_url_to_overview', methods=['POST'])
@limiter.limit("5 per minute")
@custom_jwt_required
def add_url_to_overview():
    image_url = request.json.get('image_url')
    if image_url is None:
        return jsonify({'error': 'Missing image_url'}), 400
    storage = GoogleCloudStorage()
    storage.add_url_to_overview(image_url)
    return jsonify('success!'), 200

@bp.route('/get_image_urls', methods=['GET'])
@limiter.limit("3 per minute")
@custom_jwt_required
def get_image_urls():
    storage = GoogleCloudStorage()
    image_urls = storage.get_selected()
    return jsonify({'image_urls': image_urls}), 200

"""
5. Error-handler
-------------------------------------------------------------------------------------------------------------------
"""
@bp.errorhandler(404)
def not_found(error):
    custom_message = error.description if error.description else 'Resource not found'
    return jsonify({'error': custom_message}), 404

@bp.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad Request'}), 400

@bp.errorhandler(415)
def Unsupported_media_type(error):
    return jsonify({'error': 'Unsupported Media Type'}), 415