from web.api.silksong import silksong_api
from web.api.auth import auth_api
from web.api.users import users_api


blueprints = [silksong_api, auth_api, users_api]
