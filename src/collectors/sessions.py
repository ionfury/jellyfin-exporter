from prometheus_client.core import GaugeMetricFamily
import traceback


class JellyfinSessions(object):
    def __init__(self, request_api, critical_logger):
        self.request_api = request_api
        self.critical_logger = critical_logger

    def collect(self):
        endpoint = "/sessions"
        try:
            data = self.request_api(endpoint)
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
            self.critical_logger(f"Error collecting {endpoint}: %s", ex)
            self.critical_logger("Traceback: %s", traceback.format_exc())

    def transcode_info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_transcode_info",
            "Info about transcoding in the jellyfin session.",
            labels=[
                "session_id",
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
                    session["Id"],
                    session["UserName"],
                    str(session["TranscodingInfo"].get("AudioCodec", "Unknown")),
                    str(session["TranscodingInfo"].get("VideoCodec", "Unknown")),
                    str(session["TranscodingInfo"].get("Container", "Unknown")),
                    str(session["TranscodingInfo"].get("IsVideoDirect", "Unknown")),
                    str(session["TranscodingInfo"].get("IsAudioDirect", "Unknown")),
                    str(session["TranscodingInfo"].get("Width", "Unknown")),
                    str(session["TranscodingInfo"].get("Height", "Unknown")),
                    str(session["TranscodingInfo"].get("AudioChannels", "Unknown")),
                ],
                1,
            )
        return gauge

    def transcode_bitrate(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_transcode_bitrate",
            "The transcoding bitrate of the jellyfin session.",
            labels=[
                "session_id",
                "user",
            ],
        )
        for session in data:
            if "TranscodingInfo" not in session:
                continue
            gauge.add_metric(
                [
                    session["Id"],
                    session["UserName"],
                ],
                int(session["TranscodingInfo"].get("Bitrate", 0)),
            )
        return gauge

    def transcode_completion(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_transcode_completion",
            "The transcoding completion percentage of the jellyfin session.",
            labels=[
                "session_id",
                "user",
            ],
        )
        for session in data:
            if "TranscodingInfo" not in session:
                continue
            gauge.add_metric(
                [
                    session["Id"],
                    session["UserName"],
                ],
                float(session["TranscodingInfo"].get("CompletionPercentage", 100)),
            )
        return gauge

    def bitrate(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_bitrate",
            "The bitrate of the jellyfin session.",
            labels=[
                "session_id",
                "user",
            ],
        )
        for session in data:
            if "NowPlayingItem" not in session:
                continue
            if "MediaStreams" not in session["NowPlayingItem"]:
                continue
            streams = session["NowPlayingItem"]["MediaStreams"]
            bitrate = sum(item.get("BitRate", 0) for item in streams if "BitRate" in item)
            gauge.add_metric(
                [
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
                "session_id",
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
                    session["Id"],
                    session["UserName"],
                    str(session["NowPlayingItem"].get("Id", "Unknown")),
                    str(session["NowPlayingItem"].get("Name", "Unknown")),
                    str(session["NowPlayingItem"].get("Type", "Unknown")),
                    str(session["NowPlayingItem"].get("MediaType", "Unknown")),
                    str(session["NowPlayingItem"].get("OfficialRating", "Unknown")),
                ],
                1,
            )
        return gauge

    def now_playing_run_time(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_now_playing_run_time",
            "Run time of the item currently playing on the jellyfin session.",
            labels=[
                "session_id",
                "user",
                "item_id",
            ],
        )
        for session in data:
            if "NowPlayingItem" not in session:
                continue
            gauge.add_metric(
                [
                    session["Id"],
                    session["UserName"],
                    str(session["NowPlayingItem"].get("Id", "Unknown")),
                ],
                int(session["NowPlayingItem"].get("RunTimeTicks", 0)),
            )
        return gauge

    def count(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_sessions",
            "Number of jellyfin sessions",
        )
        gauge.add_metric([], len(data))
        return gauge

    def info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_info",
            "Info about current jellyfin sessions.",
            labels=["session_id", "user", "client", "device"],
        )
        for session in data:
            gauge.add_metric(
                [
                    session["Id"],
                    session["UserName"],
                    session["Client"],
                    session["DeviceName"],
                ],
                1,
            )
        return gauge

    def play_state_info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_play_state_info",
            "Information about the play state of the jellyfin session.",
            labels=[
                "session_id",
                "user",
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
                    session["Id"],
                    session["UserName"],
                    str(session["PlayState"].get("IsPaused", "Unknown")),
                    str(session["PlayState"].get("IsMuted", "Unknown")),
                    str(session["PlayState"].get("PlayMethod", "Unknown")),
                ],
                1,
            )
        return gauge

    def play_state_position(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_session_play_state_position",
            "Information about the play state of the jellyfin session.",
            labels=[
                "session_id",
                "user",
            ],
        )
        for session in data:
            if "PlayState" not in session:
                continue
            gauge.add_metric(
                [
                    session["Id"],
                    session["UserName"],
                ],
                int(session["PlayState"].get("PositionTicks", 0)),
            )
        return gauge
