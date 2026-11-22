
import requests

GPS_API = "https://gps.ballota.jp/api.php"
STELLARIUM_API = "http://localhost:8090/api"

TIMEOUT = 10


def get_gps_location(code):
    """GPS中継サーバーから測位データを取得"""

    response = requests.post(
        GPS_API,
        params={"action": "receive"},
        json={"code": code},
        timeout=TIMEOUT
    )

    if response.status_code == 404:
        raise ValueError("キーが存在しないか、有効期限切れです")

    if response.status_code == 429:
        raise ValueError("アクセス回数制限に達しました")

    response.raise_for_status()

    data = response.json()

    if data.get("status") != "ok":
        raise ValueError("GPSデータ取得失敗")

    lat = float(data["latitude"])
    lon = float(data["longitude"])

    alt = data.get("altitude")
    alt = round(float(alt)) if alt is not None else None

    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValueError("不正なGPS座標です")

    return lat, lon, alt


def set_stellarium_location(lat, lon, alt):
    """Stellariumの観測地点を変更"""

    # 接続確認
    response = requests.get(
        f"{STELLARIUM_API}/main/status",
        timeout=5
    )
    response.raise_for_status()

    # 観測地点設定
    params = {
        "latitude": lat,
        "longitude": lon,
        "name": "GPS Location",
        "planet": "Earth"
    }

    if alt is not None:
        params["altitude"] = alt

    response = requests.post(
        f"{STELLARIUM_API}/location/setlocationfields",
        data=params,
        timeout=5
    )

    response.raise_for_status()

    if response.text.strip().lower() != "ok":
        raise RuntimeError(
            f"Stellariumが変更を確認できません: {response.text}"
        )

    # 反映結果を確認
    response = requests.get(
        f"{STELLARIUM_API}/main/status",
        timeout=5
    )
    response.raise_for_status()

    location = response.json()["location"]

    if (abs(float(location["latitude"]) - lat) > 0.0001 or
            abs(float(location["longitude"]) - lon) > 0.0001):
        raise RuntimeError("Stellariumの座標が一致しません")

    return location


def main():
    print("=== Stellarium GPS Location ===")

    code = input("6桁キーを入力: ").strip()

    if len(code) != 6 or not code.isdigit():
        print("エラー: 6桁の数字を入力してください")
        return

    try:
        print("\nGPSデータ取得中...")
        lat, lon, alt = get_gps_location(code)

        print(f"緯度 : {lat:.6f}")
        print(f"経度 : {lon:.6f}")
        print(f"標高 : {alt if alt is not None else '不明'} m")

        print("\nStellariumへ転送中...")
        location = set_stellarium_location(lat, lon, alt)

        print("\nStellarium観測地点変更完了！")
        print(f"地点名 : {location['name']}")
        print(f"緯度   : {location['latitude']}")
        print(f"経度   : {location['longitude']}")
        print(f"標高   : {location['altitude']} m")

    except requests.exceptions.ConnectionError:
        print("通信エラー: GPSサーバーまたはStellariumに接続できません")
    except requests.exceptions.Timeout:
        print("通信タイムアウト")
    except (ValueError, RuntimeError) as e:
        print(f"エラー: {e}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTPエラー: {e}")


if __name__ == "__main__":
    main()
