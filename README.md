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
- Experience dimuat dari endpoint JSON menggunakan Fetch API tanpa reload halaman
- Pencarian dan filter Experience dengan debouncing serta request cancellation
- Modal create Experience berbasis AJAX dengan response `201`, `400`, atau `403`
- Loading, empty, no-results, error, retry, result count, dan toast feedback
- Sanitasi input Experience menggunakan `strip_tags` dan output aman melalui
  DOM `textContent`
- Authorization Experience untuk guest, user biasa, Editor, dan superuser
- AJAX star dan unstar Experience per user tanpa reload halaman
- Penghapusan Experience berbasis POST dengan confirmation popover
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
- 73 automated test untuk AJAX, CSRF, XSS, autentikasi, permission, API privacy,
  serta isolasi data personal antar-user

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

Perintah `migrate` juga menerapkan migration `0005_experience_starred_by` yang
menambahkan relasi star per user pada Experience. Migration perlu dijalankan pada
setiap database baru, termasuk database deployment PWS.

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
3. Tambahkan permission **Main | project | Can change project** dan
   **Main | experience | Can change experience**.
4. Simpan grup tersebut.
5. Buka user yang ingin dijadikan Editor.
6. Masukkan user tersebut ke grup `Editor`, lalu simpan.

Editor dapat memperbarui Project dan Experience, tetapi tetap tidak dapat membuat
atau menghapus keduanya. Create dan delete hanya tersedia untuk superuser. Guest
diarahkan ke halaman login, sedangkan user yang sudah login tetapi tidak mempunyai
permission akan mendapat response `403 Forbidden`.

## Experience Routes

| Route | Method | Fungsi | Akses |
| --- | --- | --- | --- |
| `/experience/` | GET | Menampilkan kerangka halaman dan interaksi Experience | Publik |
| `/api/experiences/` | GET | Mengirim data Experience publik beserta state star | Publik |
| `/experience/add/` | GET/POST | Fallback form dan AJAX create | Superuser |
| `/experience/<uuid>/edit/` | GET/POST | Memperbarui Experience | Editor dan superuser |
| `/experience/<uuid>/delete/` | POST | Menghapus Experience | Superuser |
| `/experience/<uuid>/star/` | POST | Toggle star dan mengembalikan state terbaru | User login |

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
  menggabungkannya ke `main` melalui pull request.

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

### Minggu 6: AJAX Experience dan Web Interactivity (29 September - 5 Oktober 2026)

- Mengubah halaman Experience menjadi kerangka yang mengambil data dari endpoint
  JSON manual menggunakan Fetch API.
- Menambahkan loading, empty, no-results, error, retry, dan result count supaya
  kondisi halaman tetap jelas tanpa reload.
- Membuat pencarian title dengan debounce 400 ms serta `AbortController` agar
  request lama tidak menimpa hasil pencarian terbaru.
- Membuat modal add Experience menggunakan Popover API dan AJAX POST dengan
  `FormData`, CSRF token, validasi `ModelForm`, toast, dan status HTTP yang sesuai.
- Mempertahankan akses guest, user biasa, Editor, dan superuser pada view, bukan
  hanya dengan menyembunyikan tombol di tampilan.
- Membersihkan title dan description menggunakan `strip_tags`, lalu merender
  seluruh data server melalui DOM API dan `textContent` untuk mencegah XSS.
- Menambahkan fitur ekstra star dan unstar Experience melalui AJAX dengan jumlah
  serta state yang berbeda untuk setiap user.
- Menambahkan request cancellation, pencegahan double-click, error feedback, API
  privacy, serta test CSRF dan UUID 404 sebagai perlindungan tambahan.
- Membagi implementasi menjadi sepuluh conventional commit pada branch
  `feat/tugas-5-experience-ajax`, lalu merge ke `main` melalui pull request #18.
- Menambah cakupan menjadi 73 automated test dan memastikan Django check,
  migration check, syntax JavaScript, serta browser smoke test berhasil.

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

## Refleksi Tugas 5

### 1. Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX!

Debouncing adalah cara menunda pemanggilan function sampai user berhenti melakukan input selama waktu tertentu. Pada pencarian Experience, saya memakai delay 400 ms. Jadi, ketika saya mengetik beberapa huruf dengan cepat, aplikasi tidak langsung mengirim request untuk setiap huruf, tetapi menunggu sampai saya berhenti mengetik. Cara ini mengurangi request yang tidak perlu, membuat hasil pencarian tidak terlalu sering berkedip, dan mengurangi beban server maupun network. Saya juga memakai `AbortController` untuk membatalkan request lama supaya response yang terlambat tidak menimpa hasil terbaru.

### 2. Jelaskan fungsi dari penggunaan `await` ketika kita menggunakan `fetch()`! Apa yang akan terjadi jika kita tidak menggunakan `await`?

`fetch()` langsung menghasilkan Promise karena request berjalan secara asynchronous. `await` dipakai agar function menunggu Promise tersebut selesai sebelum memakai response-nya. Setelah itu, `await response.json()` masih diperlukan karena membaca body JSON juga asynchronous. Tanpa `await`, variabel yang saya pakai masih berisi Promise, bukan response atau data Experience yang sebenarnya. Akibatnya, kode yang mencoba membaca `response.ok` atau membuat card dari data tersebut dapat berjalan terlalu cepat dan menghasilkan error. Proses ini tetap tidak membekukan seluruh browser karena hanya alur di dalam function `async` yang menunggu.

### 3. Jelaskan apa itu serangan XSS (`Cross-Site Scripting`) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django!

XSS terjadi ketika input berbahaya berhasil dijalankan sebagai script di browser pengguna lain. Template Django melakukan auto-escaping secara default, tetapi data AJAX dirender sendiri melalui JavaScript. Kalau data dari server langsung dimasukkan dengan `innerHTML`, browser dapat menganggap isinya sebagai markup aktif. Karena itu, pada Experience saya membuat elemen dengan DOM API dan mengisi teks memakai `textContent`. Input title dan description juga dibersihkan di server melalui `strip_tags` pada `clean_title()` dan `clean_description()`. Menurut saya dua lapisan ini tetap diperlukan karena data yang sudah berada di database belum tentu otomatis aman.

## AI Disclosure

Selama mengerjakan Tutorial sampai Tugas 5, saya memakai OpenAI Codex sebagai tutor dan coding assistant. AI membantu menjelaskan konsep yang baru saya pakai, merencanakan workflow Git, membagi pengerjaan menjadi beberapa module dan commit, membaca error, serta memeriksa hasil test. Pada Tugas 5, AI juga membantu mengedit beberapa bagian view, JavaScript, CSS, dan automated test untuk alur AJAX Experience. Saya tetap menentukan bagian Experience yang dikembangkan, fitur ekstra star, pembagian akses tiap role, dan bentuk akhir interaksinya.

Saat memberi prompt, saya biasanya menyertakan rubrik, source code terbaru, error yang muncul, atau hasil command Git. Saya meminta pekerjaan dibagi per module, setiap konsep baru dijelaskan, dan perubahan diperiksa sebelum commit. Cara ini membantu saya mengikuti alasan di balik `fetch()`, `await`, debounce, `AbortController`, `FormData`, CSRF, serta penggunaan `textContent`, bukan hanya melihat hasil akhirnya.

Saya tidak langsung menganggap output AI pasti benar karena AI tetap bisa salah menempatkan kode atau melewatkan behavior lama. Contohnya, saat menambahkan test star Experience, class test sempat tersisip sebelum seluruh test JSON selesai. Masalah tersebut ditemukan saat review struktur file dan diperbaiki sebelum test dijalankan. Saya juga memastikan response star hanya berisi state dan jumlah, sanitizer tidak menggantikan output escaping, elemen modal dicek sebelum event listener dipasang, serta request pencarian lama dibatalkan agar hasilnya tidak tertukar.

Karena itu, saya tetap membaca diff, mencoba alur lewat browser, dan memeriksa hasilnya menggunakan `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `python manage.py test`, `node --check`, dan `git diff --check`. Pada akhir implementasi Tugas 5, seluruh 73 automated test berhasil dijalankan. Menurut saya AI paling membantu untuk memberi arah dan mempercepat pemeriksaan, tetapi keputusan desain, kesesuaian rubrik, dan verifikasi akhir tetap tidak bisa diserahkan begitu saja ke AI.

Contoh prompt dan cara saya memakai hasilnya dapat dilihat pada
[AI Prompt Log](docs/ai-prompt-log.md).
