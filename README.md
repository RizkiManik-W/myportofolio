# Portfolio Project

Nama : PUTU RIZKI MANIK WIDIADNYANA

NPM : 2506621900

Kelas : B

## About
Proyek ini adalah sebuah personal proyek yang simple yang dibuat dengan Django. Ini saya buat bertujuan untuk belajar web development, Git, dan cara melakukan deployment. Selain itu juga, kedepannya repositori ini akan menjadi portofolio utama saya. 

## Tech Stack
- Python
- Django
- HTML
- CSS
- SQLite (default dev database)

## Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/RizkiManik-W/myportofolio.git
cd myportofolio
```

### 2. Create a virtual environment
```bash
python -m venv env
```

On Windows:
```bash
env\Scripts\activate
```

On macOS/Linux:
```bash
source env/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Run the development server
```bash
python manage.py runserver
```

Then open:
```bash
http://127.0.0.1:8000/
```

## Project Structure
```bash
myportofolio/
├── manage.py
├── requirements.txt
├── portofolio/
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   └── wsgi.py
├── templates/
├── static/
└── db.sqlite3
```

## Individual Assignment 4: Authentication and Authorization

Portfolio pages remain readable without login. Signed-in users can star skills. Users in the `Editor` group can edit skills and experiences, while only superusers can add or delete them.

To enable the editor role, sign in to `/admin`, create a group named `Editor`, and add the intended user to that group. The skills JSON endpoint is available at `/api/skills/` and does not return passwords or other account credentials.

Superusers can review the 100 most recent Skill and Experience changes at `/activity/`. Each entry records the actor, action, item title, and timestamp; the activity record is written in the same transaction as the portfolio change.

The `Skill.starred_by` relationship is included in the project migrations. Apply pending migrations before running the app:

```bash
python manage.py migrate
```

## Notes
This is a learning project, so feel free to explore, modify, and improve it, hehe~. 

## AI Disclosure
Saya menggunakan ChatGPT (OpenAI) untuk memahami instruksi tugas, membandingkannya dengan kode proyek, dan merencanakan implementasi secara bertahap. Untuk tugas ini, bantuan AI digunakan untuk menulis dan meninjau perubahan pada view, template, dan dokumentasi. Saya meninjau perubahan kode sebelum menggunakannya. Bantuan AI sebelumnya juga digunakan untuk memahami refactoring CSS dan menyusun tes pada aplikasi.

AI assistance reference: https://chatgpt.com/share/6a9ec111-2468-83ec-855e-b0f64a787498

### AI Assistance Log: Individual Assignment 4

- Tool: ChatGPT (OpenAI).
- Prompting approach: compare the assignment checklist with the existing Django project, then implement related gaps in small, reviewable batches.
- AI-assisted changes: Editor group authorization, the activity log model and view, role-specific action controls in templates, and this assignment's README notes.
- Review: changes were checked with `git diff --check` and a manual diff review; application tests were not run in this session.

### Tugas 1
1. Ya, saya menggunakan semantik elemenet HTML5 seperti `section`, `article`, dan `aside`, ini saya gunakan untuk mengorganisir struktur portofolio saya supaya lebih bersih dan nyaman dilihat. Elemen-elemen ini membantu saya membuat website statik karena setiap bagian memiliki tujuannya masing-masing, seperti contoh section  hero untuk identitas saya, section skills and experience, dan aside untuk informasi tambahan yang saya ingin tunjukkan. Dengan struktur semantik, website yang saya buat terasa lebih terorganisir dan yang paling penting adalah kemudahan untuk menambahkan fitur ataupun konten baru yang ingin saya tambahkan kedepannya. 

2. Tantangan utama saya dalam membuat layout yang responsif adalah menyeimbangkan tempat kosong dan konten yang ingin saya tunjukkan ketika ukuran layar berubah-ubah. Di desktop saya dapat menempatkan elemen-elemen dengan ruang yang lebih luas, tetapi untuk mobile, karena ukuran layarnya yang kecil dan terasa hanya ada satu kolom, konten yang saya sajikan akan terasas 'sesak' karena kekurangan tempat. Untuk mengatasi ini saya mengevaluasi elemen mana yang paling penting dan yang harus diprioritaskan, seperti judul, bio, dan tombol-tombol, saya juga mengatur ukuran, 'spacing', dan urutan sehingga informasi yang paling penting dapat terlihat dengan mudah. Pendekatan yang saya gunakan deapat membuat website saya lebih mudah dibaca ketika berubah dari layar yang luas (deskstop) ke layar yang lebih kecil (mobile) yang membuat layout lebih sempit.

3. Keterbatasan utama yang saya hadapi ketika membuat statik website adalah kesulitan untuk meprepresentasikan konten dinamis lebih efisien, seperti memperbarui informasi portofolio secara manual di file HTML/CSS. Seiring informasi yang saya tunjukkan bertambah, mengelola konten akan terasa lebih sulit dan tidak efisien. Setelah saya melakukan research lebih dalam Fungsionalitas Dinamis yang inginkan pada proyek selanjutnya adalah sebuah CRUD (Create, Read, Update, Delete) sistem yang simple untuk mengelola proyek, pengalaman, dan skill dari panel admin, sehingga data portofolio dapat ditambahkan atau diperbarui tanpa melakukan perubahan pada file statik secara langsung.

### Tugas 2
1. Alur ketika user membuka halaman portofolio dimulai dari HTTP request yang dikirim oleh browser ke Django server. Request pertama akan masuk ke proyek URL configuration file [myportofolio/portofolio/urls.py](myportofolio/portofolio/urls.py), tepatnya `urls.py`. File ini yang bertanggung jawab untuk menghubungkan struktur URL utama proyek. Setelah itu, request akan diteruskan ke file konfigurasi aplikasi URL [myportofolio/main/urls.py](myportofolio/main/urls.py), yang cocok dengan rute spesifik ke fungsi `view` yang benar. fungsi `view` didefinisikan di [myportofolio/main/views.py](myportofolio/main/views.py). `view` kemudian menerima `request`, lalu mengakses data yang diperlukan dari model di [myportofolio/main/models.py](myportofolio/main/models.py). Model merepresentasikan struktur database yang memiliki field seperti `title`, `description`, `category`, dan `proficiency`. Setelah data yang di fetch dari model, view mengirimkan data resebut ke template HTML seperti [myportofolio/templates/index.html](myportofolio/templates/index.html) or [myportofolio/templates/skills.html](myportofolio/templates/skills.html). Jadi, alurnya adalah: browser → project urls.py → app urls.py → view → model → template → HTML response dikembalikan ke browser.

2. Portofolio data harusnya disimpan di model dibandingkan di tulis manual di template karena template seharusnya hanya bertangggung jawab untuk mendisplay data, tidak sebagai sumber data . Jika data di tulis secarat langsung di template, maka setiap perubahan pada data memerlukan perubahan pada file htl, membuat maintenance lebih sulit dan tidak konsisten. Dibandingkan jika menyimpannya di model, ini mengizinkan kita untuk menyimpannya di database dan dapat memanggilnya dengan cara yang dinamis melalui `view` dan Django ORM. Dengan model, data lebih mudah di untuk dikelola, selain itu menambahkan dan menghapus data menjadi jauh lebih mudah. Untuk kedepannya, dengan menggunakan model akan membuat proyek lebih 'clean' dan 'reuseable'. 

3. Django command `makemigrations` dan `migrate` mempunyai tugas berbeda. `makemigrations` membaca perubahan pada model dan membuat file migrasi yang mencatat perubahan pada struktur database. Sedangkan `migrate` menjalankan file migrasi yang membuat perubahan terjadi di databse. Sebuah contoh dari perubahan model yang memerlukan kedua command adalah menambahkan field baru seperti `proficiency` ke `Skill` model atau emmbuat model baru. Setelah mengubah model. kita harus melakukan run `python manage.py makemigrations` untuk mengenerate file migrasi lalu `python manage.py migrate` untuk melakukan perubahan pada database.

### Tugas 3
Di tugas ini, saya menambahkan fungsionalitas CRUD untuk data portofolio di Django, saya membuat model, form, view dan routing untuk skills dan experiences, lalu menghubungkannya ke tempplate sehinnga user dapat menambahkan, melihat, melakujan edit, dan mendelete daya dari aplikasi web. Saya juga mebambahkan fitur search. Saya juga melakukan refactoring.

1. Kita menambahkan `ModelForm` di Django karena dapat secara langsung menghubungkan ke model yang kita definisikan. Dengan `ModelForm`, input fields menghubungkan ke database, melakukan validasi, pemanggilan data, dan penyimpanan yang lebih cepat dan lebih aman. Dan juga, kita tidak perlu mengedit form HTML secara manual untuk setiap fields karena Djanog telah menyediakan form rendering. Kita diwajibkan menambahkan `{% csrf_token %}` karena Djanog menggunakan CSRF token untuk mencegah serangan cross-site request. Ini memastikan bahwa request datang dari aplikasi kita sendiri dan bukan merupakan situs third party yang mencoba memanipulasi data user. 

2. JSON lebih bagus daripada XML di modern web development karena lebih  jelas, lebih mudah dibaca dan lebih cepat untuk diproses. JSON juga memimiliki sturktur yang lebih simpel and lebih kompatibel dengan javaScripts, membuatnya lebih ideal untuk aplikasi web, API, dan komunikasi frontend-backend. XML lebih sulit dimengerti dan sulit untuk diproses, jadi JSON lebih efisien di aplikasi modern. 

3. Ketika view mengembalikan data portofolio dalam format JSON, requestnya pertama akan masuk ke URL yang sesuai dan diproses oleh view. View kemudian mengembalikan data dari model Django menggunakan ORM, dan melakukan serialisasi sehingga objek model dikonversi menjadi format JSON yang dapat dikirm ke client. Serialisasi pengin karena model objek Django merupakan objek python, bukan data biasa yang browsers atau aplikasi frontend biasa gunakan. Setelah serialisasi, respon kemudian di kirim menggunakan `HttpResponse` atau `JsonResponse`, sehingga client dapat menerima data yang konsisten.

### Task 4
Di tugas ini, saya melanjutkan fitur authentication dan authorization pada page skills dan experience. Page protofolio tetap mudah dibaca tanpa perlu login. User yang Singed-in dapat menambah atau menghapus stars pada skill. Saya menggunakan grup Django bernama `Editor` untuk mengijinkan editor untuk mengupdate data portofolio, hanya superuser yang dapat menambahkan atau menghapus.

For this assignment, I extended authentication and authorization to the Skills and Experience sections. Portfolio pages remain readable without logging in. Signed-in users can add or remove stars on skills. I used a Django group named `Editor` to allow editors to update portfolio data, while only superusers can add or delete it. Pemeriksaan akses diterapkan pada tampilan, dan beberapa tombol disembunyikan dari pengguna yang tidak diizinkan menggunakannya.

Saya juga menabhakn fitur tambahan yaitu riwayat aktifitas. Untuk setiap pembuatan, udpate, atau penghapusan skill ataupun experience akan merekam username, action, item tittle, dan timestamp. Riwayat akan disimpah di dalam tempat yang sama di perubahan portofolio dan hanya tersedia untuk superusers di `/activity`. 

/`api/skills/` JSON endpoint tetap tersedia untuk membaca skill data tanpa exposing password atau credentials akun. Untuk menambah role editor pada environment baru, buat grup `Editor` di Django admin dan tambahkan akun yang diinginkan ke grup tersebut.

### Tugas 5

Mengimplementasikan AJAX untuk experience dan skill

1. Debouncing mendelay search sampai user stop mengetik selama beberapa saat. Di projek ini, search menunggu selama 300ms sebelum melakukan request data yang telah difilter melalui endpoint JSON. Ini menhindari pengiriman request untuk setiap ketikan dan mengurangi kerja yang tidak begitu diperlukab untuk server dan browser. 

2. `fetch()` mengembalikan sebuah Promise karena request network selesai secara asinkronus. Menggunakan `await` melakukan pause untuk fungsi async saat ini sampai respon tersedia, jadi code dapat mengecek status dan membaca data JSON secara terurut. tanpa `await` atau `.then()`, code akan akan tetap lanjut dengan Promise dibandingkan respon yang respon yang telah selesai diproses. Hal ini dapat menyebabkan hasil yang salah atau race condition.

3. Cross-Site scripting (XSS) merupakan serangan dimana konten yang tidak dipercayai di interpretasikan sebagai executeable HTML atau JavaScript di user browser lain. Data yang diload AKAX tidak secara otomatis tidak aman, tapi JavaScript dapat membuat halaman rentan terhadap XSS jika memasukkan nilai yang tidak tepercaya menggunakan innerHTML. Template Django secara default melakukan escaping terhadap output variabel, sedangkan pada JavaScript sebaiknya digunakan API DOM yang aman seperti textContent atau melakukan escaping nilai secara eksplisit. Pada proyek ini, textContent digunakan untuk menampilkan teks, dan tag HTML pada judul serta deskripsi Skill dan Experience dihapus di sisi server.
