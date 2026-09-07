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
git clone <repository-url>
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

## Notes
This is a learning project, so feel free to explore, modify, and improve it, hehe~. 

## AI Disclosure
Proyek ini menggunakan bantuan AI untuk membantu saya memahami apa yang harus saya lakukan ketika ingin mengubah sesuatu, mempratikkan bagaimana implementasi sebuah fitur harus dilakuakn, melakukan strukturisasi, yang dimana awalnya code CSS saya sangat berantakan. Selain itu saran juga merupakan hal yang saya dapat dari AI, seperti apa yang harusnya saya tunjukkan, dan bagaimana harus direpresentasikan. 

AI assistance reference: https://chatgpt.com/share/6a9ec111-2468-83ec-855e-b0f64a787498

### Tugas 1
1. Ya, saya menggunakan semantik elemenet HTML5 seperti `section`, `article`, dan `aside`, ini saya gunakan untuk mengorganisir struktur portofolio saya supaya lebih bersih dan nyaman dilihat. Elemen-elemen ini membantu saya membuat website statik karena setiap bagian memiliki tujuannya masing-masing, seperti contoh section  hero untuk identitas saya, section skills and experience, dan aside untuk informasi tambahan yang saya ingin tunjukkan. Dengan struktur semantik, website yang saya buat terasa lebih terorganisir dan yang paling penting adalah kemudahan untuk menambahkan fitur ataupun konten baru yang ingin saya tambahkan kedepannya. 

2. Tantangan utama saya dalam membuat layout yang responsif adalah menyeimbangkan tempat kosong dan konten yang ingin saya tunjukkan ketika ukuran layar berubah-ubah. Di desktop saya dapat menempatkan elemen-elemen dengan ruang yang lebih luas, tetapi untuk mobile, karena ukuran layarnya yang kecil dan terasa hanya ada satu kolom, konten yang saya sajikan akan terasas 'sesak' karena kekurangan tempat. Untuk mengatasi ini saya mengevaluasi elemen mana yang paling penting dan yang harus diprioritaskan, seperti judul, bio, dan tombol-tombol, saya juga mengatur ukuran, 'spacing', dan urutan sehingga informasi yang paling penting dapat terlihat dengan mudah. Pendekatan yang saya gunakan deapat membuat website saya lebih mudah dibaca ketika berubah dari layar yang luas (deskstop) ke layar yang lebih kecil (mobile) yang membuat layout lebih sempit.

3. Keterbatasan utama yang saya hadapi ketika membuat statik website adalah kesulitan untuk meprepresentasikan konten dinamis lebih efisien, seperti memperbarui informasi portofolio secara manual di file HTML/CSS. Seiring informasi yang saya tunjukkan bertambah, mengelola konten akan terasa lebih sulit dan tidak efisien. Setelah saya melakukan research lebih dalam Fungsionalitas Dinamis yang inginkan pada proyek selanjutnya adalah sebuah CRUD (Create, Read, Update, Delete) sistem yang simple untuk mengelola proyek, pengalaman, dan skill dari panel admin, sehingga data portofolio dapat ditambahkan atau diperbarui tanpa melakukan perubahan pada file statik secara langsung.



