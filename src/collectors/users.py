import traceback
from prometheus_client.core import GaugeMetricFamily
from datetime import datetime


class JellyfinUsers(object):
    def __init__(self, request_api, critical_logger):
        self.request_api = request_api
        self.critical_logger = critical_logger

    def collect(self):
        endpoint = "/users"
        try:
            data = self.request_api(endpoint)
            yield self.count(data)
            yield self.info(data)
            yield self.invalid_login_attempts(data)
            yield self.lockout_login_attempts(data)
            yield self.bitrate_limit(data)
            yield self.last_login(data)
        except Exception as ex:
            self.critical_logger(f"Error collecting {endpoint}: %s", ex)
            self.critical_logger("Traceback: %s", traceback.format_exc())

    def count(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_users",
            "Number of jellyfin users",
            labels=[],
        )
        gauge.add_metric([], len(data))
        return gauge

    def info(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_info",
            "Info about jellyfin users.",
            labels=[
                "user_id",
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
                    user["Id"],
                    user["Name"],
                    str(user["Policy"].get("IsAdministrator", "Unknown")),
                    str(user["Policy"].get("IsHidden", "Unknown")),
                    str(user["Policy"].get("IsDisabled", "Unknown")),
                    user["Configuration"].get("SubtitleLanguagePreference", "Unknown"),
                    user["Configuration"].get("SubtitleMode", "Unknown"),
                ],
                1,
            )
        return gauge

    def invalid_login_attempts(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_invalid_login_attempts",
            "Number of invalid login attempts for a jellyfin user.",
            labels=[
                "user_id",
                "user",
            ],
        )
        for user in data:
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    user["Id"],
                    user["Name"],
                ],
                int(user["Policy"].get("InvalidLoginAttemptCount", 0)),
            )
        return gauge

    def lockout_login_attempts(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_lockout_login_attempts",
            "Number of logins attempts before a jellyfin user is locked out.",
            labels=[
                "user_id",
                "user",
            ],
        )
        for user in data:
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    user["Id"],
                    user["Name"],
                ],
                int(user["Policy"].get("LoginAttemptsBeforeLockout", 0)),
            )
        return gauge

    def bitrate_limit(self, data):
        gauge = GaugeMetricFamily(
            "jellyfin_user_bitrate_limit",
            "The maximum bitrate sessions from a jellyfin user are limited to.",
            labels=[
                "user_id",
                "user",
            ],
        )
        for user in data:
            if "Policy" not in user:
                continue
            gauge.add_metric(
                [
                    user["Id"],
                    user["Name"],
                ],
                int(user["Policy"].get("RemoteClientBitrateLimit", 0)),
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
                "user_id",
                "user",
            ],
        )
        for user in data:
            if "LastLoginDate" not in user:
                continue
            date = self._strip_microseconds(user["LastLoginDate"])
            gauge.add_metric(
                [
                    user["Id"],
                    user["Name"],
                ],
                int(datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").timestamp()),
            )
        return gauge
