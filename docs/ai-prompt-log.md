# AI Prompt Log

Dokumen ini berisi beberapa contoh prompt yang mewakili penggunaan OpenAI Codex
selama pengerjaan Tutorial, Tugas 1 sampai Tugas 5, Tutorial 07, dan Tugas 6. Prompt di
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

## 30. Menghubungkan tombol star Project ke DRF

**Prompt (ringkasan):**

> Create sudah lewat DRF, sekarang tombol star dan unstar disambungkan gimana
> supaya tidak reload? Tombol detailnya dibuat ulang oleh JavaScript; jelasin
> event delegation, token CSRF, dan cara mencegah klik ganda. Kalau aku unstar
> saat filter starred aktif atau pindah project sebelum respons selesai,
> gimana supaya daftar dan detail tetap sesuai?

**Hasil penggunaan:**

Saya mengintegrasikan star Project dengan bantuan AI untuk penjelasan,
implementasi, dan pengujian. Form menyimpan named URL API di `data-api-url`,
sedangkan action HTML lama tetap tersedia sebagai fallback. Handler submit
dipasang pada container detail melalui event delegation, sehingga tetap
berfungsi untuk form hasil clone. Placeholder UUID pada URL API juga diganti
dengan ID project yang dipilih.

Saya memakai POST dengan header CSRF dan mengambil label, jumlah star, serta
`aria-pressed` dari respons DRF. Request yang sedang berjalan dicatat per ID
project agar submit ganda tetap ditolak walaupun detail dibuat ulang. Tidak ada
retry otomatis pada toggle. Sesudah berhasil, daftar dimuat ulang dengan filter
aktif; project yang di-unstar hilang dari daftar personal, tetapi detailnya
tetap bisa dipakai untuk star kembali.

Respons star tidak mengganti detail project lain yang baru dipilih. Jika masih
di project yang sama, pembacaan detail lama dibatalkan agar status sebelum
mutation tidak menimpa hasil terbaru. Penolakan API dan gangguan jaringan
menampilkan toast, mempertahankan status yang terlihat, dan membuka kembali
tombol. Status server setelah gangguan jaringan perlu diperiksa lagi karena
respons yang gagal diterima belum memastikan mutation gagal tersimpan.

Empat test halaman baru memeriksa URL API dan template, tiga role login,
fallback HTML, guest, serta penolakan CSRF dan sesi berakhir beserta kondisi
database. Pemeriksaan browser memakai database sementara dan mencakup toggle
tanpa reload, klik ganda, filter personal, pindah detail, respons detail lama,
error JSON/HTML, gangguan jaringan, serta penolakan CSRF dan sesi sebenarnya.
Seluruh 134 test `main` lulus; check, pemeriksaan migrasi, sintaks JavaScript,
dan whitespace juga lolos. Data lokal tetap satu Project dan dua Experience.
Delete UI masih memakai route lama; PWS tidak diubah dan commit dijalankan
sendiri oleh saya.

## 31. Menghapus Project melalui DRF tanpa reload

**Prompt (ringkasan):**

> Tombol star sudah lewat DRF, sekarang confirmation delete perlu disambungkan
> ke endpoint mana? Jelasin cara mengirim DELETE dengan CSRF dan kenapa respons
> 204 tidak boleh dibaca sebagai JSON. Kalau request gagal, diklik dua kali,
> atau aku sudah pindah detail, gimana supaya modal dan daftar tetap sesuai?

**Hasil penggunaan:**

Saya memindahkan delete Project ke DRF dengan bantuan AI untuk penjelasan,
implementasi, dan pengujian. Form konfirmasi mempunyai `data-api-url` menuju
detail API, sementara action POST lama tetap tersedia sebagai fallback HTML.
Handler submit memakai event delegation seperti star dan mengirim DELETE
dengan token CSRF. Dialog konfirmasi serta tampilan lama dipertahankan.

Saya memahami bahwa keberhasilan delete ditandai status 204 tanpa body,
sehingga JSON hanya dibaca pada respons error. Setelah berhasil, konfirmasi
ditutup, pilihan detail dibersihkan bila masih menunjuk project yang dihapus,
dan daftar dimuat ulang memakai filter aktif. URL kembali ke halaman daftar
untuk pilihan yang dihapus. Jika sudah memilih project lain, detail dan URL
pilihan baru dipertahankan. Penghapusan record terakhir menampilkan empty state
dan tombol Add project tetap tersedia.

Request delete dicatat per ID agar submit ganda ditolak, termasuk ketika form
detail dibuat ulang. Star dan delete untuk project yang sama saling mengunci
selama request masih berjalan agar responsnya tidak saling menimpa. Kontrol
project lain tetap bisa digunakan. Pada error, toast ditampilkan, detail dan
daftar dipertahankan, serta tombol dibuka kembali; modal yang masih terbuka
tidak ditutup otomatis. Tidak ada retry mutation otomatis.

Lima test halaman baru mencakup URL konfirmasi dan template, delete 204 dengan
body kosong, record lain yang harus tetap ada, fallback HTML, CSRF dan sesi
berakhir, target yang sudah dihapus, serta kontrol khusus superuser. Pemeriksaan
browser memakai database sementara: Cancel sebelum submit tidak mengirim
DELETE, submit ganda hanya mengirim satu DELETE, star/delete saling terkunci,
filter tetap aktif, dan respons lambat tidak membersihkan detail project lain.
Error JSON 403/404, HTML 503, gangguan jaringan, CSRF, serta sesi berakhir juga
diperiksa. Browser memastikan tidak ada pemanggilan JSON pada 204; body kosong
diverifikasi lewat test Django.

Seluruh 139 test `main` lulus. Check, pemeriksaan migrasi, sintaks JavaScript,
dan whitespace juga lolos. Data lokal tetap satu Project dan dua Experience;
PWS tidak diubah. Commit tetap dijalankan sendiri oleh saya. Finalisasi
dokumentasi dan pemeriksaan checklist Tutorial 07 menjadi checkpoint berikutnya.

## 32. Menutup celah loading pada audit Tutorial 07

**Prompt (ringkasan):**

> Setelah delete selesai, bantu cocokkan hasilnya dengan checklist Tutorial 07.
> Loading daftar dan detail sudah cukup jelas belum kalau koneksi lambat?
> Kalau keduanya berjalan bersamaan atau request pencarian lama dibatalkan,
> gimana supaya indikatornya tidak hilang sebelum request terbaru selesai?

**Hasil penggunaan:**

Saya meninjau ulang materi dan implementasi dengan bantuan AI. Audit menemukan
bahwa daftar dan detail sudah memakai `aria-busy`, tetapi belum mempunyai pesan
loading yang terlihat. Saya menutup celah ini sebagai checkpoint terpisah dengan
bantuan AI untuk penjelasan, implementasi, dan pengujian sebelum finalisasi README.

Pesan loading memakai `role="status"` dan `aria-atomic="true"`, ditempatkan di
luar container yang sedang busy agar statusnya terpisah dari hasil yang dimuat.
Helper `setProjectBusy` menyelaraskan `aria-busy`, teks, dan visibilitas pesan
berdasarkan request daftar serta detail. Pesan tidak disembunyikan hanya karena
salah satunya sudah selesai. Pengecekan controller yang sudah ada tetap menjaga
agar request lama yang dibatalkan tidak mengubah status request terbaru.

Saya mempertahankan isi sebelumnya selama pemuatan dan memakai warna cloud-soft
dari tema Projects. Tanpa JavaScript, indikator tetap tersembunyi dan fallback
HTML masih menampilkan data. Error dan empty state lama tetap dipakai; checkpoint
ini tidak menambahkan model atau mengubah kontrak API.

Test halaman memeriksa status yang tersedia tetapi tersembunyi pada fallback
daftar dan detail. Browser dengan database sementara memeriksa loading daftar,
detail, dan keduanya sekaligus; request lama yang dibatalkan; error 503/404 dan
pemulihan; serta fallback tanpa JavaScript. Tampilan 390 dan 1440 px diperiksa
melalui screenshot tanpa horizontal overflow. Seluruh 140 test `main` lulus,
check dan pemeriksaan migrasi bersih, dependency tidak bentrok, serta sintaks
JavaScript dan whitespace lolos. Data lokal dan PWS tidak diubah.

Audit ini belum berarti seluruh proses pengumpulan selesai. Finalisasi README,
pencatatan hash akhir, push/PR, pemeriksaan deployment, dan submit masih perlu
dituntaskan. Commit, push, merge, serta deployment tetap saya jalankan sendiri.

## 33. Menyiapkan dokumentasi checkpoint Tutorial 07

**Prompt (ringkasan):**

> Loading sudah selesai, sekarang README perlu mencatat apa saja untuk Tutorial
> 07? Bantu cocokkan API dan test dengan implementasi, jelasin lagi perbedaan
> Editor pada API Projects dengan form lama, dan pisahkan progres lokal dari
> push, deploy, serta pengumpulan. Roadmap pribadi juga perlu diperbarui supaya
> saat lanjut Experience tidak menganggap semua modul sudah selesai.

**Hasil penggunaan:**

Saya memperbarui dokumentasi dengan bantuan AI untuk penjelasan, penyusunan,
review, dan verifikasi. README root mencatat dependency DRF, route/method,
matriks role, field contoh yang disesuaikan, payload, filter, status HTTP,
session/CSRF, struktur kode, fallback, hasil test/browser, dan progres Tutorial
07. Refleksi historis tetap disimpan; implementasi serta refleksi Tugas 6 belum
diklaim selesai. AI disclosure mencatat bantuan edit per checkpoint dan temuan
yang benar-benar terjadi selama review.

Saya memahami bahwa Editor Projects masih bisa memakai form HTML dengan
`main.change_project`, tetapi API Projects owner-only. Aturan ini tidak dibawa
ke rencana API Experience: Editor di sana tetap perlu PUT/PATCH sesuai Tugas 6.
Playbook dan roadmap pribadi di folder materi diperbarui dengan commit aktual,
matriks bukti T01-T12, serta Tugas 6 yang masih rencana. Keduanya tetap di luar
repo dan tidak menggantikan README proyek.

Contoh JSON README lolos validasi ProjectSerializer tanpa disimpan. Tautan
Markdown lokal dan jumlah method test diperiksa: 73 test lama, 48 API, dan 19
halaman, total 140 sesuai full suite yang lulus pada checkpoint `0653a49`.
Checkpoint ini tidak mengubah kode aplikasi dan tidak mengulang seluruh suite;
check, pemeriksaan migrasi, pip check, sintaks ketiga script, serta whitespace
diperiksa lagi untuk memastikan dokumentasinya sesuai environment proyek.

Eksperimen permission sementara di memori test juga membuktikan bahwa test
penolakan menangkap regresi: user biasa, Editor, dan staff sempat mendapat 201
ketika kebijakan sengaja dilonggarkan, sehingga assertion 403 gagal sesuai
harapan. Setelah patch memori dilepas, test yang sama lulus. Source permission
dan data lokal tidak diubah. Data tetap satu Project dan dua Experience.

Commit implementasi terakhir yang diperiksa adalah `0653a49`; commit dokumentasi
dan hash akhir pengumpulan baru dicatat setelah saya membuat dan memeriksanya.
Push, PR/merge, deployment/PWS, akses commit publik, dan submit SCELE masih perlu
bukti. Instalasi ulang dari environment kosong juga belum diverifikasi. Tutorial
07 harus dikumpulkan terpisah sebelum melanjutkan pengumpulan Tugas 6.

## 34. Memulai serializer Experience untuk Tugas 6 (7 November 2026)

**Prompt (ringkasan):**

> Untuk Tugas 6, aku mau lanjut dengan pola bantuan edit langsung seperti saat
> Tutorial 07, tetap satu checkpoint lalu aku yang commit. Bantu jelasin dan
> terapkan serializer Experience memakai model lama. Field star harus read-only,
> teks dibersihkan, dan tanggal tetap valid saat PATCH hanya mengirim salah satu
> tanggal. Sertakan test yang sesuai sebelum lanjut ke permission dan endpoint.

**Hasil penggunaan:**

Saya meminta bantuan edit langsung per checkpoint dan tetap menjalankan commit
sendiri. AI membantu memeriksa branch `feat/tugas-6-experience-api` dari merge
Tutorial 07 `dd3220e`, lalu menjalankan ulang baseline. Seluruh 140 test lama,
Django check, pemeriksaan migrasi, dan pip check lolos sebelum perubahan.

Saya menambahkan ExperienceSerializer dengan bantuan AI untuk penjelasan,
implementasi, dan pengujian. Dua belas field ditulis eksplisit, mencakup data
model, description mentah untuk kebutuhan edit, description_points,
category_label, is_ongoing, serta jumlah dan status star. UUID dan field turunan
read-only; akun pemberi star tidak ditampilkan. Status star mengikuti request
pengguna dan bernilai false jika tidak ada request atau pengguna anonim.

Validasi title dan description memakai helper pembersihan teks yang sudah ada.
Tag HTML dibuang, spasi tepi dirapikan, dan teks kosong setelah dibersihkan
ditolak. Validasi URL, choices, panjang teks, serta format tanggal mengikuti
field model. Saat PATCH, tanggal input dibandingkan dengan tanggal yang tetap
tersimpan pada instance. `ended_at: null` mengembalikan status ongoing; waktu
akhir yang sama dengan waktu mulai tetap diizinkan seperti aturan form lama.

Saya memahami bahwa start date mempunyai default dari model. Saat create
tidak mengirim start, serializer mengambil default sekali agar tanggal yang
divalidasi sama dengan yang disimpan. Saat update, tanggal yang tidak dikirim
tetap memakai instance. Pengujian juga mencakup perbandingan offset zona waktu.

Test Experience ditempatkan pada `main/tests_experience_api.py` agar mudah
ditinjau bersama fitur berikutnya. Seluruh 19 test baru dan total 159 test main
lulus. Check, pemeriksaan migrasi, serta whitespace bersih. Data lokal tetap
satu Project dan dua Experience; tidak ada perubahan schema, UI, atau PWS.
Warning staticfiles lama tetap nonfatal. Permission empat role dan endpoint
Experience menjadi checkpoint berikutnya; serializer ini belum dihubungkan ke
request halaman. Header log diperbarui untuk mencakup Tugas 6.

## 35. Menjaga empat role pada permission Experience

**Prompt (ringkasan):**

> Serializer sudah di-commit, lanjut permission Experience. Jelasin bagaimana
> guest dan user biasa tetap boleh membaca, Editor bisa PUT/PATCH, sedangkan
> create/delete khusus superuser. Aku memakai Django permission sejak tugas
> sebelumnya; pastikan nama grup atau status staff saja tidak memberi hak edit
> dan aturan Projects dari tutorial tetap sesuai checkpoint sebelumnya.

**Hasil penggunaan:**

Saya melanjutkan dengan bantuan AI untuk penjelasan, implementasi, dan pengujian
per checkpoint. Commit serializer `45925e9` diperiksa sebelum menambahkan
IsPortfolioOwnerOrEditorOrReadOnly pada `main/permissions.py`. SAFE_METHODS
diizinkan untuk semua pengunjung, pengguna anonim ditolak untuk mutation,
superuser diizinkan menulis, dan akun lainnya hanya boleh PUT/PATCH jika
memiliki `main.change_experience`.

Saya memahami bahwa Editor adalah peran yang ditentukan permission yang sudah
dipakai proyek. Nama grup Editor saja tidak cukup. Permission bisa diberikan
melalui grup atau langsung pada user; keduanya memberi izin update yang sama.
Status staff tidak memberikan hak create/delete Experience, dan permission
`main.change_project` saja tidak memberi hak update Experience. Class permission
Projects tetap memakai aturan owner-only yang sudah dibuat pada Tutorial 07.

Delapan test baru pada `main/tests_experience_api.py` memeriksa matriks method
semua role, grup tanpa permission, permission langsung dengan/tanpa staff,
permission Project yang berbeda, serta pembatasan mutation selain PUT/PATCH.
Test ini memeriksa keputusan class lewat APIRequestFactory; endpoint belum
dipasang. Test status HTTP, kondisi database setelah penolakan, dan CSRF lewat
session akan ditambahkan bersama endpoint. Star nantinya tetap memakai
IsAuthenticated, sehingga user biasa tetap bisa star tanpa permission Editor.

Sebanyak 12 test permission terarah lulus, termasuk 4 test Projects lama. Seluruh
167 test main juga lulus; check, pemeriksaan migrasi, dan whitespace bersih.
Data lokal tetap satu Project dan dua Experience. Tidak ada perubahan grup pada
database lokal, model, UI, atau PWS. Saya menjalankan commit sendiri sebelum
melanjutkan checkpoint endpoint daftar dan create.

## 36. Membuat API daftar dan create Experience

**Prompt (ringkasan):**

> Permission sudah di-commit, lanjut endpoint daftar dan create Experience.
> Bantu pindahkan filter title, category, dan status dari JSON lama ke query
> parameter DRF, dengan POST khusus superuser. Jelasin request.data dan
> request.query_params, serta pastikan test 403/400 memeriksa database. Uji juga
> session dan CSRF yang benar-benar lewat login.

**Hasil penggunaan:**

Saya melanjutkan dengan bantuan AI untuk penjelasan, implementasi, pengujian,
dan dokumentasi. Commit permission `afbf0f0` diperiksa sebelum experience_list
ditambahkan di `main/api_views.py` dan route `api:experience-list` didaftarkan
sebagai `/api/v1/experiences/`. View berbasis fungsi memakai @api_view untuk
GET/HEAD/POST, SessionAuthentication, permission empat role, serta Response DRF.

Saya memahami bahwa request.query_params dipakai untuk filter, sementara
request.data berisi input create yang diperiksa ExperienceSerializer. GET
mengirim array datar dengan request context untuk state star akun saat ini.
Filter judul case-insensitive, kategori, dan ongoing/completed dapat digabung.
Spasi tepi diabaikan; kategori tidak dikenal menghasilkan hasil kosong dan
status tidak dikenal diabaikan seperti perilaku lama. Urutan mempertahankan
start terbaru dengan UUID sebagai penentu jika start sama. Relasi star memakai
prefetch; optimasi Count/Exists belum ditambahkan.

POST valid menghasilkan object baru dengan 201. Validasi mengembalikan 400
per field, sedangkan guest, user biasa, Editor, dan staff ditolak dengan 403.
Permission Editor untuk PUT/PATCH tidak menambah method pada URL daftar: update
nantinya memakai URL detail. Field computed dan akun star tidak dapat dipalsukan
melalui create.

Sembilan belas test endpoint baru mencakup semua role, privacy, filter sendiri
dan kombinasi, kosong, urutan, create, malformed JSON, readonly/forged input,
HEAD/OPTIONS, wrong method, serta negosiasi JSON/HTML. Test penolakan memeriksa
isi record dan relasi star. Test session memakai APIClient dengan CSRF
enforcement dan .login(): token tidak ada/salah ditolak, token benar berhasil,
dan user biasa/Editor dengan token benar tetap ditolak membuat data.

Seluruh 186 test main lulus; check, pemeriksaan migrasi dan whitespace bersih.
Runserver diperiksa melalui HTTP GET saja pada database lokal: JSON, format JSON,
Browsable API HTML, halaman Experience dan Projects mengembalikan 200. Skrip
smoke sempat meminta format JSON tetapi membatasi Accept ke HTML saja, sehingga
DRF mengembalikan 406. Header diperbaiki mengikuti browser yang menerima JSON,
lalu cek tersebut lulus. Ini koreksi pada skrip verifikasi, tanpa perubahan
konfigurasi aplikasi. Data lokal tetap satu Project dan dua Experience.

README dan panduan pribadi diperbarui sesuai progres. Halaman masih memakai
API lama; detail/update/delete/star DRF menyusul per checkpoint. PWS tidak
diubah dan commit tetap saya jalankan sendiri.

## 37. Menambahkan API detail, update, dan delete Experience

**Prompt (ringkasan):**

> Daftar dan create sudah di-commit, lanjut detail Experience. Bantu terapkan
> GET, PUT/PATCH, dan DELETE pada URL UUID, dengan Editor tetap bisa update.
> Jelasin bedanya PUT dan PATCH untuk field serta tanggal lama, respons 404,
> dan delete 204 kosong. Sertakan test role, database, read-only field, serta
> CSRF melalui session yang benar-benar login.

**Hasil penggunaan:**

Saya melanjutkan dengan bantuan AI untuk penjelasan, implementasi, pengujian,
dan dokumentasi. Commit list/create `5caa74e` diperiksa sebelum experience_detail
ditambahkan pada `main/api_views.py`. Route `api:experience-detail` memakai
`/api/v1/experiences/<uuid>/`, SessionAuthentication, dan permission empat role.
GET/HEAD membaca satu Experience dengan metadata star sesuai request, sedangkan
PUT/PATCH memperbarui instance melalui serializer yang sudah ada.

Saya memahami bahwa PUT membutuhkan field wajib, sementara PATCH hanya
mengirim perubahan. Tanggal yang tidak dikirim memakai nilai instance; rentang
tanggal tetap diperiksa, termasuk saat hanya start atau end yang diubah.
`ended_at: null` mengembalikan status ongoing. UUID dan metadata hasil
perhitungan tetap read-only. Editor dengan `main.change_experience` dan
superuser dapat update; guest, user biasa, staff tanpa permission, atau akun
yang hanya memiliki permission Project tidak mendapat hak update Experience.

DELETE khusus superuser menghapus target beserta relasi starnya lalu mengirim
204 tanpa body. Record serta star Experience lain tetap dipertahankan. UUID
valid yang hilang menghasilkan 404 jika permission lolos. Penolakan mutation
dapat menghasilkan 403 lebih dahulu karena permission diperiksa sebelum
pencarian object. POST ke detail juga mengikuti urutan permission lalu method.

Dua puluh test baru pada ExperienceDetailAPITests mencakup pembacaan publik,
privacy, HEAD/OPTIONS/Browsable API, missing UUID, update Editor dan owner,
validasi 400 beserta database yang tetap utuh, tanggal, forged metadata,
delete 204 kosong, wrong method, dan malformed JSON. Test session memakai
APIClient dengan CSRF enforcement dan .login(). Token kosong/salah ditolak;
token valid memungkinkan update Editor dan mutation owner, tetapi tidak
memperbolehkan Editor delete atau user biasa menulis.

Seluruh 206 test main lulus. Check, pemeriksaan migrasi, dan whitespace bersih.
Runserver lokal diperiksa melalui GET/HEAD saja: JSON detail sesuai object pada
daftar, HTML Browsable API 200, HEAD kosong, dan missing UUID 404 JSON. Pengujian
mutation hanya berjalan pada database test. Data lokal tetap satu Project dan
dua Experience; model, tampilan, serta PWS tidak diubah. README dan panduan
pribadi diperbarui. Commit tetap saya jalankan sendiri; endpoint star menjadi
checkpoint berikutnya sebelum integrasi UI.

## 38. Mengaktifkan endpoint star Experience

**Prompt (ringkasan):**

> Detail, update, dan delete sudah di-commit, lanjut endpoint star Experience.
> Bantu pakai relasi lama dengan IsAuthenticated supaya user biasa, Editor,
> dan owner bisa star akun sendiri. Jelasin kenapa akun harus dari request.user,
> bagaimana responsnya dipakai daftar/detail, dan kenapa toggle tidak boleh
> otomatis di-retry. Sertakan test isolasi, input palsu, serta CSRF session.

**Hasil penggunaan:**

Saya melanjutkan dengan bantuan AI untuk penjelasan, implementasi, pengujian,
dan dokumentasi. Commit detail/update/delete `a309f96` diperiksa sebelum
experience_star ditambahkan pada `main/api_views.py`. Route `api:experience-star`
memakai `/api/v1/experiences/<uuid>/star/`, method POST, SessionAuthentication,
dan IsAuthenticated. Akun login tidak membutuhkan permission Editor untuk star.

Saya memahami bahwa view mengambil akun dari request.user dan mengubah relasi
star milik akun tersebut saja. Body tidak diperlukan dan tidak dipakai untuk
memilih user atau mengubah data Experience. Respons 200 memakai serializer
dengan request context, sehingga count dan is_starred terbaru bisa dibaca
kembali pada daftar maupun detail. Field computed tetap read-only pada input
CRUD; perubahan melalui action star diatur oleh view yang memeriksa akun.

Endpoint ini toggle: dua POST berarti star lalu unstar. UI nanti tetap harus
mengunci tombol selama request dan tidak melakukan retry otomatis. Guest ditolak
403 sebelum method atau pencarian target; akun login yang mengirim method salah
mendapat 405, sementara POST ke target UUID yang tidak ada mendapat 404.

Sebelas test baru pada ExperienceStarAPITests mencakup semua role login,
isolasi antar-user, konsistensi count/state pada list/detail, forged user dan
field, missing target, wrong method, serta session yang berakhir. Test CSRF
memakai APIClient dengan enforcement dan .login() untuk user biasa, Editor,
serta owner: token kosong/salah ditolak, token benar memungkinkan toggle.
Test kompatibilitas membuktikan route star lama dan API baru memakai relasi
yang sama, tanpa model atau migration baru.

Seluruh 217 test main lulus; check, pemeriksaan migrasi, dan whitespace bersih.
Runserver diperiksa melalui GET saja: guest mendapat 403 JSON pada endpoint
star, termasuk UUID yang hilang, dan Browsable API list/detail tetap 200 HTML.
Mutation diuji pada database test. Data lokal tetap satu Project dan dua
Experience; tampilan dan PWS tidak diubah. README serta panduan pribadi
diperbarui. Sesudah commit ini, branch API siap direview dan diintegrasikan
sebelum memulai branch UI. Commit, push, dan merge tetap saya jalankan sendiri.

## Verifikasi manual

Saya tidak menjadikan output AI sebagai hasil final tanpa pemeriksaan. Beberapa
langkah yang saya gunakan untuk melakukan verifikasi adalah:

```bash
python manage.py check
python manage.py test main
git diff --check
git status
git diff
```

Saya juga mencoba navigasi, filter AJAX, loading dan empty state, modal create,
toast, confirmation delete, star dan unstar, serta layout desktop dan mobile
melalui browser. Pada akhir Tugas 5, seluruh 73 automated test dipastikan lulus
sebelum dokumentasi diselesaikan.

Pada checkpoint lokal Tutorial 07, full suite terakhir mencatat 140 test lulus.
Rincian bantuan, eksperimen permission, hasil browser, dan batas verifikasinya
ada pada entri 22-33. Status push, deployment, serta pengumpulan tetap dicatat
terpisah dari keberhasilan test lokal.
