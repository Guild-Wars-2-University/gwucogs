from __future__ import annotations

import datetime

import pytz

from .data import ZONE_KEYS


def gen_replacements() -> dict[str, str]:
    replacements: dict[str, str] = {}
    for key, zone in ZONE_KEYS.items():
        time = datetime.datetime.now(pytz.timezone(zone))
        foramtted_time = time.strftime("%I:%M%p").lstrip("0")
        replacements[key] = foramtted_time

        formatted_24h_time = time.strftime("%H:%M")
        replacements[f"{key}-24h"] = formatted_24h_time

        hour = int(time.strftime("%H"))
        minute = int(time.strftime("%M"))
        hour_offset = "!!!"
        if hour < 12 and hour != 0:
            hour_offset = f"+{hour}"
            if minute >= 30:
                hour_offset += ".5"
        else:
            if minute < 30:
                hour_offset = f"-{24-hour}"
            else:
                hour_offset = f"-{23-hour}.5"
        replacements[f"{key}-hr"] = hour_offset
    return replacements
