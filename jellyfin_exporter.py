import os
import logging
import requests
import threading
import time
from datetime import datetime

from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, REGISTRY

PORT = int(os.getenv("JELLYFIN_EXPORTER_PORT", 8080))
URL = os.getenv("JELLYFIN_EXPORTER_URL", "localhost:9090")
API_KEY = os.getenv("JELLYFIN_EXPORTER_API_KEY", "")
INSTANCE = os.getenv("JELLYFIN_EXPORTER_INSTANCE_NAME", "jellyfin")

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(message)s",
    level=logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)

logging.info("Starting jellyfin_exporter for '%s' on port: %d", str(URL), PORT)
logging.debug("Starting with api key '%s'", API_KEY)


def request_api(action):
    url = "{}{}?api_key={}".format(URL, action, API_KEY)
    start = time.time()
    data = requests.get(url).json()
    elapsed = time.time() - start
    logging.info("Request to %s returned in %s", url, elapsed)
    return data


class JellyfinSessions(object):
    def collect(self):
        try:
            data = request_api("/sessions")
            yield self.count(data)
            yield self.info(data)
            yield self.bitrate(data)
            yield self.play_state_info(data)
            yield self.play_state_position(data)
            yield self.now_playing_info(data)
            yield self.now_playing_run_time(data)
            yield self.transcode_info(data)
            yield self.transcode_bitrate(data)
            yield self.transcode_completion(data)
        except Exception as ex:
            logging.critical(ex)

    def transcode_info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_transcode_info",
            "Info about transcoding in the jellyfin session.",
            labels=[
                "id",
                "user",
                "audio_codec",
                "video_codec",
                "container",
                "is_video_direct",
                "is_audio_direct",
                "width",
                "height",
                "audio_channels",
            ],
        )
        for session in data:
            if "TranscodingInfo" not in session:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                    str(session["TranscodingInfo"]["AudioCodec"]),
                    str(session["TranscodingInfo"]["VideoCodec"]),
                    str(session["TranscodingInfo"]["Container"]),
                    str(session["TranscodingInfo"]["IsVideoDirect"]),
                    str(session["TranscodingInfo"]["IsAudioDirect"]),
                    str(session["TranscodingInfo"]["Width"]),
                    str(session["TranscodingInfo"]["Height"]),
                    str(session["TranscodingInfo"]["AudioChannels"]),
                ],
                1,
            )
        return gauge

    def transcode_bitrate(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_transcode_bitrate",
            "The transcoding bitrate of the jellyfin session.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for session in data:
            if "TranscodingInfo" not in session:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                ],
                int(session["TranscodingInfo"]["Bitrate"]),
            )
        return gauge

    def transcode_completion(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_transcode_completion",
            "The transcoding completion percentage of the jellyfin session.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for session in data:
            if "TranscodingInfo" not in session:
                continue
            completion = 100
            if "CompletionPercentage" in session["TranscodingInfo"]:
                completion = session["TranscodingInfo"]["CompletionPercentage"]
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                ],
                float(completion),
            )
        return gauge

    def bitrate(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_bitrate",
            "The bitrate of the jellyfin session.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for session in data:
            if "NowPlayingItem" not in session:
                continue
            if "MediaStreams" not in session["NowPlayingItem"]:
                continue
            streams = session["NowPlayingItem"]["MediaStreams"]
            bitrate = sum(
                item.get("BitRate", 0) for item in streams if "BitRate" in item
            )
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                ],
                bitrate,
            )
        return gauge

    def now_playing_info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_now_playing_info",
            "Information about the item currently playing on the jellyfin session.",
            labels=[
                "instance",
                "id",
                "user",
                "item_id",
                "name",
                "type",
                "media_type",
                "rating",
            ],
        )
        for session in data:
            if "NowPlayingItem" not in session:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                    str(session["NowPlayingItem"]["Id"]),
                    str(session["NowPlayingItem"]["Name"]),
                    str(session["NowPlayingItem"]["Type"]),
                    str(session["NowPlayingItem"]["MediaType"]),
                    str(session["NowPlayingItem"]["OfficialRating"]),
                ],
                1,
            )
        return gauge

    def now_playing_run_time(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_now_playing_run_time",
            "Run time of the item currently playing on the jellyfin session.",
            labels=[
                "instance",
                "id",
                "user",
                "item_id",
            ],
        )
        for session in data:
            if "NowPlayingItem" not in session:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                    str(session["NowPlayingItem"]["Id"]),
                ],
                int(session["NowPlayingItem"]["RunTimeTicks"]),
            )
        return gauge

    def count(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_sessions",
            "Number of jellyfin sessions",
            labels=["instance"],
        )
        gauge.add_metric([INSTANCE], len(data))
        return gauge

    def info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_info",
            "Info about current jellyfin sessions.",
            labels=["instance", "id", "user", "client", "device"],
        )
        for s in data:
            gauge.add_metric(
                [INSTANCE, s["Id"], s["UserName"], s["Client"], s["DeviceName"]], 1
            )
        return gauge

    def play_state_info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_play_state_info",
            "Information about the play state of the jellyfin session.",
            labels=[
                "instance",
                "id",
                "userId",
                "paused",
                "muted",
                "play_method",
            ],
        )
        for session in data:
            if "PlayState" not in session:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                    str(session["PlayState"]["IsPaused"]),
                    str(session["PlayState"]["IsMuted"]),
                    str(session.get("PlayState").get("PlayMethod", "Unknown")),
                ],
                1,
            )
        return gauge

    def play_state_position(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_play_state_info",
            "Information about the play state of the jellyfin session.",
            labels=[
                "instance",
                "id",
                "userId",
            ],
        )
        for session in data:
            if "PlayState" not in session:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    session["Id"],
                    session["UserName"],
                ],
                int(session.get("PlayState").get("PositionTicks", 0)),
            )
        return gauge


class JellyfinUsers(object):
    def collect(self):
        try:
            data = request_api("/users")
            yield self.count(data)
            yield self.info(data)
            yield self.invalid_login_attempts(data)
            yield self.lockout_login_attempts(data)
            yield self.bitrate_limit(data)
            yield self.last_login(data)
        except Exception as ex:
            logging.critical(ex)

    def count(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_users",
            "Number of jellyfin users",
            labels=["instance"],
        )
        gauge.add_metric([INSTANCE], len(data))
        return gauge

    def info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_info",
            "Info about jellyfin users.",
            labels=[
                "instance",
                "id",
                "user",
                "administrator",
                "hidden",
                "disabled",
                "subtitle_language_preference",
                "subtitle_mode",
            ],
        )
        for user in data:
            if "Configuration" not in user:
                continue
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    user["Id"],
                    user["Name"],
                    str(user["Policy"]["IsAdministrator"]),
                    str(user["Policy"]["IsHidden"]),
                    str(user["Policy"]["IsDisabled"]),
                    user["Configuration"]["SubtitleLanguagePreference"],
                    user["Configuration"]["SubtitleMode"],
                ],
                1,
            )
        return gauge

    def invalid_login_attempts(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_invalid_login_attempts",
            "Number of invalid login attempts for a jellyfin user.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for user in data:
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    user["Id"],
                    user["Name"],
                ],
                int(user["Policy"]["InvalidLoginAttemptCount"]),
            )
        return gauge

    def lockout_login_attempts(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_lockout_login_attempts",
            "Number of logins attempts before a jellyfin user is locked out.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for user in data:
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    user["Id"],
                    user["Name"],
                ],
                int(user["Policy"]["LoginAttemptsBeforeLockout"]),
            )
        return gauge

    def bitrate_limit(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_bitrate_limit",
            "The maximum bitrate sessions from a jellyfin user are limited to.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for user in data:
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    INSTANCE,
                    user["Id"],
                    user["Name"],
                ],
                int(user["Policy"]["RemoteClientBitrateLimit"]),
            )
        return gauge

    def _strip_microseconds(self, date_string):
        """Strip microseconds down to 6 digits if they are longer."""
        if "." in date_string and "Z" in date_string:
            before_microseconds, rest = date_string.split(".")
            microseconds = rest[:-1]  # Remove the 'Z'
            if len(microseconds) > 6:
                microseconds = microseconds[:6]
            return f"{before_microseconds}.{microseconds}Z"
        return date_string

    def last_login(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_last_login",
            "Last login timestamp of jellyfin users.",
            labels=[
                "instance",
                "id",
                "user",
            ],
        )
        for user in data:
            if "LastLoginDate" not in user:
                continue
            date = self._strip_microseconds(user["LastLoginDate"])
            gauge.add_metric(
                [
                    INSTANCE,
                    user["Id"],
                    user["Name"],
                ],
                int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()),
            )
        return gauge


class JellyfinItems(object):
    def collect(self):
        try:
            data = request_api("/Items/Counts")
            yield self.count(data)
        except Exception as ex:
            logging.critical(ex)

    def count(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_items",
            "Number of jellyfin items.",
            labels=["instance", "type"],
        )
        for item, value in data.items():
            gauge.add_metric([INSTANCE, item], int(value))

        return gauge


REGISTRY.register(JellyfinSessions())
REGISTRY.register(JellyfinUsers())
REGISTRY.register(JellyfinItems())
start_http_server(PORT)

e = threading.Event()
e.wait()
