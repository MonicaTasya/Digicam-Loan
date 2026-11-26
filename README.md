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

## Contoh pemakaian (Postman)

| No  | Method | URL                              | Body           | Hasil yang diharapkan                        |
| --- | ------ | -------------------------------- | -------------- | -------------------------------------------- |
| 1   | POST   | `<FUNCTION_URL>/cameras`         | lihat di bawah | 201, kamera dibuat dengan status `available` |
| 2   | GET    | `<FUNCTION_URL>/cameras/cam-001` | tidak ada      | 200, detail kamera                           |
| 3   | PUT    | `<FUNCTION_URL>/cameras/cam-001` | lihat di bawah | 200, status menjadi `borrowed`               |
| 4   | GET    | `<FUNCTION_URL>/cameras/cam-001` | tidak ada      | 200, status masih `borrowed`                 |
| 5   | GET    | `<FUNCTION_URL>/cameras/cam-999` | tidak ada      | 404, "kamera tidak ditemukan"                |
| 6   | DELETE | `<FUNCTION_URL>/cameras/cam-001` | tidak ada      | 200, "cam-001 dihapus"                       |

Body untuk request 1 (POST):

```json
{ "cameraId": "cam-001", "name": "Canon IXUS 185", "category": "pocket" }
```

Body untuk request 3 (PUT):

```json
{ "status": "borrowed", "borrower": "Nama Peminjam" }
```

Screenshot hasil tiap request disimpan di `docs/evidence/`.
