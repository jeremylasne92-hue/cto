from flask import Flask
from flask_cors import CORS
from backend.database.sqlite_manager import SQLiteManager
from backend.api.profile import profile_bp, init_profile_api


app = Flask(__name__)
CORS(app)

db_manager = SQLiteManager("app.db")

init_profile_api(db_manager)

app.register_blueprint(profile_bp)


@app.route('/health', methods=['GET'])
def health():
    return {'status': 'ok'}, 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
