# Digicam Loan API

API peminjaman digicam dengan arsitektur serverless (Track C).

## Use case

Mengelola peminjaman kamera digital: tambah kamera, lihat detail, ubah status (tersedia/dipinjam), dan hapus.

## Arsitektur

Client -> API Gateway -> Lambda (Python) -> S3. Lambda memakai IAM `LabRole` untuk akses bucket.
Diagram: `docs/architecture.png` (tambahkan setelah dibuat di draw.io).

Catatan: penyimpanan memakai S3 karena DynamoDB tidak diizinkan di Learner Lab ini.

## Entitas `Camera`

Disimpan sebagai satu objek JSON per kamera di S3 dengan key `cameras/<cameraId>.json`.

| Atribut    | Tipe   | Keterangan                  |
| ---------- | ------ | --------------------------- |
| cameraId   | String | ID unik, contoh `cam-001`   |
| name       | String | Nama kamera                 |
| category   | String | pocket / mirrorless / DSLR  |
| status     | String | `available` atau `borrowed` |
| borrower   | String | Nama peminjam               |
| borrowedAt | String | Waktu pinjam (ISO 8601)     |

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
scripts/create_bucket.sh  membuat bucket S3
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
