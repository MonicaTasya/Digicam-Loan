# Digicam Loan API

API peminjaman digicam dengan arsitektur serverless (Track C).

## Use case

Mengelola peminjaman kamera digital: tambah kamera, lihat detail, ubah status (tersedia/dipinjam), dan hapus.

## Arsitektur

Client -> API Gateway -> Lambda (Python) -> DynamoDB. Lambda memakai IAM `LabRole` untuk akses tabel.
Diagram: `docs/architecture.png` (tambahkan setelah dibuat di draw.io).

## Entitas `Cameras`

| Atribut    | Tipe        | Keterangan                  |
| ---------- | ----------- | --------------------------- |
| cameraId   | String (PK) | ID unik, contoh `cam-001`   |
| name       | String      | Nama kamera                 |
| category   | String      | pocket / mirrorless / DSLR  |
| status     | String      | `available` atau `borrowed` |
| borrower   | String      | Nama peminjam               |
| borrowedAt | String      | Waktu pinjam (ISO 8601)     |

## Endpoint

| Method | Route         | Fungsi                    |
| ------ | ------------- | ------------------------- |
| POST   | /cameras      | Tambah kamera             |
| GET    | /cameras/{id} | Detail kamera             |
| PUT    | /cameras/{id} | Ubah data / status pinjam |
| DELETE | /cameras/{id} | Hapus kamera              |

## Struktur repo

```
lambda/app.py             kode handler CRUD
events/*.json             contoh event untuk test Lambda
scripts/create_table.sh   membuat tabel DynamoDB
docs/deployment-plan.md   langkah deploy ke AWS
```

## Deploy

Lihat `docs/deployment-plan.md`.

## Contoh pemakaian

```bash
curl -X POST $API_URL/cameras -d '{"name":"Canon IXUS 185"}'
curl $API_URL/cameras/cam-001
curl -X PUT $API_URL/cameras/cam-001 -d '{"status":"borrowed","borrower":"Nama"}'
curl -X DELETE $API_URL/cameras/cam-001
```
