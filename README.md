# Depo İş Makineleri Web Sitesi

Bu depo, ikinci el iş makinesi alım satımı, yedek parça ve servis hizmetleri sunan işletmeniz için hazırlanan tanıtım web sitesini içerir.

## İçerik
- `index.html`: Kurumsal tanıtım sayfası ve veri yerleştirme için gerekli HTML iskeleti.
- `styles.css`: Site için kullanılan temel stiller.
- `site-data.js`: Stok ve iletişim bilgilerini JSON dosyasından yükleyip sayfaya yerleştiren tarayıcı betiği.
- `data/doganismakinalari-data.json`: www.doganismakinalari.com adresinden çekilecek stok ve iletişim verilerinin tutulduğu dosya.
- `scripts/`: Dış kaynaktan veri çekmek için kullanılabilecek yardımcı komut dosyaları.

## Veri Güncelleme
Stok ve iletişim içerikleri `data/doganismakinalari-data.json` dosyasından okunur. Dosya biçimi aşağıdaki gibidir:

```json
{
  "lastFetched": "2024-05-01T12:00:00+03:00",
  "contact": {
    "phone": "+90 (212) 000 00 00",
    "email": "info@doganismakinalari.com",
    "address": "adres metni",
    "servicePhone": "+90 (532) 000 00 00"
  },
  "machines": [
    {
      "title": "Makine adı",
      "specs": ["özellik 1", "özellik 2"],
      "detailUrl": "https://www.doganismakinalari.com/..."
    }
  ]
}
```

### Otomatik veri çekme
Çalışma ortamında dış ağ erişimi kısıtlı olduğundan, bu depoda veri dosyası örnek değerlerle sağlanmamıştır. İnternet erişimine sahip bir ortamda aşağıdaki adımları izleyerek verileri çekip JSON dosyasını güncelleyebilirsiniz:

1. Gerekli bağımlılıkları yükleyin:
   ```bash
   pip install requests beautifulsoup4
   ```
2. `scripts/fetch_doganismakinalari_data.py` komut dosyasını çalıştırın:
   ```bash
   python scripts/fetch_doganismakinalari_data.py
   ```
3. Betik `data/doganismakinalari-data.json` dosyasını güncellediğinde sayfa otomatik olarak yeni verileri gösterecektir.

Betik, bağlantı veya erişim sorunları yaşanması durumunda bunları konsola raporlar. Alternatif olarak JSON dosyasını elle düzenleyerek stok ve iletişim bilgilerini girebilirsiniz.

## Hızlı Önizleme
Web sitesini dakikalar içinde görüntülemek için aşağıdaki adımları izleyin:

1. Terminal/Powershell penceresi açın ve depo klasörüne girin:
   ```bash
   cd depo
   ```
2. Aşağıdaki komutu çalıştırarak yerleşik önizleme yardımcısını başlatın:
   ```bash
   python scripts/preview.py
   ```
   Komut, varsayılan tarayıcınızda `http://localhost:8000/index.html` adresini açar.
3. Önizleme işiniz bittiğinde sunucuyu durdurmak için sunucu komutunun çalıştığı terminalde `Ctrl + C` tuş bileşimine basın.

> Dilerseniz `python scripts/preview.py --port 8080 --no-open` gibi parametrelerle farklı bir port seçebilir veya tarayıcıyı otomatik açmayı kapatabilirsiniz.

## Siteyi Görüntüleme
Projeyi yerel ortamınızda incelemek için aşağıdaki yöntemlerden birini kullanabilirsiniz:

### 1. Dosyayı doğrudan açma
1. Bu depoyu bilgisayarınıza indirin veya klonlayın.
2. `index.html` dosyasını çift tıklayarak varsayılan tarayıcınızda açın.

Bu yöntem ek bir araç gerektirmez; ancak bazı tarayıcılar dosya tabanlı isteklere kısıt koyabildiğinden stok/iletişim verileri yüklenmeyebilir. Bu durumla karşılaşırsanız ikinci yöntemi tercih edin.

### 2. Basit yerel sunucu ile görüntüleme
1. Depo klasörüne gidin.
2. Terminalde aşağıdaki komutu çalıştırarak basit bir HTTP sunucusu başlatın:
   ```bash
   python -m http.server 8000
   ```
3. Tarayıcınızda `http://localhost:8000` adresine gidin ve `index.html` dosyasını açın.

Tarayıcı, JSON dosyasını bu sunucu üzerinden sorunsuzca okuyabildiği için stok kartları ve iletişim bilgilerinin yüklenmesi garanti altına alınmış olur.

Sunucuyu kapatmak için terminalde `Ctrl + C` tuş bileşimini kullanabilirsiniz.

## Yayınlama
Siteyi herkese açık olarak yayınlamak için GitHub Pages kullanabilirsiniz. Depoda yer alan GitHub Actions iş akışı, `main` dalına yapılan her itmede siteyi otomatik olarak dağıtır. Aşağıdaki adımları takip edin:

1. Bu depoyu GitHub'da yeni bir repoya gönderin.
2. GitHub arayüzünde **Settings → Pages** bölümüne gidin ve "Build and deployment" alanında **GitHub Actions** seçili olduğundan emin olun.
3. `main` dalına değişiklik gönderin veya `Actions` sekmesinden **Deploy static site to GitHub Pages** iş akışını manuel olarak çalıştırın.
4. Dağıtım tamamlandığında iş akışı çıktısında yayınlanan site bağlantısı görünecektir. Bağlantı aynı zamanda `Settings → Pages` sayfasında da listelenir.

İş akışı, depo kökündeki statik dosyaları (HTML, CSS, JS ve veri dosyalarını) `github-pages` ortamına yükler. Gerekiyorsa `deploy.yml` içinde `path` değerini değiştirerek yalnızca belirli bir klasörü yayınlayabilirsiniz.

## Geliştirme
Projeyi düzenlemek için herhangi bir kod düzenleyici kullanabilir, değişiklikleri kaydettikten sonra yukarıdaki yöntemlerden biriyle sonucu kontrol edebilirsiniz.

## Testler
Site varlıklarının beklenen kancaları ve veri şemasını koruduğunu doğrulamak için Python'un yerleşik `unittest` modülünü kullanabilirsiniz:

```bash
python -m unittest
```

Bu komut, `tests/test_site_integrity.py` dosyasındaki kontrol adımlarını çalıştırarak HTML iskeleti ve JSON veri dosyasının temel gereksinimleri sağladığını doğrular.
