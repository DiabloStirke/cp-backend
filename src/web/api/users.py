from flask import jsonify
from web.auth import AuthBlueprint
from web.models.user import User

users_api = AuthBlueprint('users_api', __name__,
                          response_type='json', url_prefix='/api/users')


@users_api.auth_route('/me', methods=['GET'], require_auth=True)
def me(user: User):
    # Now I'm not sure, but I think user, passed to the view function, will never be None
    if not user:
        return jsonify({'error': 'User not found'}), 404

    user_info = {
        'username': user.username,
        'avatar_url': user.avatar_url,
    }
    return jsonify(user_info), 200
