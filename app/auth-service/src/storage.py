import uuid
import datetime
from authlib.jose import jwt


def setup_storage(app, private_key):
    app.storage = Storage(private_key)


class Storage:

    def __init__(self, private_key):
        self.private_key = private_key
        self.states = dict()
        self.sessions = dict()

    def create_state(self, req_url):
        key = str(uuid.uuid4())
        self.states[key] = {'req_url': req_url}
        return key

    def pop_state(self, key):
        if key not in self.states:
            return

        return self.states.pop(key)

    def create_session(self, *, username):
        key = str(uuid.uuid4())
        groups = ['users']
        scope = 'user'

        if username == 'admin':
            scope = 'admin'
            groups.append('admin')

        jwt_header = {
            'alg': 'RS256',
            'kid': self.private_key.thumbprint()
        }
        jwt_data = {
            "groups": groups,
            "username": username,
            "iss": "http://auth-service",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=365),
            "sub": key,
            "scope": scope  # Ambassador умеет работать со стандартными полями токена
        }
        jwt_header = jwt.encode(jwt_header, jwt_data, self.private_key).decode('utf-8')

        self.sessions[key] = {
            'x-username': username,
            'x-auth-token': jwt_header
        }

        return key

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
