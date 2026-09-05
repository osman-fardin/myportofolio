# My Portfolio

A personal portfolio built with Django, semantic HTML5, and responsive CSS3.
It presents my background, teaching experience, technical skills, and selected
projects, with a visual direction inspired by cloud infrastructure and route maps.

## Identity

- **Name:** Muhammad Osman Fardin
- **NPM:** 2506541723
- **Class:** PBP D

## Features

- Semantic About, Experience, Projects, Skills, and Contact sections
- Responsive layout for desktop, tablet, and mobile screens
- Desktop route navigation with anchor links to every section
- Featured Fasilkom Study Hub project with a live website preview
- Visible keyboard focus states and pointer-aware hover effects
- Reduced-motion support for visitors with motion sensitivity

## Technology

- Django
- HTML5
- CSS3
- WhiteNoise
- Gunicorn

## Local Setup

Clone the repository and enter its directory:

```bash
git clone https://github.com/osman-fardin/myportofolio.git
cd myportofolio
```

Create and activate a virtual environment:

```bash
python -m venv env
source env/bin/activate
```

On Windows, activate it with:

```powershell
env\Scripts\activate
```

Install the dependencies and prepare the local database:

```bash
pip install -r requirements.txt
python manage.py migrate
```

Start the development server:

```bash
python manage.py runserver
```

Open `http://127.0.0.1:8000/` in a browser.

## Progres Mingguan

### Minggu 1: Fondasi Proyek (26 Agustus - 1 September 2026)

- Membuat proyek Django dan mencatat seluruh dependency Python yang dibutuhkan.
- Mengganti nama package konfigurasi Django menjadi `portofolio` agar dapat
  dibedakan dengan folder root repositori.
- Menghubungkan folder global `templates/` dan `static/` dengan konfigurasi Django.
- Menambahkan template portofolio pertama, foto profil, dan stylesheet.
- Menyiapkan konfigurasi deployment untuk PWS, termasuk WhiteNoise untuk
  menyajikan berkas statis dan SQLite sebagai database sementara.

### Minggu 2: Pengembangan Portofolio Tugas 1 (2 - 7 September 2026)

- Memperbaiki bagian About menggunakan HTML semantik dan data pribadi yang akurat.
- Menambahkan pengalaman mengajar dan mentoring, keterampilan teknis, serta
  proyek Fasilkom Study Hub.
- Membuat sistem visual bertema hangat dan terinspirasi cloud menggunakan CSS
  custom properties untuk warna, border, spacing, dan waktu transisi.
- Menambahkan route rail pada desktop, layout section yang responsif, dan bagian
  Contact tersendiri.
- Menguji portofolio pada viewport sekitar `390px`, `768px`, dan `1440px`, serta
  memastikan tidak terdapat horizontal overflow yang tidak disengaja.
- Menambahkan indikator fokus untuk navigasi keyboard, hover khusus perangkat
  pointer, feedback saat link ditekan, smooth scrolling, dan dukungan
  `prefers-reduced-motion`.

## Refleksi Tugas 1

### 1. Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti `section`, `article`, atau `aside`? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat static web? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?

Pada Tugas 1 ini, saya memakai elemen semantik untuk menggambarkan fungsi dari setiap bagian halaman. Elemen `header` saya pakai sebagai pembuka yang berisi identitas dan navigasi, sedangkan `main` dipakai untuk membungkus konten utama portofolio. Bagian seperti About, Experience, Projects, Skills, dan Contact ditempatkan dalam `section` dan dihubungkan dengan heading memakai `aria-labelledby`. Saya juga memakai `article` untuk pengalaman dan proyek karena setiap item punya informasi yang bisa dipahami secara mandiri. Untuk route rail, saya memakai `aside` karena navigasi tersebut sifatnya sebagai informasi pendamping dari konten utama.

Menurut saya, struktur semantik membuat kode jadi lebih mudah dibaca dan dipahami. Penggunaan `nav`, `aria-label`, teks alternatif pada gambar, dan urutan heading juga membantu dari sisi aksesibilitas. Dari proses ini saya jadi lebih sadar kalau semantic HTML bukan sekadar memakai tag yang berbeda, tetapi juga membuat struktur halaman lebih jelas dan tidak terlalu bergantung pada CSS untuk menjelaskan fungsi setiap bagian.

### 2. Ketika Anda mengatur CSS Anda agar tetap responsive, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?

Tantangan terbesar yang saya alami muncul saat membuat route rail selebar `180px` di sisi kiri halaman. Layout-nya terlihat bagus di desktop, tetapi mulai terasa sempit saat dibuka di tablet maupun handphone. Bagian hero yang berisi teks dan foto juga membutuhkan ruang yang cukup banyak, jadi mempertahankan rail pada semua ukuran layar malah membuat kontennya terlalu sempit. Akhirnya, saya memakai breakpoint `900px` untuk menyembunyikan route rail dan memakai navigasi pada header sebagai penggantinya. Saya memilih ukuran ini berdasarkan ruang yang dibutuhkan konten, bukan hanya karena mengikuti ukuran perangkat tertentu.

Pada ukuran maksimal `600px`, hero, project preview, daftar pengalaman, skills, dan contact links saya ubah menjadi layout satu kolom. Saya memakai `minmax(0, 1fr)` dan `min-width: 0` supaya elemen CSS Grid bisa mengecil tanpa menimbulkan horizontal overflow. Gambar juga diberi ukuran dan `object-fit` yang sesuai supaya tidak terlihat gepeng atau terdistorsi. Saya lalu mencoba halaman pada lebar `390px`, `768px`, dan `1440px`. Dari pengujian ini saya sadar kalau responsive design tidak cukup diselesaikan dengan satu media query saja. Keterbacaan, urutan konten, navigasi, dan ruang yang tersedia tetap harus diperiksa pada setiap ukuran layar.

### 3. Website yang Anda buat saat ini adalah static web murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?

Salah satu keterbatasan yang saya temukan muncul ketika saya ingin memberi penanda pada route rail berdasarkan section yang sedang terlihat. Saya sempat mencoba CSS dengan `:target` dan `:has()`. Cara ini memang bisa menyorot link setelah ditekan, tetapi saat pengguna melakukan scroll secara manual, fragmen URL-nya tidak ikut berubah. Akibatnya, highlight tetap berada pada link sebelumnya dan tidak menggambarkan posisi pengguna dengan benar.

Pada akhirnya, saya menghapus cara tersebut dan hanya mempertahankan feedback yang hasilnya selalu akurat, yaitu `hover`, `focus-visible`, efek saat link ditekan, dan smooth scrolling. Menurut saya, lebih baik tidak menunjukkan status aktif daripada menampilkan informasi yang salah. Pada pengembangan berikutnya, saya ingin mencoba JavaScript dan `IntersectionObserver` untuk mendeteksi section yang sedang berada di viewport. Dari sini saya jadi tahu kalau HTML dan CSS sudah cukup untuk menyajikan informasi secara responsif, tetapi tetap punya keterbatasan saat halaman membutuhkan state dinamis yang mengikuti interaksi pengguna.

## AI Disclosure

Selama mengerjakan Tutorial dan Tugas 1, saya memakai OpenAI Codex sebagai tutor dan coding assistant. AI cukup banyak membantu saya dalam merencanakan workflow Git, membagi perubahan ke beberapa commit, mencari inspirasi visual, memahami semantic HTML dan responsive CSS, serta memeriksa kode dan README yang saya buat.

Saat memberi prompt, saya menyertakan rubrik tugas, source code terbaru, CV, screenshot website, dan gambaran desain yang saya inginkan. Saya menjelaskan bahwa saya ingin tema cloud computing dengan warna warm-brown, ukuran teks yang tidak terlalu besar, dan tampilan yang sederhana. Saya juga sering meminta penjelasan tentang letak perubahan, fungsi kode baru, dan alasan kode tersebut dibutuhkan supaya saya tidak hanya menyalinnya.

Saya tidak langsung memakai semua saran yang diberikan AI. Saya tetap memilih sendiri desain yang ingin digunakan, seperti route rail di sisi kiri, project preview yang sudah saya sukai, dan Skills sebagai section tersendiri. Saya juga memutuskan untuk belum memakai JavaScript. AI membantu mengedit beberapa bagian HTML dan memperbaiki CSS yang sempat terduplikasi, tetapi saya tetap membaca, mencoba, dan memeriksa hasilnya sendiri.

Salah satu keterbatasan yang saya temukan adalah ketika AI menyarankan `:target` dan `:has()` untuk menandai section aktif. Setelah dicoba, highlight-nya tidak ikut berubah saat halaman di-scroll secara manual. Karena hasilnya kurang akurat, saya memilih untuk menghapus fitur tersebut. Hasil akhir kemudian saya periksa dengan `python manage.py check`, `git diff --check`, serta pengujian pada viewport `390px`, `768px`, dan `1440px`. Jadi, AI saya gunakan sebagai teman diskusi dan alat bantu, bukan sebagai pengganti pemahaman dan keputusan saya sendiri.
