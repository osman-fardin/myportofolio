# My Portfolio

A personal portfolio built with Django using the Model-View-Template architecture.
It presents my background, experience, and database-backed projects through a
minimal multi-page interface with a warm visual theme.

## Identity

- **Name:** Muhammad Osman Fardin
- **NPM:** 2506541723
- **Class:** PBP D

## Features

- Minimal homepage with direct paths to Projects and About
- Database-backed Experience and Projects pages
- Experience management melalui form create dan update yang menggunakan
  `ModelForm` serta validasi tanggal
- Penghapusan Experience yang hanya menerima request POST dan dilengkapi
  confirmation popover
- Pencarian dan filter Experience berdasarkan judul, kategori, dan status
- Endpoint `/api/experiences/` yang menyediakan data terfilter dalam format JSON
- Halaman Experience yang menampilkan kembali data setelah proses deserialisasi JSON
- Project and experience management through Django Admin
- Shared navigation and footer using Django template inheritance
- Responsive layouts for desktop, tablet, and mobile screens
- Fullscreen navigation menu with subtle page transitions
- Visible keyboard focus states and reduced-motion support
- Registrasi, login, dan logout menggunakan sistem autentikasi bawaan Django
- Session login dan cookie `last_login` untuk mencatat waktu login terakhir
- Authorization Project untuk guest, user biasa, Editor, dan superuser
- Update Project melalui permission `main.change_project`, sedangkan create dan
  delete tetap dibatasi untuk superuser
- Sistem star per user melalui relasi ManyToMany, request POST, dan CSRF token
- Filter personal **Starred by me** yang dapat digabungkan dengan pencarian judul
- Endpoint JSON Project dengan allowlist field publik agar identitas akun yang
  memberi star tidak ikut dikirim
- Automated test untuk autentikasi, permission, API privacy, dan isolasi data
  personal antar-user

## Technology

- Django 5.2
- Python
- HTML5
- CSS3
- JavaScript
- SQLite
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

## Editor Role Setup

Role Editor memakai Django Group dan permission bawaan model. Karena data grup
tersimpan di database, setup ini perlu dilakukan kembali pada database lokal
maupun PWS dan tidak ikut terbawa hanya melalui Git.

Buat superuser jika belum tersedia:

```bash
python manage.py createsuperuser
```

Jalankan server, lalu buka `http://127.0.0.1:8000/admin/` dan login menggunakan
akun superuser. Setelah itu:

1. Buka **Authentication and Authorization -> Groups**.
2. Pilih **Add group** dan beri nama `Editor`.
3. Tambahkan permission **Main | project | Can change project**.
4. Simpan grup tersebut.
5. Buka user yang ingin dijadikan Editor.
6. Masukkan user tersebut ke grup `Editor`, lalu simpan.

Editor dapat membuka dan menyimpan form update Project, tetapi tetap tidak dapat
membuat atau menghapus Project. Create dan delete hanya tersedia untuk
superuser. Guest diarahkan ke halaman login, sedangkan user yang sudah login
tetapi tidak mempunyai permission akan mendapat response `403 Forbidden`.

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

### Minggu 3: Implementasi MVT dan Redesign Multi-Page (8 - 14 September 2026)

- Membuat model `Project`, migration, dan registrasi Django Admin agar data
  proyek dapat disimpan dan dikelola melalui database.
- Menghubungkan model, view, URL, dan template untuk menampilkan Experience
  dan Projects secara dinamis.
- Menambahkan empty state agar halaman tetap memberikan informasi ketika
  database belum memiliki data.
- Membuat test untuk memeriksa route, template, data dari model, dan empty state.
- Mengubah portofolio menjadi struktur multi-page dengan shared navigation
  dan footer melalui template inheritance.
- Membuat project browser interaktif serta memperbaiki tampilan About dengan
  panel navy dan background cloudscape yang responsif.
- Memeriksa hasil menggunakan `python manage.py check`,
  `python manage.py test`, `git diff --check`, dan pengujian desktop serta mobile.

### Minggu 4: Form dan Data Delivery Experience (15 - 21 September 2026)

- Membuat `ExperienceForm` menggunakan `ModelForm` untuk mengelola seluruh field
  yang dapat diisi pengguna tanpa mengekspos UUID.
- Menambahkan validasi agar tanggal selesai tidak dapat lebih awal daripada
  tanggal mulai.
- Membuat alur create dan update yang menggunakan satu template form bersama.
- Menambahkan penghapusan berbasis POST, CSRF token, dan confirmation popover
  agar data tidak terhapus hanya karena URL dibuka.
- Membuat endpoint JSON untuk Experience dan helper filter bersama berdasarkan
  judul, kategori, serta status ongoing atau completed.
- Menampilkan data Experience pada halaman setelah melalui serialization dan
  deserialization JSON.
- Menambahkan filter responsif, selected state, tombol Clear, dan empty state
  yang membedakan database kosong dengan hasil filter yang tidak ditemukan.
- Menambah cakupan test menjadi 23 test untuk memeriksa form, validasi, CRUD,
  keamanan delete, JSON, filter, 404, dan deserialization.
- Membagi implementasi ke beberapa conventional commit pada feature branch dan
  menggabungkannya ke `main` melalui pull

### Minggu 5: Authentication, Authorization, dan Personal Stars (22 - 28 September 2026)

- Menambahkan alur registrasi, login, dan logout menggunakan autentikasi bawaan
  Django serta cookie untuk menampilkan waktu login terakhir.
- Membatasi create dan delete Project hanya untuk superuser, sedangkan user yang
  tergabung dalam grup Editor dapat mengubah Project melalui permission
  `main.change_project`.
- Membuat form update Project dengan `instance=project` agar object lama diperbarui
  dan tidak menghasilkan data duplikat.
- Menambahkan sistem star berbasis user melalui relasi ManyToMany, request POST,
  CSRF token, status Star atau Starred, dan jumlah star pada setiap Project.
- Menambahkan filter **Starred by me** yang dapat digabungkan dengan pencarian
  judul dan tetap memisahkan koleksi milik setiap user.
- Membatasi endpoint JSON Project menggunakan allowlist field publik agar daftar
  username pemberi star tidak ikut terekspos.
- Menambahkan empty state personal, kontrol filter responsif, dan focus state
  untuk penggunaan keyboard.
- Menambah cakupan menjadi 49 automated test untuk memeriksa authentication,
  cookie, permission setiap role, personal stars, API privacy, dan fitur lama.
- Membagi implementasi ke beberapa feature branch dan conventional commit, lalu
  menggabungkannya ke `main` melalui pull request setelah seluruh test lulus.

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

## Refleksi Tugas 2

### 1. Jelaskan bagaimana alur request hingga halaman Projects dapat ditampilkan pada browser.

Ketika saya membuka `/projects/`, request dari browser pertama kali masuk ke `portofolio/urls.py`. Dari sana, `include('main.urls')` meneruskan request ke URL milik aplikasi `main`. Di `main/urls.py`, path `projects/` sudah dihubungkan dengan function `show_projects` dan diberi nama `main:show_projects`.

Di dalam `show_projects`, saya mengambil data dari model menggunakan `Project.objects.all()`. Data tersebut berbentuk QuerySet dan dimasukkan ke context dengan nama `project_list`. Context lalu dikirim ke `projects.html` menggunakan `render()`. Di template tersebut, saya memakai `{% for project in project_list %}` supaya semua project dari database dapat ditampilkan sebagai HTML di browser.

Saya juga membuat route detail yang memakai UUID dari setiap project. Ketika salah satu project dipilih, `show_project_detail` akan mencari datanya menggunakan `get_object_or_404()`. Jadi, project yang ada dapat ditampilkan, sedangkan UUID yang tidak ditemukan akan menghasilkan halaman 404 dan bukan server error. Dari proses ini saya jadi lebih memahami kalau halaman yang terlihat di browser sebenarnya melewati alur URL, view, model, context, lalu template terlebih dahulu.

### 2. Mengapa data Project disimpan di model dan tidak ditulis langsung di template?

Pada versi awal portofolio, informasi Fasilkom Study Hub masih saya tulis langsung di dalam HTML. Cara tersebut memang cukup untuk halaman statis, tetapi setiap kali ingin menambah atau mengubah project, saya harus membuka dan mengedit struktur template secara langsung. Data dan tampilan akhirnya bercampur sehingga semakin sulit dikelola ketika jumlah project bertambah.

Sekarang saya menyimpan informasi project di model `Project`, sedangkan template hanya mengatur cara menampilkannya. Data dapat ditambahkan melalui Django Admin, diurutkan menggunakan `display_order`, dan diuji tanpa bergantung pada isi HTML yang ditulis manual. Template `projects.html` juga dapat digunakan kembali untuk semua object melalui loop yang sama. Dari perubahan ini saya merasa pemisahan data dan tampilan membuat proyek lebih mudah dikembangkan karena menambah project baru tidak lagi membutuhkan perubahan pada struktur halaman.

### 3. Apa perbedaan antara `makemigrations` dan `migrate` pada Django?

Menurut pemahaman saya, `makemigrations` dan `migrate` sama-sama berhubungan dengan perubahan struktur database, tetapi tugasnya berbeda. `makemigrations` membaca perubahan pada model lalu membuat file migration sebagai catatan tentang perubahan schema yang perlu dilakukan. Perintah ini belum langsung mengubah database yang sedang digunakan.

Sementara itu, `migrate` membaca file migration tersebut dan benar-benar menerapkannya ke database aktif. Dalam Tugas 2, setelah saya membuat model `Project`, saya menjalankan `makemigrations` untuk menghasilkan file `0002_project.py`. Setelah memeriksa isi file tersebut, saya menjalankan `migrate` agar tabel untuk model `Project` dibuat di database lokal. Jadi, saya memahami `makemigrations` sebagai tahap menyiapkan instruksi perubahan, sedangkan `migrate` adalah tahap menjalankan instruksi tersebut pada database.

## Refleksi Tugas 3

### 1. Mengapa kita menggunakan ModelForm pada Django alih-alih membuat form HTML secara manual? Mengapa kita wajib menambahkan `{% csrf_token %}` pada form tersebut?

`ModelForm` membuat form tetap terhubung dengan model sehingga field, tipe data, dan validasi dasar tidak perlu ditulis ulang secara manual. Pada `ExperienceForm`, saya hanya memasukkan field yang boleh diisi pengguna dan menambahkan validasi tanggal melalui `clean()`. Form yang sama juga dapat digunakan untuk create dan update dengan memberikan `instance=experience`. Sementara itu, `{% csrf_token %}` melindungi request POST dari website lain yang mencoba mengirim request atas nama pengguna. Jadi, `ModelForm` mengatur data dan validasi, sedangkan CSRF token melindungi proses pengirimannya.

### 2. Mengapa JSON lebih disukai dalam pengembangan aplikasi web modern dibandingkan XML?

JSON lebih sering digunakan karena strukturnya ringkas, mudah dibaca, dan dekat dengan object JavaScript maupun dictionary Python. Dibandingkan XML yang menggunakan tag pembuka dan penutup, JSON biasanya menghasilkan payload yang lebih sederhana untuk kebutuhan API. Dukungan JSON juga sudah tersedia luas pada browser dan framework seperti Django. Namun, XML bukan berarti tidak berguna karena masih cocok untuk data dengan namespace, schema ketat, atau struktur dokumen kompleks. Untuk data Experience yang berbentuk record sederhana, JSON lebih sesuai dengan kebutuhan proyek saya.

### 3. Jelaskan alur yang terjadi saat fungsi view mengembalikan data portofolio dalam bentuk JSON. Mengapa model Django perlu melalui serialization terlebih dahulu?

Request ke `/api/experiences/` diarahkan ke `get_experiences_json`. View tersebut mengambil QuerySet melalui `_get_filtered_experiences()`, lalu mengubahnya menjadi JSON menggunakan `serializers.serialize()`. Hasilnya dikirim lewat `HttpResponse` dengan content type JSON. Serialization diperlukan karena QuerySet dan model Django adalah object Python yang tidak dapat langsung dikirim melalui HTTP. Pada halaman Experience, JSON tersebut di-decode, di-deserialize kembali menjadi object Experience, dimasukkan ke context sebagai `experience_list`, lalu ditampilkan oleh template. Helper filter yang sama dipakai oleh JSON dan halaman HTML supaya hasil keduanya tetap konsisten.

## AI Disclosure

## AI Disclosure

Selama mengerjakan Tutorial sampai Tugas 4, saya memakai OpenAI Codex sebagai tutor dan coding assistant. AI lebih banyak membantu menjelaskan konsep yang baru saya pakai, merencanakan workflow Git, membagi pengerjaan menjadi beberapa module dan commit, membaca error, serta memeriksa hasil test. Pada Tugas 4, saya memakainya untuk memahami Django Group dan Permission, relasi ManyToMany per user, authorization setiap role, dan privacy pada endpoint JSON.

Saat memberi prompt, saya biasanya menyertakan rubrik, source code terbaru, error yang muncul, atau hasil command Git. Saya juga meminta penjelasan tentang letak perubahan dan fungsi kode baru sebelum melanjutkan. Sebagian besar langkah tetap saya ketik dan coba sendiri mengikuti arahan tersebut. AI sesekali membantu memperbaiki bagian tertentu ketika saya meminta, tetapi keputusan untuk memakai role Editor, fitur **Starred by me**, pembagian branch, dan hasil akhirnya tetap saya tentukan setelah mencoba fiturnya.

Saya tidak langsung memakai semua saran AI karena hasilnya tetap perlu diperiksa. Contohnya, pada filter personal stars saya sempat salah menempatkan `else` sehingga request biasa menghasilkan QuerySet kosong. AI membantu menunjukkan masalah indentasinya, lalu saya memeriksa kembali alurnya. Test lama juga awalnya masih mengharapkan username pemberi star muncul di JSON, padahal behavior tersebut perlu dihapus untuk menjaga privacy.

Karena itu, saya tetap membaca diff dan memeriksa hasilnya menggunakan `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `python manage.py test`, dan `git diff --check`. Pada akhir implementasi Tugas 4, seluruh 49 automated test berhasil dijalankan.

Contoh prompt dan cara saya memakai hasilnya dapat dilihat pada
[AI Prompt Log](docs/ai-prompt-log.md).
