# AI Prompt Log

Dokumen ini berisi beberapa contoh prompt yang mewakili penggunaan OpenAI Codex
selama pengerjaan Tutorial, Tugas 1, Tugas 2, dan Tugas 3. Prompt di bawah diringkas dari
percakapan asli agar lebih mudah dibaca. Informasi sensitif dan percakapan yang
tidak berkaitan dengan tugas tidak disertakan.

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

Saya juga mencoba navigasi, form Experience, filter, confirmation delete, empty
state, detail project, dan layout desktop serta mobile melalui browser. Seluruh
23 test juga saya pastikan lulus sebelum dokumentasi diselesaikan.
