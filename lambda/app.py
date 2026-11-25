"""Lambda handler untuk API peminjaman digicam (CRUD ke DynamoDB).

Dipanggil oleh API Gateway (REST API, Lambda proxy integration).
Event berisi httpMethod, pathParameters, dan body.
"""
import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

TABLE_NAME = os.environ.get("TABLE_NAME", "Cameras")
table = boto3.resource("dynamodb").Table(TABLE_NAME)

VALID_STATUS = {"available", "borrowed"}


def response(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=str),
    }


def create_camera(data):
    if not data.get("name"):
        return response(400, {"error": "field 'name' wajib diisi"})
    item = {
        "cameraId": data.get("cameraId") or f"cam-{uuid.uuid4().hex[:8]}",
        "name": data["name"],
        "category": data.get("category", "pocket"),
        "status": "available",
        "borrower": "",
        "borrowedAt": "",
    }
    table.put_item(Item=item, ConditionExpression="attribute_not_exists(cameraId)")
    return response(201, item)


def get_camera(camera_id):
    item = table.get_item(Key={"cameraId": camera_id}).get("Item")
    if not item:
        return response(404, {"error": "kamera tidak ditemukan"})
    return response(200, item)


def update_camera(camera_id, data):
    status = data.get("status")
    if status and status not in VALID_STATUS:
        return response(400, {"error": "status harus 'available' atau 'borrowed'"})

    updates = {k: data[k] for k in ("name", "category", "status", "borrower") if k in data}
    if status == "borrowed":
        updates["borrowedAt"] = datetime.now(timezone.utc).isoformat()
    if status == "available":
        updates["borrower"] = ""
        updates["borrowedAt"] = ""
    if not updates:
        return response(400, {"error": "tidak ada field yang diubah"})

    names = {f"#{k}": k for k in updates}
    values = {f":{k}": v for k, v in updates.items()}
    expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
    try:
        result = table.update_item(
            Key={"cameraId": camera_id},
            UpdateExpression=expr,
            ExpressionAttributeNames=names,
            ExpressionAttributeValues=values,
            ConditionExpression="attribute_exists(cameraId)",
            ReturnValues="ALL_NEW",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return response(404, {"error": "kamera tidak ditemukan"})
        raise
    return response(200, result["Attributes"])


def delete_camera(camera_id):
    try:
        table.delete_item(
            Key={"cameraId": camera_id},
            ConditionExpression="attribute_exists(cameraId)",
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return response(404, {"error": "kamera tidak ditemukan"})
        raise
    return response(200, {"message": f"{camera_id} dihapus"})


def lambda_handler(event, context):
    method = event.get("httpMethod")
    camera_id = (event.get("pathParameters") or {}).get("id")
    try:
        data = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return response(400, {"error": "body bukan JSON yang valid"})

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
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return response(409, {"error": "cameraId sudah ada"})
        return response(500, {"error": "kesalahan server", "detail": str(e)})
