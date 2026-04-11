import requests
import json
import re
from datetime import datetime
import pytz

STREAM_URL = "https://netx.streamstar18.workers.dev/soni"
JSON_FILE = "stream.json"
M3U_FILE = "stream.m3u"
CREDIT = "Sayan10"

def fetch_and_save():
    try:
        response = requests.get(STREAM_URL)
        response.raise_for_status()
        lines = response.text.split("\n")

        result = {}
        current_tvg_id = None
        current_group = None
        current_logo = None
        current_channel = None
        current_extinf = None
        skip_first = True

        for line in lines:
            trimmed = line.strip()

            if trimmed.startswith("#EXTINF:"):
                tvg_id_match = re.search(r'tvg-id="([^"]+)"', trimmed)
                group_match = re.search(r'group-title="([^"]+)"', trimmed)
                logo_match = re.search(r'tvg-logo="([^"]+)"', trimmed)
                channel_match = re.search(r',(.*)$', trimmed)

                current_tvg_id = tvg_id_match.group(1) if tvg_id_match else None
                current_group = group_match.group(1) if group_match else None
                current_logo = logo_match.group(1) if logo_match else None
                current_channel = channel_match.group(1) if channel_match else None
                current_extinf = trimmed

            elif trimmed.startswith("http") and current_tvg_id:

                if skip_first and current_tvg_id == "sf-top":
                    skip_first = False
                    current_tvg_id = current_group = current_logo = current_channel = current_extinf = None
                    continue

                result[current_tvg_id] = {
                    "url": trimmed,
                    "group_title": current_group,
                    "tvg_logo": current_logo,
                    "channel_name": current_channel,
                    "extinf": current_extinf
                }

                current_tvg_id = current_group = current_logo = current_channel = current_extinf = None

        total = len(result)

        # IST timestamp
        ist = pytz.timezone("Asia/Kolkata")
        now_ist = datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S IST")

        # ── Save JSON ──────────────────────────────────────────────
        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"✅ {JSON_FILE} saved ({total} channels).")

        # ── Save M3U ───────────────────────────────────────────────
        with open(M3U_FILE, "w", encoding="utf-8") as f:
            f.write("#EXTM3U\n")
            f.write(f"#CREDIT: {CREDIT}\n")
            f.write(f"#LAST UPDATED: {now_ist}\n")
            f.write(f"#TOTAL CHANNELS: {total}\n\n")
            for entry in result.values():
                f.write(f"{entry['extinf']}\n{entry['url']}\n")
        print(f"✅ {M3U_FILE} saved ({total} channels).")

    except requests.RequestException as e:
        print(f"❌ Failed to fetch M3U: {e}")
        raise SystemExit(1)

if __name__ == "__main__":
    fetch_and_save()