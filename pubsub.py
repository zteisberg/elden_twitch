from twitchAPI import UserAuthenticator
from twitchAPI.pubsub import PubSub
from twitchAPI.twitch import Twitch
from twitchAPI.types import AuthScope

import callbacks
from settings import Settings as settings

import tracemalloc
tracemalloc.start()


def start_sub():
    twitch = Twitch(settings.APP_ID, settings.APP_SECRET)
    twitch.authenticate_app([])
    target_scope = [
        AuthScope.BITS_READ,
        AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
        AuthScope.CHANNEL_READ_REDEMPTIONS,
        AuthScope.USER_READ_BROADCAST,
        AuthScope.CHAT_READ,
        AuthScope.CHANNEL_SUBSCRIPTIONS,
        AuthScope.USER_READ_SUBSCRIPTIONS,
        AuthScope.USER_READ_FOLLOWS
    ]
    auth = UserAuthenticator(twitch, target_scope, force_verify=False)
    token, refresh_token = auth.authenticate()
    twitch.set_user_authentication(token, target_scope, refresh_token)
    user = twitch.get_users(logins=[settings.CHANNEL_NAME])
    user_id = user['data'][0]['id']

    uuids = []
    pubsub = PubSub(twitch)
    pubsub.start()
    uuids.append(pubsub.listen_channel_points(user_id, callbacks.callback_channel_points))
    uuids.append(pubsub.listen_bits(user_id, callbacks.callback_bits))
    uuids.append(pubsub.listen_channel_subscriptions(user_id, callbacks.callback_subs))
    input('press ENTER to close...')
    print()
    for uuid in uuids:
        pubsub.unlisten(uuid)
    pubsub.stop()
