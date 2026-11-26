# Deployment plan (Track C: Serverless)

Semua langkah dilakukan di AWS Learner Lab, region us-east-1.

Catatan: DynamoDB dan API Gateway tidak diizinkan pada akun Learner Lab ini (aksi `dynamodb:CreateTable` dan `apigateway:POST` ditolak). Karena itu data disimpan sebagai objek JSON di S3 dan endpoint HTTP disediakan lewat Lambda Function URL.

1. **S3**: buat bucket privat `digicam-loan-544527` (Block all public access tetap aktif) lewat konsol atau `scripts/create_bucket.sh`.
2. **Lambda**: buat function `digicam-crud` (Python 3.12), tempel isi `lambda/app.py` ke `lambda_function.py`, handler `lambda_function.lambda_handler`, lalu tambahkan environment variable `BUCKET_NAME` dengan value `digicam-loan-544527`.
3. **IAM**: pada Execution role pilih existing role `LabRole` (Learner Lab tidak mengizinkan membuat role baru).
4. **Function URL**: pada function `digicam-crud`, buka Configuration, Function URL, lalu Create function URL dengan Auth type `NONE`. Salin URL-nya (`https://<id>.lambda-url.us-east-1.on.aws`). Routing (`POST /cameras`, `GET/PUT/DELETE /cameras/{id}`) ditangani oleh kode di `lambda_handler`.
5. **Uji**: jalankan test event Lambda (`events/*.json`), lalu uji Function URL dengan Postman atau curl. Simpan screenshot sebagai bukti.

## Rencana lanjutan

- Endpoint `GET /cameras` untuk list (memakai `list_objects_v2`).
- Frontend sederhana untuk daftar dan peminjaman kamera.
- Jika akses tersedia, migrasi ke DynamoDB dan API Gateway dengan autentikasi.
- Function URL dinonaktifkan setelah penilaian karena Auth type-nya `NONE`.
