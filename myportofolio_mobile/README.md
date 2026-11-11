# MyPortfolio Mobile - Tutorial 08

Aplikasi Flutter untuk Tutorial 08: Basic Flutter, PBP Gasal 2026/2027.
Aplikasi Flutter berada di subfolder `myportofolio_mobile` dalam repositori Django `myportofolio`. Jalankan perintah Flutter dari subfolder ini.

## Menjalankan

```powershell
flutter pub get
flutter run -d chrome
```

Jika Flutter belum terbaca di terminal yang sudah dibuka, gunakan
`C:\tools\flutter\bin\flutter.bat` sebagai pengganti `flutter`.

## Implementasi

- `lib/main.dart`: bootstrap `MyApp`, tema Material 3 indigo dan amber,
  serta halaman awal `MyHomePage`.
- `lib/menu.dart`: halaman stateless, widget reusable `InfoCard` dan `ItemCard`,
  model `ItemHomepage`, dan grid tiga kolom.
- Identitas contoh tutorial: Burhan, NPM 2406000001, kelas PBP A.
- Tombol Lihat Proyek, Tambah Proyek, dan Logout menampilkan SnackBar
  `Kamu telah menekan tombol <nama tombol>!`.
- Konten dapat digulir pada layar pendek; kartu identitas menyesuaikan lebar
  tersedia agar tidak overflow pada ponsel.

Tutorial ini belum menghubungkan aplikasi ke REST API Django dan belum membuat
halaman proyek atau autentikasi. Tombol-tombol memberikan umpan balik SnackBar
sesuai lingkup Tutorial 08. Personalisasi identitas dan menu merupakan bagian
Individual Assignment 7.

## Verifikasi

```powershell
dart format --output=none --set-exit-if-changed lib test
flutter analyze
flutter test
flutter build web
```

Pengujian widget mencakup identitas pemilik, ketiga tombol dan pesannya,
serta layout layar kecil dalam orientasi portrait dan landscape.

## Pengumpulan

Sesuai permintaan pemilik, aplikasi ini sekarang mengikuti Git repositori
Django di folder induk. Dari root `myportofolio`, jalankan:

```powershell
git add myportofolio_mobile
git commit -m "Add Tutorial 08 Flutter mobile app"
git push
```

Panduan tutorial asli meminta repositori Flutter terpisah. Susunan folder
saat ini mengikuti permintaan pemilik untuk menggunakan repositori yang sama.
Riwayat Git mobile sebelumnya disimpan di folder saudara
`myportofolio_mobile.git-backup` di luar repositori Django.

Referensi: tutorial mata kuliah yang diberikan dan
[dokumentasi Flutter](https://docs.flutter.dev/).

## Hasil pemeriksaan lokal

Diverifikasi dengan Flutter 3.47.9 dan Dart 3.13.7:

- `flutter analyze`: No issues found.
- `flutter test`: 6 pengujian berhasil.
- `flutter build web`: berhasil.
- Chrome headless: halaman berhasil dirender tanpa JavaScript page error.
- `dart run tool/halo_burhan.dart`: menampilkan salam sesuai tutorial.

Tangkapan layar:

- [Tampilan ponsel](docs/tutorial08-mobile.png)
- [Tampilan desktop](docs/tutorial08-desktop.png)

Flutter SDK tersedia di `C:\tools\flutter` dan sudah ditambahkan ke User PATH.
Ekstensi resmi Flutter dan Dart untuk VS Code sudah terpasang.
Buka terminal baru agar perubahan PATH terbaca.

Target Chrome siap digunakan. Android SDK/Android Studio belum terpasang,
sehingga menjalankan emulator atau membangun APK memerlukan setup Android
terlebih dahulu. Toolchain desktop Windows juga belum lengkap; kedua hal
ini tidak menghalangi menjalankan dan membangun aplikasi web.
