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
- Form HTML update Project memakai permission `main.change_project`; API DRF
  Projects membatasi create, update, dan delete untuk superuser
- Sistem star per user melalui relasi ManyToMany, request POST, dan CSRF token
- Filter personal **Starred by me** yang dapat digabungkan dengan pencarian judul
- API DRF Projects di `/api/v1/projects/` dengan serializer, validasi, dan permission
- Daftar, detail, pencarian, create, star, dan delete Projects melalui Fetch API
  tanpa reload, dengan preview statis dan fallback HTML tetap tersedia
- Loading daftar/detail, empty state, toast error API, dan pencegahan submit ganda
- Payload publik Project hanya memuat count dan status star, tanpa identitas akun
- 186 automated test untuk fitur lama, serializer, API, integrasi halaman, CSRF,
  XSS, permission, privacy, serta isolasi data personal antar-user

## Technology

- Django 5.2
- Django REST Framework 3.18
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
python -m pip install -r requirements.txt
python manage.py migrate
```

Environment yang dipakai untuk checkpoint Tutorial 07: Python 3.14.6, Django
5.2.17, dan DRF 3.18.3. Requirement tetap `django~=5.2` dan menambahkan
`djangorestframework~=3.18.3`; versi patch hasil install bisa berbeda.
Tutorial ini memakai model dan data lama, tanpa migration baru.

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

Pada route HTML lama, Editor dapat memperbarui Project dan Experience melalui
permission masing-masing, tetapi tidak dapat membuat atau menghapus keduanya.
Guest yang membuka tindakan yang memerlukan login diarahkan ke halaman login;
akun login tanpa izin mendapat `403 Forbidden`.

**API Projects mengikuti aturan Tutorial 07:** hanya superuser yang dapat
create, PUT/PATCH, atau delete. Jadi Editor tetap bisa memakai form HTML
`/projects/<uuid>/edit/`, tetapi mendapat 403 saat menulis ke API Projects.
`is_staff` dan nama grup saja tidak memberikan izin API tersebut. Perbedaan ini
disengaja untuk menjaga fitur lama dan diuji pada API serta halaman.

Halaman Experience masih memakai route Tugas 5 di bawah. Pada progres Tugas 6,
serializer, permission empat role, serta API daftar/create sudah tersedia.
Integrasi halaman ke DRF dilanjutkan pada checkpoint berikutnya.

## Projects API: Tutorial 07

### Route dan akses

| Endpoint | Method | Hasil sukses | Akses |
| --- | --- | --- | --- |
| `/api/v1/projects/` | GET/HEAD | Array datar, 200 | Publik |
| `/api/v1/projects/` | POST | Object baru, 201 | Superuser |
| `/api/v1/projects/<uuid>/` | GET/HEAD | Satu object, 200 | Publik |
| `/api/v1/projects/<uuid>/` | PUT/PATCH | Object terbaru, 200 | Superuser |
| `/api/v1/projects/<uuid>/` | DELETE | Body kosong, 204 | Superuser |
| `/api/v1/projects/<uuid>/star/` | POST | Object dengan state star terbaru, 200 | User login |

Ganti `<uuid>` dengan ID dari daftar dan pertahankan slash terakhir. Namespace
URL adalah `api`, dengan nama `project-list`, `project-detail`, dan `project-star`.
GET, HEAD, dan OPTIONS tidak mengubah data pada endpoint baca. Endpoint star
hanya menerima POST; akun login yang mengirim GET mendapat 405.

| Aksi API Projects | Guest | User biasa | Editor | Superuser |
| --- | --- | --- | --- | --- |
| Baca daftar/detail dan pencarian | Ya | Ya | Ya | Ya |
| Star/unstar | 403 | Ya | Ya | Ya |
| Create, PUT/PATCH, delete | 403 | 403 | 403 | Ya |

`?title=...` mencari judul tanpa membedakan huruf besar/kecil dan mengabaikan
spasi di tepi. `?starred=mine` membatasi hasil ke star akun yang sedang login;
untuk guest hasilnya `[]`. Kedua filter bisa digabung. Urutan hasil tetap
`display_order`, `title`, lalu `id`. Daftar kosong atau pencarian tanpa hasil
mengembalikan `[]` dengan 200, bukan 404.

### Field, validasi, dan penyesuaian contoh

Response berupa object langsung dengan 12 field: `id`, sembilan field input di
bawah, `star_count`, dan `is_starred`. Tidak ada wrapper `pk/fields`. `id` dan
kedua field star read-only; input klien tidak bisa menentukan akun pemberi star.
`starred_by`, username, email, dan data akun lainnya tidak ikut dikirim.

| Contoh tutorial | Field di proyek ini |
| --- | --- |
| `tech_stack` | `technologies`, satu teknologi per baris |
| `project_url` | `live_url` wajib; `source_url` opsional |
| `project_image_url` | `thumbnail_path`, path static opsional, bukan upload atau URL gambar |
| `starred_by_names` | Tidak ditambahkan; kontrak privacy lama hanya count dan status |
| Template `project.html` | `templates/projects.html` dan komponen detail/modal lama |

Contoh payload create untuk dicoba pada database pengujian sendiri:

```json
{
  "title": "Portfolio percobaan",
  "project_type": "Personal Website",
  "role": "Developer",
  "description": "Data percobaan integrasi API.",
  "technologies": "Django\nJavaScript",
  "thumbnail_path": "",
  "live_url": "https://example.com/",
  "source_url": "",
  "display_order": 0
}
```

Field teks wajib adalah `title`, `project_type`, `role`, `description`, dan
`technologies`. Serializer membuang tag HTML dan spasi tepi, lalu menolak teks
yang kosong setelah dibersihkan. `live_url` wajib berupa URL valid;
`source_url` boleh kosong. `thumbnail_path` boleh kosong dan `display_order`
memakai default 0 jika tidak dikirim. Batas panjang dan rentang mengikuti model.
Serializer tidak menjalankan `ProjectForm.clean()`; jalur API mempunyai validasi
sendiri. Output tetap memakai auto-escaping Django atau DOM `textContent`.

PUT membutuhkan seluruh field wajib. PATCH cukup field yang berubah, misalnya
`{"title": "Judul baru"}`, dan mempertahankan field lainnya. Field opsional yang
tidak dikirim pada PUT tidak otomatis dianggap harus dikosongkan.

### Session, CSRF, dan respons error

Semua view API memakai `SessionAuthentication`. Login portofolio dan login
Browsable API di `/api-auth/login/` memakai session Django yang sama. Buka
`/api/v1/projects/` langsung untuk Browsable API, atau tambahkan `?format=json`
untuk JSON. Fetch mengirim `Accept: application/json`; create mengirim JSON dengan
`Content-Type: application/json`. Function view menampilkan form input JSON
mentah pada Browsable API, bukan form otomatis untuk setiap field serializer.

Setiap POST/PUT/PATCH/DELETE lewat session harus menyertakan `X-CSRFToken`.
Halaman Projects merender token juga untuk user biasa dan Editor yang tidak
mempunyai modal create. Cookie session dikirim browser pada origin yang sama;
izin tetap diperiksa server, bukan hanya melalui tombol yang terlihat.

| Status | Makna |
| --- | --- |
| 200 | Baca/update/star berhasil, termasuk hasil pencarian kosong |
| 201 | Project dibuat |
| 204 | Project dihapus, tanpa body; jangan panggil `.json()` |
| 400 | Input tidak valid atau JSON rusak; error per field |
| 403 | Izin ditolak, belum login untuk tindakan tertentu, atau CSRF gagal |
| 404 | UUID tidak ditemukan setelah permission lolos |
| 405 | Method tidak didukung setelah autentikasi/permission lolos |

Error validasi berbentuk `{"title": ["pesan"]}`; error umum memakai
`{"detail": "pesan"}`. UI menampilkannya lewat toast dan mempertahankan input
modal saat gagal. Respons HTML tak terduga memakai pesan status HTTP. Guest yang
mencoba mutation mendapat 403, termasuk pada UUID yang tidak ada, karena
permission diperiksa sebelum pencarian object.

Star memakai akun dari `request.user`. Dua POST berarti star lalu unstar, jadi
tidak ada retry otomatis. Tombol star/delete untuk project yang sama dikunci
selama mutation. Setelah berhasil, daftar dimuat ulang memakai filter aktif.
Delete membersihkan detail jika masih menunjuk project yang dihapus; respons
terlambat tidak mengganti pilihan project lain. Jika jaringan putus setelah
request dikirim, baca ulang state sebelum memutuskan mengulang mutation.

### Struktur dan route lama

`main/serializers.py` menangani representasi/validasi, `main/permissions.py`
menangani izin, dan `main/api_views.py` memakai `@api_view` serta `Response`.
`main/api_urls.py` didaftarkan pada prefix `/api/v1/` di `portofolio/urls.py`.
Queryset daftar/detail memakai prefetch relasi star; belum memakai optimasi
Count/Exists. Model serta migration tidak berubah.

`main/views.py` tetap menyediakan halaman dan fallback ORM tanpa deserialize
JSON lama. Named URL disalurkan melalui atribut `data-*` ke
`static/js/projects.js`. Script memakai event delegation, debounce 400 ms,
AbortController, dan loading untuk daftar/detail yang berjalan bersamaan.

| Route lama yang tetap tersedia | Fungsi |
| --- | --- |
| `/projects/`, `/projects/<uuid>/` | Halaman dan fallback HTML |
| `/api/projects/` | JSON lama; tidak lagi dipakai Fetch Projects |
| `/projects/add/` | Form create superuser dan jalur AJAX lama |
| `/projects/<uuid>/edit/` | Form update Editor/superuser, belum berupa modal PATCH |
| `/projects/<uuid>/star/` | POST fallback star untuk akun login |
| `/projects/<uuid>/delete/` | POST fallback delete superuser |

Modal edit AJAX Projects bukan bagian inti yang ditambahkan pada checkpoint
ini. API PUT/PATCH sudah berfungsi; form update lama tetap dapat dipakai.

## Experience Routes

| Route | Method | Fungsi | Akses |
| --- | --- | --- | --- |
| `/api/v1/experiences/` | GET/HEAD, POST | Daftar DRF dan create JSON | Baca publik; create superuser |
| `/experience/` | GET | Menampilkan kerangka halaman dan interaksi Experience | Publik |
| `/api/experiences/` | GET | Mengirim data Experience publik beserta state star | Publik |
| `/experience/add/` | GET/POST | Fallback form dan AJAX create | Superuser |
| `/experience/<uuid>/edit/` | GET/POST | Memperbarui Experience | Editor dan superuser |
| `/experience/<uuid>/delete/` | POST | Menghapus Experience | Superuser |
| `/experience/<uuid>/star/` | POST | Toggle star dan mengembalikan state terbaru | User login |

Progres API Tugas 6 pada 7 November: `api:experience-list` mendukung filter
`title`, `category`, dan `status=ongoing/completed`, termasuk kombinasinya.
Daftar berupa array datar dengan 12 field publik dari ExperienceSerializer;
`description` mentah tetap tersedia bersama `description_points`. Akun pemberi
star tidak dikirim; hanya count dan status sesuai request pengguna.
Urutan memakai `-started_at`, lalu UUID sebagai penentu saat tanggal sama.
Kategori tidak dikenal menghasilkan `[]`; status tidak dikenal diabaikan seperti
jalur JSON lama. Hasil kosong tetap 200.

POST memakai SessionAuthentication dan header CSRF, menghasilkan 201 saat valid,
400 untuk error serializer, serta 403 untuk guest, user biasa, Editor, atau
staff tanpa hak superuser. Izin update Editor tidak berlaku untuk membuat data.
Validasi mencakup title/description, kategori/URL, dan rentang tanggal. Field
hasil perhitungan read-only. Browsable API tersedia pada URL yang sama; gunakan
`Accept: application/json` atau `?format=json` dengan header Accept yang menerima
JSON. Permintaan yang membatasi Accept ke HTML saja sambil memaksa format JSON
akan ditolak dengan 406.

Saat ini endpoint detail/update/delete/star DRF dan migrasi UI masih menyusul;
route lama tetap dipakai halaman. Test list/create baru berjumlah 19 dan total
test main mencapai 186. Test penolakan memeriksa record dan relasi star; test
CSRF memakai `.login()` serta APIClient dengan CSRF enforcement. Cek HTTP lokal
membuktikan JSON dan HTML Browsable API bisa dibuka, serta kedua halaman lama
tetap mengembalikan 200. PWS belum diverifikasi ulang untuk perubahan ini.

## Verifikasi Tutorial 07

Dari folder yang berisi `manage.py`, aktifkan environment proyek lalu jalankan:

```bash
python manage.py check
python manage.py test main.tests_api
python manage.py test main
python manage.py makemigrations --check --dry-run
python -m pip check
node --check static/js/projects.js
node --check static/js/experiences.js
node --check static/js/toast.js
git diff --check
```

Hasil lokal terakhir pada 3 November 2026: **140 test main lulus**, terdiri dari
73 test lama, 48 test serializer/permission/API, dan 19 test halaman Projects.
Ketigabelas kelompok pengujian tutorial tercakup dengan field aktual, jadi
jumlah method tidak harus sama dengan 13 pada contoh. Test penolakan memeriksa
database; test CSRF memakai `APIClient(enforce_csrf_checks=True)` dan `.login()`.
`force_authenticate` hanya dipakai untuk memilih role pada test yang sesuai.
Check, pemeriksaan migrasi, dependency, sintaks JavaScript, dan whitespace lolos.

Eksperimen regresi permission juga dijalankan di memori test: ketika semua akun
login sementara diizinkan menulis, test penolakan mendeteksi POST user biasa,
Editor, dan staff mendapat 201 alih-alih 403. Setelah patch sementara dilepas,
test yang sama lulus lagi. File permission dan data lokal tidak berubah.

Browser diuji dengan server serta database sementara: guest, user biasa, Editor,
dan superuser; list/detail/search, preview, Back/Forward, filter personal,
create/star/delete tanpa reload, CSRF, sesi berakhir, validasi, submit ganda,
request lambat, error/pemulihan, escaping, dan fallback tanpa JavaScript.
Layout diperiksa pada 390/768/1440 px; indikator loading tambahan diperiksa pada
390/1440 px. Data lokal tetap satu Project dan dua Experience.

Warning WhiteNoise tentang folder `staticfiles/` yang belum ada masih muncul
saat test lokal, tanpa menggagalkan test. Checkpoint ini tidak menjalankan
`collectstatic`, mengubah PWS, atau membuktikan deployment sudah memakai versi
terbaru. Verifikasi lokal memakai environment proyek yang sudah terpasang;
instalasi dari environment kosong belum diuji ulang pada checkpoint ini.

### Status checkpoint dan pengumpulan

Implementasi Tutorial 07 berada pada branch `feat/tutorial-7-drf-projects`.
Commit implementasi terakhir sebelum dokumentasi ini adalah `0653a49`.
Commit dokumentasi berikutnya perlu direview dan dibuat sendiri, kemudian
dipush. Hash final pengumpulan dicatat sesudah commit/integrasi selesai, sehingga
hash implementasi di atas belum dinyatakan sebagai hash pengumpulan akhir.

Push, PR/merge, smoke PWS, akses commit publik, dan submit SCELE belum
diverifikasi pada checkpoint dokumentasi ini. Sebelum menyatakan selesai:

1. Review diff dan stage path spesifik; jangan ikutkan `.playwright-cli/`,
   database, environment, atau credential.
2. Commit dokumentasi, push branch, lalu review dan merge melalui PR sesuai alur
   kerja. Ambil hash final Tutorial 07 setelah integrasi dan simpan terpisah.
3. Deploy sendiri memakai alur PWS yang sudah ada. Periksa baca halaman/API,
   login, dan satu operasi tulis pada record percobaan saja, termasuk CSRF dari
   origin HTTPS yang benar. Jika gagal, baca error sebelum mengubah konfigurasi.
4. Buka tautan commit GitHub sebagai pengunjung dan pastikan dapat diakses publik,
   lalu submit link commit itu di slot Tutorial 07 SCELE sebelum **4 November
   2026 pukul 23.59 WIB**.

Tugas 6 baru melanjutkan DRF pada Experience setelah checkpoint tutorial.
Tenggatnya **9 November 2026 pukul 23.59 WIB**, dengan hash pengumpulan terpisah.
Fitur dan empat refleksi Tugas 6 belum diklaim selesai dalam dokumen ini.

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

### Implementasi Tutorial 07 (2 - 3 November 2026)

- Menambahkan DRF 3.18.3 tanpa mengganti versi mayor Django atau model lama.
- Membuat ProjectSerializer dengan field eksplisit, sanitasi, validasi URL,
  UUID/count/state read-only, dan privacy akun pemberi star.
- Memisahkan permission owner-only API Projects dari permission form HTML Editor.
- Menambahkan API list/create, detail/PUT/PATCH/delete, serta toggle star dengan
  session dan CSRF, lalu mengintegrasikan list/detail/create/star/delete ke Fetch.
- Mempertahankan preview statis, filter judul/personal, form fallback, desain,
  dan fitur Experience dari Tugas 5.
- Memeriksa respons lambat agar tidak menimpa detail baru; mencegah submit ganda
  dan mutation star/delete yang bersamaan untuk project yang sama.
- Menambahkan loading yang terlihat setelah audit menemukan bahwa `aria-busy`
  saja belum memberi feedback visual.
- Mencapai 140 test main lulus, disertai pemeriksaan browser pada database
  sementara. Test lama tidak dihapus untuk mengejar hasil hijau.
- Membagi implementasi menjadi conventional commit per behavior pada feature
  branch. Push, integrasi PR, deployment, dan submit dicatat setelah dilakukan.

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

Selama mengerjakan Tutorial sampai Tugas 5 dan Tutorial 07, saya memakai OpenAI Codex sebagai tutor dan coding assistant. AI membantu menjelaskan konsep yang baru saya pakai, merencanakan workflow Git, membagi pengerjaan menjadi beberapa module dan commit, membaca error, serta memeriksa hasil test. Pada Tugas 5, AI juga membantu mengedit beberapa bagian view, JavaScript, CSS, dan automated test untuk alur AJAX Experience. Saya tetap menentukan bagian Experience yang dikembangkan, fitur ekstra star, pembagian akses tiap role, dan bentuk akhir interaksinya.

Pada Tutorial 07, bantuan juga mencakup membaca materi serta kode aktual, menyusun roadmap/playbook pribadi, dan mengedit serializer, permission, view/URL API, integrasi Projects, test, serta dokumentasi per checkpoint yang saya minta. Codex membantu menjalankan verifikasi dan browser pada database sementara. Commit tetap saya jalankan sendiri; push, merge, dan deployment tidak dianggap otomatis selesai oleh bantuan tersebut.

Pada awal Tugas 6, bantuan edit per checkpoint berlanjut ke serializer Experience,
permission empat role, API daftar/create, test, dan dokumentasi terkait. Rincian
hasil dan batas verifikasinya dicatat pada prompt log mulai entri 34.

Saat memberi prompt, saya biasanya menyertakan rubrik, source code terbaru, error yang muncul, atau hasil command Git. Saya meminta pekerjaan dibagi per module, setiap konsep baru dijelaskan, dan perubahan diperiksa sebelum commit. Cara ini membantu saya mengikuti alasan di balik `fetch()`, `await`, debounce, `AbortController`, `FormData`, CSRF, serta penggunaan `textContent`, bukan hanya melihat hasil akhirnya.

Untuk Tutorial 07, saya juga meminta penyesuaian field contoh dengan `technologies`, URL live/source, dan thumbnail static milik saya. Keputusan privacy serta akses Editor dibahas sebelum implementasi permission. Prompt log berikutnya memakai label **Prompt (ringkasan)**, jadi pertanyaannya merupakan ringkasan topik percakapan dan bukan transkrip literal.

Saya tidak langsung menganggap output AI pasti benar karena AI tetap bisa salah menempatkan kode atau melewatkan behavior lama. Contohnya, saat menambahkan test star Experience, class test sempat tersisip sebelum seluruh test JSON selesai. Masalah tersebut ditemukan saat review struktur file dan diperbaiki sebelum test dijalankan. Saya juga memastikan response star hanya berisi state dan jumlah, sanitizer tidak menggantikan output escaping, elemen modal dicek sebelum event listener dipasang, serta request pencarian lama dibatalkan agar hasilnya tidak tertukar.

Keterbatasan itu muncul lagi saat bantuan menambahkan test star Project: posisi class sempat memotong test detail, lalu diperbaiki setelah struktur file diperiksa. Pemeriksaan browser juga menemukan tombol Clear masih terlihat karena CSS menimpa atribut hidden; audit berikutnya menemukan loading baru memakai `aria-busy` tanpa pesan visual. Temuan ini diperbaiki melalui review dan pengujian terarah. Bantuan AI untuk koreksi tersebut dicatat di prompt log agar asal perubahan dan proses pemeriksaannya jelas.

Karena itu, workflow saya tetap mencakup review diff, pemeriksaan alur browser dengan bantuan AI, serta `python manage.py check`, `python manage.py makemigrations --check --dry-run`, `python manage.py test main`, `node --check`, dan `git diff --check`. Pada akhir Tugas 5, 73 test lulus; pada checkpoint lokal Tutorial 07 jumlahnya menjadi 140. Hasil ini belum membuktikan deployment atau pengumpulan sudah selesai. Menurut saya AI paling membantu untuk memberi arah dan mempercepat pemeriksaan, tetapi keputusan desain, kesesuaian rubrik, dan verifikasi akhir tetap perlu saya pertanggungjawabkan.

Contoh prompt dan cara saya memakai hasilnya dapat dilihat pada
[AI Prompt Log](docs/ai-prompt-log.md).
