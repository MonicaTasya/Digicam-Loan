# Deployment plan (Track C: Serverless)

Semua langkah dilakukan di AWS Learner Lab, region us-east-1.

Catatan desain: DynamoDB tidak diizinkan pada akun Learner Lab ini (aksi `dynamodb:CreateTable` ditolak), sehingga data disimpan sebagai objek JSON di S3.

1. **S3**: buat bucket privat `digicam-loan-<inisial-nim>` (Block all public access tetap aktif) lewat konsol atau `scripts/create_bucket.sh`.
2. **Lambda**: buat function `digicam-crud` (Python 3.12), tempel isi `lambda/app.py` ke `lambda_function.py`, handler `lambda_function.lambda_handler`, environment variable `BUCKET_NAME=<nama bucket>`.
3. **IAM**: pada Execution role pilih existing role `LabRole` (Learner Lab tidak mengizinkan membuat role baru).
4. **API Gateway**: buat REST API `digicam-api` dengan resource `/cameras` (POST) dan `/cameras/{id}` (GET, PUT, DELETE). Semua method memakai Lambda proxy integration ke `digicam-crud`. Deploy ke stage `dev`.
5. **Uji**: test event Lambda (`events/*.json`) lalu uji URL API Gateway dengan curl/Postman. Simpan screenshot sebagai bukti.

## Rencana lanjutan

- Endpoint `GET /cameras` untuk list (memakai `list_objects_v2`).
- Frontend sederhana untuk daftar dan peminjaman kamera.
- Jika akses DynamoDB tersedia, migrasi penyimpanan ke DynamoDB agar mendukung query dan update atomik.
