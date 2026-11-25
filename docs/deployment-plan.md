# Deployment plan (Track C: Serverless)

Semua langkah dilakukan di AWS Learner Lab, region us-east-1.

1. **DynamoDB**: buat tabel `Cameras` (partition key `cameraId`, mode on-demand) lewat `scripts/create_table.sh` atau konsol.
2. **Lambda**: buat function `digicam-crud` (Python 3.12), upload `lambda/app.py`, set handler `app.lambda_handler`, set environment variable `TABLE_NAME=Cameras`.
3. **IAM**: pada Execution role pilih existing role `LabRole` (Learner Lab tidak mengizinkan membuat role baru).
4. **API Gateway**: buat REST API `digicam-api` dengan resource `/cameras` (POST) dan `/cameras/{id}` (GET, PUT, DELETE). Semua method memakai Lambda proxy integration ke `digicam-crud`. Deploy ke stage `dev`.
5. **Uji**: test event Lambda (`events/*.json`) lalu uji URL API Gateway dengan curl/Postman. Simpan screenshot sebagai bukti.

## Rencana minggu berikutnya
- Validasi input lebih ketat, endpoint `GET /cameras` untuk list.
- Frontend sederhana untuk daftar dan peminjaman kamera.
