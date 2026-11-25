import streamlit as st

INTRO = '''### Layihənin məqsədi
Günəş işığını elektrik enerjisinə çevirə biləcək üzvi molekulları kompüterdə araşdırırıq. Minlərlə namizədi bir-bir laboratoriyada yoxlamaq əvəzinə AI ilə ilkin seçim aparırıq. **PCE burada hesablanmış referens göstəricidir, real panelin ölçülmüş səmərəliliyi deyil.**

**İş prinsipi:** SMILES → molekulyar qraf → 21 kimyəvi göstərici və 2048 bitlik Morgan izi → XGBoost → proqnoz və interval → namizədlərin sıralanması.

Kvant hissəsində molekulyar qraf üzərində ehtimalın yayılmasını araşdırırıq. Bu, kvant kompüterində icra deyil və elektronun real trayektoriyasını göstərmir. Yekun proqnoz modeli klassikdir; kvant xüsusiyyətləri ayrıca tədqiq edilib.'''

DESCRIPTORS = [
('MolWt','Molekulyar kütlə, g/mol. Atomların kütlələrinin cəmi (hidrogenlər daxil).'),('MolLogP','Oktanol və su arasında paylanmanın hesablanmış loqarifmi; böyük qiymət adətən yağabənzər mühitə meyli göstərir.'),('TPSA','Topoloji polar səth sahəsi, Å²; polar atomların səthə töhfəsinin təxmini cəmi.'),('NumHDonors','Hidrogen rabitəsi verə bilən qrupların sayı.'),('NumHAcceptors','Hidrogen rabitəsi qəbul edə bilən qrupların sayı.'),('NumRotatableBonds','Fırlana bilən rabitələrin sayı; elastiklik haqqında məlumat verir.'),('NumAromaticRings','Aromatik halqaların sayı; delokalizasiya ilə əlaqəli struktur göstəricisi.'),('NumAliphaticRings','Aromatik olmayan halqaların sayı.'),('NumHeteroatoms','Karbon və hidrogendən fərqli atomların sayı.'),('RingCount','Halqaların ümumi sayı (RDKit tərifinə görə).'),('FractionCSP3','sp³ hibridləşmiş karbonların bütün karbonlara nisbəti.'),('BalabanJ','Qraf məsafələri və əlaqələr əsasında topoloji indeks.'),('BertzCT','Molekulyar strukturun mürəkkəbliyini ifadə edən indeks.'),('Chi0','Atomların qrafdakı əlaqə dərəcələrinə əsaslanan indeks.'),('Chi1','Rabitə ilə bağlı atomların əlaqə dərəcələrinə əsaslanan indeks.'),('Kappa1','Molekulyar qrafın ümumi forma indekslərindən biri.'),('Kappa2','İki rabitəli yollar əsasında forma və şaxələnmə indeksi.'),('Kappa3','Üç rabitəli yollar əsasında forma indeksi.'),('NumAtoms','Qrafda açıq göstərilən atomların sayı; adətən gizli hidrogenlər daxil deyil.'),('NumBonds','Qrafdakı rabitələrin sayı.'),('NumConjugatedBonds','RDKit tərəfindən konyuqasiya olunmuş kimi tanınan rabitələrin sayı; elektron delokalizasiyası ilə əlaqəlidir.')]

PAGES={
'Molecular Explorer': '''**SMILES** molekulun mətnlə yazılışıdır. Məsələn, `CCO` etanoldur, `c1ccccc1` benzoldur. Kiçik hərflər aromatik atomları, rəqəmlər halqanın bağlanmasını, mötərizələr şaxələri bildirə bilər. Canonical SMILES eyni struktur üçün standartlaşdırılmış yazılışdır.

2D şəkil atomların əlaqələrini, 3D conformer isə mümkün fəza formasını göstərir. ETKDG alqoritmi ilə yaradılan 3D forma kvant-kimyəvi optimallaşdırma deyil. Dataset membership molekulun məlum bölmədə olub-olmadığını bildirir. `not found` yeni kəşf demək deyil. Descriptor warning təlim diapazonundan kənar göstəriciləri xəbər verir; xəbərdarlığın olmaması etibarlılığa zəmanət deyil.

**Sına:** benzol və etanolun strukturunu müqayisə et. Bu sadə molekullar təlim sahəsindən kənar ola bilər; PCE proqnozunu real nəticə sayma.''',
'AI Property Prediction': '''**HOMO** elektronla dolu ən yüksək enerjili molekulyar orbitaldır. **LUMO** elektronla dolu olmayan ən aşağı enerjili orbitaldır. Enerji vahidi eV (elektronvolt) adlanır. **Energy Gap = LUMO − HOMO.** Məsələn, −3.96 − (−5.34) = 1.38 eV. Bu orbital fərqi optik enerji boşluğu ilə mütləq eyni deyil.

**PCE** (Power Conversion Efficiency) enerji çevrilmə səmərəliliyidir. Burada datasetin hesablanmış PCE göstəricisini proqnozlaşdırırıq; real cihazın səmərəliliyi materialdan əlavə cihaz quruluşundan da asılıdır.

**XGBoost:** çoxlu qərar ağacı ardıcıl öyrənərək əvvəlki ağacların xətalarını azaltmağa çalışır. Hər HOMO, LUMO və PCE üçün üç modelin ortalaması alınır; gap fərqdən hesablanır. Giriş 21 descriptor + 2048 Morgan bitidir. Morgan izi atom ətrafındakı lokal strukturları radius 2 ilə kodlayır; bitlər fiziki enerji deyil.

**90% nominal interval:** kalibrasiya xətalarından hesablanmış proqnoz aralığıdır. Bu, hər molekul üçün 90% zəmanət deyil. Məsələn, PCE 10% ± 1.76 faiz bəndi olarsa aralıq təxminən 8.24–11.76%-dir.

**Sına:** iki referens molekul seç, gap fərqini əl ilə hesabla və intervalları müqayisə et.''',
'Quantum Walk Simulator': '''Molekulu qraf kimi təsəvvür et: atomlar düyün, rabitələr kənardır. Başlanğıc atomu ehtimalın ilkin yerləşdiyi düyündür. Zaman parametri ölçüsüzdür, saniyə deyil. t=0 olduqda bütün ehtimal başlanğıc atomundadır.

**Klassik walk:** ehtimal istiliyin yayılması kimi qrafda diffuziya edir. **Quantum walk:** kompleks amplitudalar yayılır və bir-birini gücləndirə və ya zəiflədə bilər (interferensiya). Ehtimal amplitudanın modulunun kvadratıdır. Hər iki paylanmanın cəmi 1 olmalıdır.

A çəkili qonşuluq matrisi, D hər düyünün çəkilər cəminin diaqonal matrisi, L=D−A qraf Laplasianıdır. Rabitə çəkisi rabitə növü, konyuqasiya və atom nömrələrinin fərqindən asılıdır. 0.25 əmsalları seçilmiş evristik parametrlərdir, fiziki sabit deyil. Çəkilər orta müsbət çəkiyə bölünür. Matris eksponenti zamanla yayılmanı hesablayır; i kompleks vahiddir.

**Sına:** eyni atom üçün t=0, 1 və 4 seç. Sonra başlanğıc atomunu dəyiş. Qrafikdə X atom indeksi, Y ehtimaldır. Kvant paylanmasının həmişə daha geniş yayılacağını gözləmə.''',
'Material Screening': '''Screening çoxlu namizədi ilkin qiymətləndirmə və sıralama prosesidir. Referens rejimində təlimdən ayrı 7500 molekulun əvvəlcədən hesablanmış proqnozları istifadə edilir. CSV rejimində `smiles` sütunu və ya hər sətirdə bir SMILES daxil et; maksimum 500 namizəd. Təkrar strukturlar çıxarılır, etibarsız girişlər göstərilir.

Minimum predicted PCE aşağı həddi, Maximum displayed candidates isə göstərilən sətir sayını müəyyən edir. Sıralama PCE nöqtə proqnozuna görədir, intervala görə deyil. Yüksək PCE və dar interval faydalı ilkin məlumatdır, lakin sintez, stabillik, toksiklik və real cihaz sınağı ayrıca tələb olunur.

**Sına:** minimum PCE həddini dəyiş və siyahının necə qısaldığını müşahidə et. CSV-ni endir və iki namizədin proqnozunu müqayisə et.''',
'Research & Experiments': '''**Dataset:** CEPDB hesablanmış üzvi fotovoltaik molekul göstəriciləridir. 50 000 molekuldan 35 031 təlim, 7 469 kalibrasiya, 7 500 test üçün ayrılıb. Generic scaffold molekulun ümumiləşdirilmiş halqa və birləşdirici skeletidir; bölmələr arasında bu skeletlər təkrarlanmır. Bu, oxşar strukturların təlim və test arasında qarışması riskini azaldır.

**MAE** orta mütləq xəta, **RMSE** böyük xətalara daha həssas kvadratik xəta kökü, **R²** referens variasiyasının model tərəfindən izah olunan hissəsini ölçən göstəricidir. MAE/RMSE aşağı, R² yüksək olduqda adətən daha yaxşıdır. R² təsnifat dəqiqliyi deyil. Coverage intervala düşən referens qiymətlərin payıdır.

**Active Learning:** əvvəlcə 500 etiketli molekul, sonra 500-lük addımlarla 5000-ə qədər seçim. AL0 təsadüfi, AL1 qeyri-müəyyənlik, AL2 Morgan müxtəlifliyi, AL3 klassik walk müxtəlifliyi, AL4 spektral müxtəliflik, AL5 kvant walk müxtəlifliyi, AL6 qeyri-müəyyənlik + klassik walk, AL7 qeyri-müəyyənlik + kvant walk. Müxtəliflik bir-birindən fərqli namizədləri seçməyə çalışır. Atom-aware walk ehtimalları atom növlərinə görə qruplaşdırır; spektral xüsusiyyətlər qraf matrisinin özqiymətlərindən və əlaqəli göstəricilərdən alınır. Etiketlər əvvəlcədən hesablanıb; seçim simulyasiyadır.

**AULC:** etiket büdcəsi boyunca MAE əyrisinin normallaşdırılmış sahəsi; aşağı daha yaxşıdır. SD üç təkrar arasındakı dəyişkənlikdir. Bootstrap etibar intervalı test nümunələrini təkrar seçərək xəta fərqinin qeyri-müəyyənliyini qiymətləndirir. Sıfırı əhatə edirsə, üstünlük təsdiqlənməyib.

**Precision@100 = 93/100:** seçilmiş 100 namizəddən 93-ü referens PCE üzrə ən yüksək 10%-dədir. Bu, ümumi dəqiqlik deyil. Top 100 orta referens PCE 9.64%, bütün testdə 4.41%-dir. Kvant hibridi PCE-də kiçik üstünlük göstərib, amma 5% meyarına çatmayıb və statistik üstünlük təsdiqlənməyib.'''}

FAQ=[('Layihənin yeniliyi nədir?','Atom növlərinə həssas kvant qraf xüsusiyyətlərini və onların aktiv seçimdə faydasını müqayisəli yoxlayıb, nəticələri qeyri-müəyyənlikli material seçimi tətbiqində birləşdirmişik. Dünyada ilk olduğunu iddia etmirik.'),('Kvant kompüteri istifadə etmisiniz?','Xeyr. Klassik CPU-da matris hesablamaları ilə kvant walk simulyasiyası aparılıb.'),('Niyə yekun model klassikdir?','Kvant xüsusiyyətləri sabit və statistik təsdiqlənmiş üstünlük vermədi. Sadə, yoxlanmış klassik model seçildi.'),('93% nə deməkdir?','Proqnoza görə ilk 100 molekuldan 93-ü hesablanmış referens PCE üzrə ən yüksək 10%-dədir.'),('Yeni material kəşf etmisiniz?','Xeyr. Məlum hesablanmış namizədləri sıraladıq; yeni materialın sintezi və cihaz sınağı aparılmayıb.'),('Niyə test ayrıca saxlanılıb?','Modelin görmədiyi strukturlarda performansı ölçmək üçün. Kalibrasiya intervalı müəyyən edir, test isə yekun qiymətləndirmə üçündür.'),('Kvant üstünlüyü varmı?','Təsdiqlənməyib. PCE üzrə kiçik fərq 5% meyarını ödəmir və etibar intervalları sıfırı əhatə edir.')]

