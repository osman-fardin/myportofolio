# AI Prompt Log

Dokumen ini berisi beberapa contoh prompt yang mewakili penggunaan OpenAI Codex
selama pengerjaan Tutorial, Tugas 1 sampai Tugas 5, serta awal Tutorial 07. Prompt di
bawah diringkas dari percakapan asli agar lebih mudah dibaca. Informasi sensitif
dan percakapan yang tidak berkaitan dengan tugas tidak disertakan.

## 1. Memahami Tugas 2

**Prompt:**

> Tolong baca Tutorial sama Tugas 2 dulu ya. Experience kan udah aku buat di
> tutorial sebelumnya, jadi untuk tugas ini enaknya bagian apa yang dibikin
> dynamic? Jelasin juga kenapa biar aku ngerti sebelum mulai.

**Hasil penggunaan:**

AI membantu membandingkan beberapa pilihan dan menjelaskan bahwa Projects dapat
menjadi bagian database-backed yang berbeda dari Experience. Saya memilih
Projects karena sudah memiliki project nyata, yaitu Fasilkom Study Hub.

## 2. Merencanakan model Project

**Prompt:**

> Oke kita pakai Projects. Sekarang modelnya perlu field apa aja ya kalau minimal
> harus ada tiga selain primary key? Jangan langsung bikinin semuanya, jelasin
> dulu tiap field itu buat apa dan kenapa kita perlu pakai itu.

**Hasil penggunaan:**

AI menjelaskan penggunaan `CharField`, `TextField`, `URLField`, UUID, dan ordering.
Saya kemudian memakai field yang sesuai dengan data project saya, seperti title,
role, description, technologies, URL, thumbnail path, dan display order.

## 3. Memahami alur MVT

**Prompt:**

> Aku masih agak bingung MVT-nya. Bisa jelasin pelan-pelan pas aku buka
> `/projects/` itu request-nya pergi ke mana dulu, terus URL, view, model,
> context, sama template tuh nyambungnya gimana? Kalau ada yang baru tolong
> jelasin juga itu apa dan gunanya buat apa.

**Hasil penggunaan:**

Penjelasan ini saya gunakan untuk memahami hubungan antara `main/urls.py`,
`show_projects`, QuerySet `project_list`, dan loop di `projects.html`. Saya juga
memeriksa kembali nama function dan context berdasarkan kode yang benar-benar
ada di proyek.

## 4. Membuat test

**Prompt:**

> Untuk Projects ini test apa aja yang perlu aku buat biar aman dan sesuai
> rubrik? Aku kepikiran cek page-nya kebuka, template-nya bener, data dari model
> muncul, sama empty state. Kalau ada test lain yang penting kasih tau dan
> jelasin kenapa.

**Hasil penggunaan:**

AI membantu menyusun cakupan test dan beberapa bagian implementasinya. Setelah
itu saya menjalankan seluruh test, membaca hasilnya, dan memastikan 11 test
lulus tanpa bergantung pada database development saya.

## 5. Mengembangkan desain portfolio

**Prompt:**

> Aku ngerasa website sekarang terlalu ngikutin template awal. Aku pengen pas
> masuk cuma ada homepage yang singkat, terus ada pilihan buat lihat Projects
> atau About. Warna warm-brown yang sekarang jangan diganti, dan coba kasih
> beberapa preview di tempat terpisah dulu sebelum kita ubah yang asli.

**Hasil penggunaan:**

AI membuat beberapa alternatif visual pada tempat terpisah. Saya tidak langsung
memakai semuanya. Saya memilih homepage yang lebih ringkas, fullscreen menu,
project browser, dan kemudian menambahkan panel navy dengan cloudscape tipis
pada About.

## 6. Menolak solusi yang kurang akurat

**Prompt:**

> Highlight route rail-nya kenapa masih nyala walaupun aku scroll manual ke
> section lain? Ini bisa dibenerin cuma pakai CSS atau emang perlu JavaScript?
> Kalau aku belum mau pakai JavaScript, best practice-nya gimana?

**Hasil penggunaan:**

AI menjelaskan keterbatasan `:target` dan `:has()` untuk mengikuti posisi scroll.
Setelah mencoba hasilnya, saya memilih menghapus active state tersebut daripada
menampilkan posisi yang salah. Pada redesign berikutnya, route rail juga saya
hapus karena tidak lagi cocok dengan struktur multi-page.

## 7. Memeriksa Git dan deployment

**Prompt:**

> Coba cek posisi Git aku sekarang, branch-nya udah bener belum dan file apa aja
> yang bakal masuk commit. Jangan sampai README yang belum selesai, `.env`, atau
> database lokal ikut kepush. Sebelum jalanin command baru jelasin juga itu buat
> apa ya.

**Hasil penggunaan:**

AI membantu memeriksa status, diff, staging, dan branch. Saya tetap melakukan
merge melalui pull request GitHub dan memastikan file sensitif tidak masuk ke
commit. Ketika versi Django yang diwajibkan berubah, saya mengikuti pengumuman
mata kuliah dan memperbarui requirement ke Django 5.2.

## 8. Merencanakan Tugas 3

**Prompt:**

> Tolong baca Tugas 3 dulu ya. Untuk bagian yang dikembangkan aku mau pakai
> Experience. Bisa bantu pecah pengerjaannya menjadi beberapa module dan commit
> supaya progres Git-nya rapi? Jelasin juga target tiap module sebelum mulai.

**Hasil penggunaan:**

AI membantu merangkum kebutuhan tugas dan membaginya menjadi form, create,
update, delete, JSON, filter, testing, dan dokumentasi. Pembagian tersebut saya
pakai sebagai panduan supaya setiap commit mewakili progres yang jelas.

## 9. Memahami ModelForm dan CSRF

**Prompt:**

> Aku masih bingung kenapa harus pakai ModelForm dan bukan form HTML biasa.
> Terus `csrf_token` itu sebenarnya ngapain? Tolong jelasin pakai contoh dari
> Experience yang lagi aku kerjain dan jangan langsung kasih semua kodenya.

**Hasil penggunaan:**

AI menjelaskan hubungan antara model, field form, validasi, dan penggunaan
`instance` saat update. Penjelasan tersebut juga membantu saya memahami bahwa
`ModelForm` mengatur data form, sedangkan CSRF token melindungi request POST.

## 10. Memahami alur JSON Experience

**Prompt:**

> Bisa jelasin pelan-pelan alur Experience dari QuerySet sampai jadi JSON, terus
> kenapa di halaman perlu di-deserialize lagi? Aku juga mau filter title,
> category, dan status, jadi jelasin enaknya logikanya ditaruh di mana.

**Hasil penggunaan:**

AI membantu menjelaskan hubungan antara QuerySet, serialization,
`HttpResponse`, deserialization, context, dan template. Saya kemudian memakai
satu helper filter bersama agar endpoint JSON dan halaman HTML menghasilkan data
yang konsisten.

## 11. Menentukan cakupan test

**Prompt:**

> Untuk fitur Experience ini test apa aja yang penting supaya create, update,
> delete, JSON, dan filternya benar-benar aman? Tolong bagi per bagian dan
> jelasin apa yang dibuktikan oleh masing-masing test.

**Hasil penggunaan:**

AI membantu menyusun cakupan test untuk form, validasi tanggal, create, update,
404, delete berbasis POST, JSON, filter, dan deserialization. Saya menjalankan
seluruh test tersebut bersama test lama hingga total 23 test berhasil lulus.

## 12. Memahami pertanyaan reflektif

**Prompt:**

> Tolong bantu jelasin maksud tiga pertanyaan refleksi Tugas 3 pakai contoh yang
> benar-benar ada di project aku. Bahasanya jangan terlalu formal dan jangan
> terlalu panjang karena nanti tetap mau aku sesuaikan sendiri.

**Hasil penggunaan:**

AI membantu menghubungkan pertanyaan refleksi dengan `ExperienceForm`, CSRF,
endpoint `/api/experiences/`, serta proses serialization dan deserialization.
Jawabannya kemudian saya ringkas dan sesuaikan lagi dengan gaya README saya.

## 13. Merencanakan Tugas 4

**Prompt:**

> Tolong baca Tugas 4 dulu ya. Aku mau Git history-nya tetap rapi seperti tugas
> sebelumnya, jadi bantu pecah pengerjaannya menjadi beberapa branch, module,
> dan commit. Jelasin juga fitur tambahan apa yang masih nyambung dengan materi
> authentication dan authorization.

**Hasil penggunaan:**

AI membantu merangkum kebutuhan role guest, user biasa, Editor, dan superuser,
lalu membagi pengerjaan menjadi authorization, API privacy, personal stars,
testing, dan dokumentasi. Saya memilih fitur **Starred by me** karena masih
berhubungan langsung dengan user dan relasi ManyToMany.

## 14. Memahami Group dan Permission

**Prompt:**

> Aku masih bingung role Editor ini bagusnya dibuat gimana. Kenapa tidak cukup
> cek username atau bikin role string sendiri? Jelasin cara kerja Group,
> `change_project`, `has_perm`, dan `perms` di template pelan-pelan ya.

**Hasil penggunaan:**

AI menjelaskan bahwa permission bawaan Django lebih aman daripada memeriksa
username atau menyimpan role manual. Saya kemudian memakai
`main.change_project` pada view dan `perms.main.change_project` pada template,
sedangkan create dan delete tetap dibatasi untuk superuser.

## 15. Menjaga privacy endpoint JSON

**Prompt:**

> Endpoint JSON Project sekarang masih bisa nampilin username orang yang kasih
> star. Ini aman atau harus dihapus? Tolong jelasin cara membatasi field yang
> keluar tanpa merusak filter title dan halaman Projects.

**Hasil penggunaan:**

AI membantu menjelaskan penggunaan allowlist pada serializer. Saya membatasi
response ke field Project yang memang publik dan memastikan `starred_by`,
username, serta email tidak ikut dikirim. Filter title tetap diperiksa melalui
automated test.

## 16. Membuat personal starred projects

**Prompt:**

> Aku mau user yang login bisa lihat project yang dia star sendiri. Bantu
> jelasin query ManyToMany-nya, cara gabungin dengan search title, empty state,
> dan test supaya koleksi user A tidak kecampur sama user B.

**Hasil penggunaan:**

AI membantu membagi fitur menjadi backend query, kontrol filter, empty state,
styling, dan test. Saya menerapkan query `starred_by=request.user`, mencoba
fiturnya, lalu menambahkan test untuk isolasi antar-user, guest, kombinasi
pencarian, dan koleksi kosong.

## 17. Memeriksa bug filter

**Prompt:**

> Aku kayaknya salah nulis bagian filter personal stars karena project biasa
> malah hilang. Tolong cek bagian yang salah, perbaiki hanya bagian itu, terus
> jelasin aku salahnya di mana.

**Hasil penggunaan:**

AI membantu menemukan bahwa posisi `else` saya sejajar dengan kondisi
`starred_filter`, bukan dengan pengecekan user login. Setelah diperbaiki, saya
menjalankan seluruh test untuk memastikan request biasa, personal filter, dan
guest kembali menghasilkan behavior yang benar.

## 18. Merencanakan Tugas 5

**Prompt:**

> Tolong baca Tugas 5 dulu ya. Seperti tugas sebelumnya, buatin roadmap dan
> pembagian module serta commit supaya Git history-nya rapi. Bagian yang mau aku
> kembangkan tetap Experience, dan pastikan semua requirement AJAX dari tutorial
> diterapkan di sana, bukan cuma di Projects.

**Hasil penggunaan:**

AI membantu memetakan requirement menjadi JSON manual, role authorization, AJAX
rendering, debounce, modal create, AJAX POST, XSS, star interaction, testing, dan
dokumentasi. Saya memakai satu feature branch dan commit terpisah untuk setiap
behavior supaya progresnya dapat diperiksa dengan jelas.

## 19. Memahami rendering dan pencarian AJAX

**Prompt:**

> Experience sekarang masih dirender dari template. Jelasin gimana caranya bikin
> halaman cuma jadi shell terus datanya diambil pakai fetch. Search title,
> category, sama status harus tetap jalan tanpa reload, terus debounce dan
> AbortController itu masing-masing gunanya apa?

**Hasil penggunaan:**

AI membantu menjelaskan perbedaan server-rendered list dan AJAX shell, alur
`fetch()`, serta alasan debounce tidak cukup untuk mencegah response lama datang
belakangan. Implementasi akhirnya memakai delay 400 ms dan `AbortController`,
serta tetap menampilkan loading, empty, error, retry, dan result count.

## 20. Menjaga keamanan modal create

**Prompt:**

> Untuk modal add Experience, bantu jelasin alur FormData, CSRF header, response
> 201/400/403, dan cara nampilin error dari ModelForm. Aku juga mau ngetes payload
> XSS yang pakai img onerror, tapi jangan sampai sanitizer bikin validasi tanggal
> yang lama rusak.

**Hasil penggunaan:**

AI membantu menyusun alur AJAX POST dan beberapa bagian implementasinya. Saya
memastikan permission tetap diperiksa di view, request membawa CSRF token, error
server masuk ke toast, serta `strip_tags` hanya dipakai pada field teks. Rendering
card tetap memakai `textContent` sebagai lapisan perlindungan output.

## 21. Menambahkan fitur ekstra star Experience

**Prompt:**

> Aku mau fitur ekstra yang masih nyambung sama Tugas 4. Bisa bikin star dan
> unstar Experience lewat AJAX tanpa reload? Response jangan bocorin user, tombol
> jangan bisa didouble-click pas request, dan test user A sama user B harus tetap
> kepisah.

**Hasil penggunaan:**

AI membantu menyesuaikan relasi star yang sudah ada menjadi endpoint AJAX khusus
Experience. Response dibatasi ke `is_starred` dan `star_count`, sedangkan tombol
memperbarui label, angka, dan `aria-pressed`. Interaksi star dan unstar diperiksa
melalui browser, lalu ditambahkan test isolasi antar-user, GET rejection, CSRF,
dan UUID 404.

## 22. Memulai Tutorial 07 dan serializer Project

**Prompt (ringkasan):**

> Baca handoff, Tutorial 07, dan Tugas 6 dulu, lalu audit repo dan baseline.
> Bikin roadmap pribadi dan arahkan satu langkah kecil setiap kali. Aku yang
> ngetik, dan setelah bilang done tolong cek kode aktualnya.

**Hasil penggunaan:**

Saya mengerjakan setup DRF, serializer Project, dan test awalnya secara bertahap.
AI membantu menjelaskan `ModelSerializer`, daftar field eksplisit, field read-only,
dan penggunaan context untuk membaca status star pengguna, serta memberi contoh
penerapan dan saran test yang sesuai dengan model saya.

Saat method penghitung star masih berada di dalam `Meta`, Django check tetap
lulus, tetapi pemeriksaan `.data` menemukan `AttributeError`. Setelah mendapat
penjelasan dari AI, saya memperbaiki indentasinya. Saya juga menambahkan test
untuk output publik, status star tiap pengguna, dan perlindungan ID serta relasi
star, dengan bantuan review dari AI. Dari sini saya memahami bahwa check
konfigurasi saja belum cukup untuk memastikan perilaku serializer benar.

## 23. Memahami validasi input API Project

**Prompt (ringkasan):**

> Lanjut ke checkpoint berikutnya. Bantu implementasikan validasi serializer
> beserta test, jelaskan perubahannya, dan biarkan aku yang commit.

**Hasil penggunaan:**

Saya mengembangkan validasi serializer Project dengan bantuan AI untuk
penjelasan, implementasi, dan pengujian. Aturannya mengikuti field Project saya:
tag HTML dibuang, teks wajib yang menjadi
kosong ditolak, dan thumbnail tetap berupa path static opsional. Saya mendapat
penjelasan bahwa serializer tidak menjalankan `ProjectForm.clean()`, sehingga
jalur API perlu validasinya sendiri. Test juga mencakup URL yang tidak valid,
batas field model, default field opsional, dan perbedaan update penuh dengan
parsial. Pembersihan input tetap perlu disertai escaping saat ditampilkan.

## 24. Membedakan permission API Projects dan form lama

**Prompt (ringkasan):**

> Aku masih bingung permission API ini bedanya apa sama pengecekan izin di view
> lama. Di tutorial yang boleh ubah Projects cuma superuser, tapi Editor di
> punyaku sudah bisa edit. Ini enaknya disesuaikan gimana supaya fitur lama tetap
> jalan? Jelasin juga SAFE_METHODS, kenapa is_staff saja belum cukup, dan test
> apa yang perlu buat memastikan tiap role dapat akses yang benar.

**Hasil penggunaan:**

Saya menyiapkan permission API Projects dengan bantuan AI untuk penjelasan,
implementasi, dan pengujian. Saya memahami perbedaan aturan tutorial dengan
proyek saya: API Projects hanya boleh diubah superuser, sementara Editor tetap
bisa mengedit lewat form HTML lama menggunakan `main.change_project`. Karena itu,
permission lama tidak diganti. Aturan Experience akan tetap mengikuti empat role
Tugas 6, termasuk hak Editor untuk PUT/PATCH.

Test class permission mencakup method baca untuk semua role dan method tulis
untuk superuser, serta penolakan bagi guest, user biasa, staff, dan Editor yang
benar-benar mempunyai permission edit Project. Pada checkpoint ini kelasnya
belum dipasang ke endpoint; status HTTP dan perubahan database akan diperiksa
lagi saat API view dibuat.

## 25. Menghubungkan serializer dan permission ke API daftar Project

**Prompt (ringkasan):**

> Serializer sama permission sudah ada, terus gimana cara menghubungkannya jadi
> endpoint daftar dan tambah Project? Jelasin alur request.data, query parameter,
> dan Response. Search judul sama filter Starred by me yang lama harus tetap bisa
> dipakai. Gimana juga cara memastikan session login tetap terlindungi CSRF?

**Hasil penggunaan:**

Saya melanjutkan endpoint daftar dan tambah Project dengan bantuan AI untuk
penjelasan, implementasi, dan pengujian. API baru memakai URL `/api/v1/projects/`
dan namespace `api`, sementara route lama tetap tersedia. GET menghasilkan daftar
objek datar, dan POST yang valid menghasilkan 201 setelah melewati permission
serta validasi serializer. Urutan `display_order`, pencarian judul, dan filter
personal tetap mengikuti kebutuhan portofolio saya.

Saya memahami bahwa test permission dengan `force_authenticate` berbeda dari
test session dan CSRF. Karena itu ada test dengan login sungguhan memakai akun
database uji dan `APIClient(enforce_csrf_checks=True)`, dengan dan tanpa token.
Test penolakan juga memeriksa database. Integrasi JavaScript halaman belum
dipindahkan ke API baru pada checkpoint ini.

## 26. Memahami API detail, PUT, PATCH, dan DELETE

**Prompt (ringkasan):**

> Kalau API daftar dan tambah sudah ada, gimana cara membuat detail, update,
> dan delete untuk UUID Project yang sama? Aku masih bingung bedanya PUT sama
> PATCH dan kenapa setelah DELETE tidak boleh langsung membaca JSON. Jelasin
> juga cara memastikan Editor tetap ditolak di API dan data tidak berubah saat
> validasi atau CSRF gagal.

**Hasil penggunaan:**

Saya melanjutkan API detail Project dengan bantuan AI untuk penjelasan,
implementasi, dan pengujian. GET menghasilkan satu objek, PUT membutuhkan semua
field wajib, sedangkan PATCH memakai `partial=True` supaya field yang tidak
dikirim tetap dipertahankan. DELETE menghasilkan 204 dengan body kosong.

Test memeriksa database setelah update, delete, dan penolakan akses, termasuk
star yang harus tetap ada saat update serta Project lain yang tidak boleh ikut
berubah. Ada pemeriksaan UUID yang tidak ditemukan, field read-only, dan CSRF
melalui login session untuk PUT, PATCH, dan DELETE. Form Editor lama tetap
tersedia; halaman Projects belum dihubungkan ke endpoint baru pada checkpoint ini.

## 27. Memahami toggle star lewat API

**Prompt (ringkasan):**

> Kalau CRUD Project sudah ada, gimana mengubah star lama menjadi endpoint API?
> User biasa harus tetap bisa star walaupun tidak boleh mengedit Project. Gimana
> memastikan akun pemberi star selalu dari user yang login, bukan ID di payload,
> dan star user A tidak mengubah punya user B? Jelasin juga test CSRF yang perlu.

**Hasil penggunaan:**

Saya melanjutkan API star dengan bantuan AI untuk penjelasan, implementasi,
dan pengujian. Endpoint POST memakai `IsAuthenticated`, bukan permission
owner-only CRUD. Akun pemberi star berasal dari `request.user`, dan response
menggunakan serializer publik yang sama tanpa daftar akun pemberi star.

Test mencakup toggle untuk seluruh role yang login, isolasi antar-user, payload
yang mencoba memilih akun lain, method yang ditolak, UUID yang tidak ditemukan,
serta login session dengan token CSRF yang tidak ada, salah, dan valid. Hasil
star juga diperiksa melalui list, detail, dan filter personal. Toggle tidak boleh
di-retry otomatis karena POST kedua justru membatalkan hasil pertama; tombol UI
nanti dinonaktifkan selama request. Integrasi halaman masih menjadi tahap berikutnya.

Pemeriksaan awal menemukan class test star tersisip di tengah class detail saat
dibantu penambahan kode. Susunannya dibetulkan dengan memastikan seluruh test
detail lama tetap utuh, lalu kedua kelompok test dijalankan ulang. Ini menjadi
contoh kenapa bantuan implementasi tetap perlu diperiksa melalui test dan diff.

## 28. Memindahkan pembacaan halaman Projects ke DRF

**Prompt (ringkasan):**

> API Project sudah lengkap, terus gimana cara menghubungkannya ke halaman yang
> sekarang? JSON baru sudah tidak punya pk dan fields, tapi desain list, panel
> detail, preview, dan tombol lamaku harus tetap jalan. Jelasin cara mengambil
> detail tanpa reload, menjaga Back/Forward dan filter, serta menampilkan teks
> dari API dengan aman.

**Hasil penggunaan:**

Saya menghubungkan list dan detail Projects ke DRF dengan bantuan AI untuk
penjelasan, implementasi, dan pengujian. JavaScript membaca field datar dari
`/api/v1/projects/` dan endpoint detailnya. Tampilan awal dari server tetap
tersedia sebagai fallback, tetapi tidak lagi bergantung pada deserialize JSON
manual. Komponen detail yang sama dipakai sebagai template DOM, sehingga desain
dan kontrol berdasarkan permission tetap konsisten saat memilih Project lain.

Saya memahami peran `textContent`, template DOM yang belum aktif, named URL dari
template Django, serta `pushState` dan `popstate` untuk navigasi. Request list
dan detail mempunyai AbortController terpisah agar hasil lama tidak menimpa
pilihan terbaru. Container AJAX tetap tersedia ketika database kosong, dan
cookie CSRF tetap dibuat bagi user biasa meskipun modal create tidak ditampilkan.

Test Django memeriksa fallback, filter, permission, CSRF cookie, dan escaping.
Pemeriksaan browser memakai database uji terpisah dan mencakup preview statis,
Back/Forward, filter personal, setiap role, simulasi request lambat/error, serta
layout 390/768/1440 px. Browser menemukan Clear masih terlihat karena style
inline-flex menimpa atribut hidden; rule khusus ditambahkan untuk memperbaikinya.
Ini memperlihatkan bahwa test backend saja belum cukup untuk memeriksa UI.

Pada checkpoint ini create, star, dan delete dari halaman masih memakai route
lama. Migrasi ketiga mutation tersebut ke DRF menjadi checkpoint berikutnya.
Verifikasi checkpoint menghasilkan 127 test `main` lulus; fallback tanpa
JavaScript juga diperiksa melalui browser. Data lokal dan PWS tidak diubah.

## 29. Mengirim modal create Project ke DRF

**Prompt (ringkasan):**

> List dan detail sudah memakai DRF, terus modal add Project perlu diubah di
> bagian mana? Jelasin bedanya mengirim FormData dengan JSON dan cara memilih
> field yang dikirim. Error serializer sekarang bentuknya berbeda; gimana cara
> menampilkan validasi 400 dan penolakan 403 tanpa menghilangkan input modal?
> Aku juga mau submit tidak terkirim dua kali dan filter aktif tetap dipakai.

**Hasil penggunaan:**

Saya memindahkan create Project ke DRF dengan bantuan AI untuk penjelasan,
implementasi, dan pengujian. Form lama tetap mempunyai action HTML sebagai
fallback, sementara JavaScript membaca named URL API dari atribut data.
`FormData` masih dipakai untuk membaca input, tetapi payload yang dikirim adalah
JSON berisi sembilan field Project yang dapat diisi, tanpa token form atau
field hasil perhitungan. Token CSRF dikirim melalui header.

Saya memahami bahwa error DRF berupa daftar pesan per field atau pesan `detail`,
bukan struktur error ModelForm lama. Saat validasi atau izin ditolak, modal dan
input dipertahankan. Saat create berhasil, form di-reset, modal ditutup, toast
ditampilkan, dan daftar diambil ulang menggunakan filter aktif. Tombol submit
dinonaktifkan selama request dan handler menolak submit tambahan yang masih
berlangsung.

Test mencakup target API dari modal, fallback HTML, input tidak valid, dan session
yang berakhir. Browser dengan database uji terpisah juga memeriksa header JSON
dan CSRF, create pertama saat daftar kosong, pencegahan submit ganda, filter
aktif, error HTML, serta gangguan jaringan. Verifikasi checkpoint menghasilkan
130 test `main` lulus. Star dan delete dari halaman masih memakai route lama;
data lokal dan PWS tidak diubah.

## Verifikasi manual

Saya tidak menjadikan output AI sebagai hasil final tanpa pemeriksaan. Beberapa
langkah yang saya gunakan untuk melakukan verifikasi adalah:

```bash
python manage.py check
python manage.py test
git diff --check
git status
git diff
```

Saya juga mencoba navigasi, filter AJAX, loading dan empty state, modal create,
toast, confirmation delete, star dan unstar, serta layout desktop dan mobile
melalui browser. Pada akhir Tugas 5, seluruh 73 automated test dipastikan lulus
sebelum dokumentasi diselesaikan.
