import datetime

from flask import session, request, jsonify
from web.discord_client import DiscordClient, DiscordClientException
from web.auth import AuthBlueprint
from web.utils import tz_now
from web.models.user import User
import web.config as config

dc = DiscordClient(
    client_id=config.DISCORD_CLIENT_ID,
    client_secret=config.DISCORD_CLIENT_SECRET
)


auth_api = AuthBlueprint('auth_api', __name__,
                         response_type='json', url_prefix='/api/auth')


def set_session(auth_data):
    session['token'] = auth_data['access_token']
    session['expires'] = tz_now(
    ) + datetime.timedelta(seconds=auth_data['expires_in'])
    session['refresh'] = auth_data['refresh_token']

    user_info = dc.me(session['token'])
    user_info['avatar_url'] = dc.get_avatar_url(session['token'])
    session['user'] = user_info


def unset_session():
    session.pop('token', None)
    session.pop('expires', None)
    session.pop('refresh', None)
    session.pop('user', None)


@auth_api.route('/discord-auth-url', methods=['GET'])
def discord_auth_url():
    return jsonify({'test_error': 'test error'}), 400
    callback = request.args.get('callback', None)
    if not callback:
        return jsonify({'error': 'No callback provided'}), 400
    authorize_url = dc.get_authorization_url(callback)
    return jsonify({'url': authorize_url}), 200


@auth_api.route('/discord-authorized', methods=['GET'])
def discord_authorized():
    code = request.args.get('code', None)
    callback = request.args.get('callback', None)
    if not code:
        return jsonify({'error': 'No code provided'}), 400
    if not callback:
        return jsonify({'error': 'No callback provided'}), 400
    try:
        auth_data = dc.exchange_code(code, callback)
    except DiscordClientException as e:
        return jsonify({'errror': e.args[0]}), e.args[1]
    set_session(auth_data)
    user = User.get_by_id(session['user']['id'])
    if user:
        if user.use_discord_username and (
                user.username != session['user']['username'] or not user.username_matches_discord):
            user.update(
                username=session['user']['username'], username_matches_discord=True)
        if user.avatar_url != session['user']['avatar_url']:
            user.update(avatar_url=session['user']['avatar_url'])

    return jsonify({'message': 'success'}), 200
