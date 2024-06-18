# Jellyfin Exporter

A(nother) Prometheus exporter for Jellyfin.

## Prometheus Metrics

The `jellyfin_exporter` program emits a variety of Prometheus metrics to monitor the state and performance of a Jellyfin server. Below is a detailed description of each metric that the program generates.

### Session Metrics

| Metric | Description | Labels |
| ------ | ----------- | ------ |
| **jellyfin_sessions** | Number of active Jellyfin sessions. | `instance` |
| **jellyfin_session_info** | Information about current Jellyfin sessions. | `instance`, `session_id`, `user`, `client`, `device` |
| **jellyfin_session_transcode_info** | Info about transcoding in the Jellyfin session. | `instance`, `session_id`, `user`, `audio_codec`, `video_codec`, `container`, `is_video_direct`, `is_audio_direct`, `width`, `height`, `audio_channels` |
| **jellyfin_session_transcode_bitrate** | The transcoding bitrate of the Jellyfin session. | `instance`, `session_id`, `user` |
| **jellyfin_session_transcode_completion** | The transcoding completion percentage of the Jellyfin session. | `instance`, `session_id`, `user` |
| **jellyfin_session_bitrate** | The bitrate of the Jellyfin session. | `instance`, `session_id`, `user` |
| **jellyfin_session_now_playing_info** | Information about the item currently playing on the Jellyfin session. | `instance`, `session_id`, `user`, `item_id`, `name`, `type`, `media_type`, `rating` |
| **jellyfin_session_now_playing_run_time** | Run time of the item currently playing on the Jellyfin session. | `instance`, `session_id`, `user`, `item_id` |
| **jellyfin_session_play_state_info** | Information about the play state of the Jellyfin session. | `instance`, `session_id`, `user`, `paused`, `muted`, `play_method` |
| **jellyfin_session_play_state_position** | Position in the currently playing item on the Jellyfin session. | `instance`, `session_id`, `user` |

### User Metrics

| Metric | Description | Labels |
| ------ | ----------- | ------ |
| **jellyfin_users** | Number of Jellyfin users. | `instance` |
| **jellyfin_user_info** | Info about Jellyfin users. | `instance`, `user_id`, `user`, `administrator`, `hidden`, `disabled`, `subtitle_language_preference`, `subtitle_mode` |
| **jellyfin_user_invalid_login_attempts** | Number of invalid login attempts for a Jellyfin user. | `instance`, `user_id`, `user` |
| **jellyfin_user_lockout_login_attempts** | Number of login attempts before a Jellyfin user is locked out. | `instance`, `user_id`, `user` |
| **jellyfin_user_bitrate_limit** | The maximum bitrate sessions from a Jellyfin user are limited to. | `instance`, `user_id`, `user` |
| **jellyfin_user_last_login** | Last login timestamp of Jellyfin users. | `instance`, `user_id`, `user` |

### Item Metrics

| Metric | Description | Labels |
| ------ | ----------- | ------ |
| **jellyfin_items** | Number of Jellyfin items. | `instance`, `type` |


## Configuration

| Environment Variable | Description | Default | Required |
|-|-|-|:-:|
| JELLYFIN_EXPORTER_API_KEY | The API key to Jellyfin | | ✅ |
| JELLYFIN_EXPORTER_PORT | The port jellyfin-exporter will listen on | 8080 | ❌ |
| JELLYFIN_EXPORTER_URL | The full URL to Jellyfin | localhost:9090 | ❌ |
| JELLYFIN_EXPORTER_INSTANCE_NAME | A unique name for your jellyfin instance | jellyfin | ❌ |
