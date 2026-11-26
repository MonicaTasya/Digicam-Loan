"""Lambda handler untuk API peminjaman digicam (CRUD ke S3).

Setiap kamera disimpan sebagai satu file JSON: cameras/<cameraId>.json
Dipanggil oleh API Gateway (REST API, Lambda proxy integration).
"""
import json
import os
import re
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

BUCKET = os.environ.get("BUCKET_NAME")
print("DEBUG BUCKET:", BUCKET)
if not BUCKET:
    raise RuntimeError("BUCKET_NAME tidak terbaca. Env keys: " + ", ".join(os.environ.keys()))
s3 = boto3.client("s3")

VALID_STATUS = {"available", "borrowed"}
ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def object_key(camera_id):
    return f"cameras/{camera_id}.json"


def read_camera(camera_id):
    """Ambil data kamera dari S3. Return None kalau tidak ada."""
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=object_key(camera_id))
        return json.loads(obj["Body"].read())
    except ClientError as e:
        if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
            return None
        raise


def write_camera(item):
    s3.put_object(
        Bucket=BUCKET,
        Key=object_key(item["cameraId"]),
        Body=json.dumps(item).encode("utf-8"),
        ContentType="application/json",
    )


def create_camera(data):
    if not data.get("name"):
        return response(400, {"error": "field 'name' wajib diisi"})
    camera_id = data.get("cameraId") or f"cam-{uuid.uuid4().hex[:8]}"
    if not ID_PATTERN.match(camera_id):
        return response(400, {"error": "cameraId hanya boleh huruf, angka, - dan _"})
    if read_camera(camera_id):
        return response(409, {"error": "cameraId sudah ada"})
    item = {
        "cameraId": camera_id,
        "name": data["name"],
        "category": data.get("category", "pocket"),
        "status": "available",
        "borrower": "",
        "borrowedAt": "",
    }
    write_camera(item)
    return response(201, item)


def get_camera(camera_id):
    item = read_camera(camera_id)
    if not item:
        return response(404, {"error": "kamera tidak ditemukan"})
    return response(200, item)


def update_camera(camera_id, data):
    item = read_camera(camera_id)
    if not item:
        return response(404, {"error": "kamera tidak ditemukan"})

    status = data.get("status")
    if status and status not in VALID_STATUS:
        return response(400, {"error": "status harus 'available' atau 'borrowed'"})

    changes = {k: data[k] for k in ("name", "category", "status", "borrower") if k in data}
    if not changes:
        return response(400, {"error": "tidak ada field yang diubah"})
    item.update(changes)
    if status == "borrowed":
        item["borrowedAt"] = datetime.now(timezone.utc).isoformat()
    if status == "available":
        item["borrower"] = ""
        item["borrowedAt"] = ""
    write_camera(item)
    return response(200, item)


def delete_camera(camera_id):
    if not read_camera(camera_id):
        return response(404, {"error": "kamera tidak ditemukan"})
    s3.delete_object(Bucket=BUCKET, Key=object_key(camera_id))
    return response(200, {"message": f"{camera_id} dihapus"})


def lambda_handler(event, context):
    # Dukung format API Gateway (httpMethod) dan Function URL (requestContext.http)
    method = event.get("httpMethod") or (
        event.get("requestContext", {}).get("http", {}).get("method")
    )
    camera_id = (event.get("pathParameters") or {}).get("id")
    raw_path = event.get("rawPath")
    if not camera_id and raw_path is not None:
        parts = raw_path.strip("/").split("/")
        if len(parts) == 2 and parts[0] == "cameras":
            camera_id = parts[1]
        elif parts != ["cameras"]:
            return response(404, {"error": "path tidak ditemukan"})

    raw_body = event.get("body") or "{}"
    if event.get("isBase64Encoded"):
        import base64
        raw_body = base64.b64decode(raw_body).decode("utf-8")
    try:
        data = json.loads(raw_body)
    except json.JSONDecodeError:
        return response(400, {"error": "body bukan JSON yang valid"})

    if camera_id and not ID_PATTERN.match(camera_id):
        return response(400, {"error": "format id tidak valid"})

    try:
        if method == "POST" and not camera_id:
            return create_camera(data)
        if method == "GET" and camera_id:
            return get_camera(camera_id)
        if method == "PUT" and camera_id:
            return update_camera(camera_id, data)
        if method == "DELETE" and camera_id:
            return delete_camera(camera_id)
        return response(405, {"error": "route tidak didukung"})
    except ClientError as e:
        return response(500, {"error": "kesalahan server", "detail": str(e)})