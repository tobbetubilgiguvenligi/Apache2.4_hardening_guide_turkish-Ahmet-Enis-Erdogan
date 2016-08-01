# Apache HTTP Server 2.4 Sıkılaştırma Kılavuzu

Bu kılavuzda farklı kaynaklardan yararlanarak bir Apache HTTP 2.4 serverini sıkılaştırma ile alakalı
bilgiler paylaşıyorum. Herhangi bir UNIX sistem üzerinde Apache HTTP Server' ınızı
daha güvenli hale getirmek için bu adımları izleyebilirsiniz. Ben sistem olarak Ubuntu 14.04 üzerinde
çalıştım. Ancak diğer UNIX distrolarında da bu kılavuzdan yararlanamamanız için bir engel
olduğunu düşünmüyorum.

## 1. Server hakkında bilgileri gizleyin
Default olarak herhangi bir hata sayfasında kullanıcı sizin kullandığınız apache versiyonunu 
görebilir. Bu da saldırganların sizin kullandığınız sistemi anlamaya çalışma sürecini ortadan
kaldırır ve onların işini kolaylaştırmış olursunuz.

Server hakkındaki bilgileri gizlemek için apache2.conf(bazi distrolarda httpd.conf) dosyasina su 
directiveleri ekleyebilirsiniz.

```
ServerTokens Prod  
ServerSignatures Off
```
## 2. Directory' lere erişimi engelleyin
Default olarak eger bir index.html dosyaniz yoksa Apache root directorynin altındaki herşeyi
listeler. Bu durumda kullanıcının görmesini istemediğiniz dosyalar da erişime açık kalır. 
Bu durumu engellemek için httpd.conf dosyasında erişimi engellemek istediğiniz Directorylerde
asağıdaki değişikliği yapabilirsiniz.
```
<Directory /var/www/html>  
    Options -Indexes  
</Directory>
```
## 3. Apache' yi surekli olarak güncel tutun
Apache' nin developer community si surekli olarak güvenlik açıklarını kapatmak için ugrasiyor.
Bu nedenle surekli olarak en güncel Apache versiyonunu kullanmaniz sizin faydaniza olacaktir.
Apache versiyonunu asağıdaki command ile öğrenebibilirsiniz.
```
apache2 -v  
```

## 4. Apache' yi başka ayrıcalıksız kullanıcı ve grupla çalıştırın
Ubuntu'da apache' yi apt-get install ile yüklediğinizde Apache zaten user ve group olarak www-data' yi
kullaniyor. Ancak baska distrolarda Apache daemon olarak veya nobody olarak calıştırılıyor olabilir. 
Bu durumda asağıdaki commandleri kullanarak yeni bir group ve user olusturun.
```
groupadd apache  
useradd -G apache apache  
```
Apache' nin yüklendiği directory de (bundan sonra bu directory $APACHE_INST_DIR olarak belirtilecek) 
httpd.conf veya apache2.conf seklinde bir dosya olacaktir(bundan sonra sadece apache2.conf belirtilecek).
Bu dosyada User ve Group kısımlarını asağıdaki gibi degistirin

```
User apache  
Group apache
```

dosyayi kaydedip Apache'yi tekrar baslatin.

## 5. System ayarlarını koruma

Default olarak kullanıcılar .htaccess dosyasini kullanarak apache configuration ini override
edebilirler. Bunu engellemek için conf dosyanizda($APACHE_INST_DIR/apache2.conf) AllowOverride i None olarak set etmeniz gerekiyor. Bunu 
root directory directive'inde yapmaniz gerekiyor.
```
<Directory />  
    AllowOverride None  
</Directory>
```
Bu değişikliği yaptıktan sonra Apache' yi yeniden baslatin veya reload edin.
## 6. HTTP Request Methodlarını limitleme
Cogu zaman web uygulamanizda sadece GET, POST, HEAD methodlarına ihtiyaciniz olacak. Ancak 
apache bu methodlarla birlikte PUT, DELETE, TRACE, CONNECT gibi diğer HTTP 1.1 protokol metodlarını
da destekliyor. Bu durum potansiyel riskleri dogurdugundan sadece kullanilan HTTP methodlarını
kabul ederek riski ortadan kaldirabilirsiniz. Asağıdaki directive' i limitlemek istediğiniz
directory directive lerinin içinde kullanabilirsiniz.
```
<LimitExcept GET HEAD POST>
    deny from all
</LimitExcept>
```
## 7. HTTP TRACE metodunu devre dışı bırakın
Default olarak Apache web server TRACE metodu etkindir. Bu durum Cross Site Tracing atagina ve
saldirganların kullanıcıların cookie bilgilerine ulasmasına olanak saglar. Bu nedenle TraceEnable
ayarini off yapmaniz bu tur atakları önlemenizi saglayacaktir. $APACHE_INST_DIR/apache2.conf
dosyasında asağıdaki sekilde degisiklik yaptıktan sonra Apache' yi tekrar baslatabilirsiniz.
```
TraceEnable off
```
Bu sekilde serverınız TRACE metodlarına izin vermeyecek ve Cross Site Tracing ataklarını 
bloklayacaktir.

## 8. Cookie'yi HttpOnly ve Secure flag ile olusturun
Cogu Cross Site Scripting atagini cookie de HttpOnly ve Secure flagleri ile engelleyebilirsiniz.
HttpOnly ve Secure flagleri olmadan cookieler manipule edilerek saldirilar yapilabilir.
HttpOnly ve Secure flaglerini set etmek için oncelikle headers modulunu etkin hale getirmeniz gerekiyor. 
Ubuntu'da su sekilde yapabilirsiniz
```
a2enmod headers
```
Ardindan $APACHE_INST_DIR/apache2.conf dosyasında asağıdaki değişikliği yapmaniz gerekiyor.

```
Header edit Set-Cookie ^(.*)$ $1;HttpOnly;Secure
```

Bu sekilde cookienin sonunda HttpOnly ve Secure flaglerini eklemis oluyorsunuz. Degisiklikleri
etkin hale getirmek için Apache'yi yeniden baslatmaniz gerekiyor.

## 9. Clickjacking ataklarından koruma
Clickjacking saldirganların site icerisinde tiklanabilir iceriklere hyperlinkler gizlemesi 
kullanıcıları yaniltmasıdir. Bunu engellemek için conf dosyasina su satırı ekleyebilirsiniz. 
Bu yontemde de Header'da degisiklik yapabilmeniz için Apache' nin header modulunu onceki gibi 
etkin hale getirmeniz gerekiyor. 
```
Header always append X-Frame-Options SAMEORIGIN
```

## 10. Server Side Include ları devre dışı bırakma
Server Side Include(SSI) lar server uzerine ek yuk bindirdiginden cok yogun bir trafik aliyorsaniz
veya ortak bir environment kullaniyorsaniz SSI' i devre dışı bırakmayi dusunebilirsiniz.
SSI'i devre dışı bırakacağınız direcotry directive' inde asağıdaki gibi değişiklik yapabilirsiniz.
```
<Directory /var/www/html>  
    Options -Includes -Indexes  
    ...  
</Directory> 
```
## 11. X-XSS Korunması
Cross Site Scripting koruması bircok web browser da bypass edilebiliyor. Ancak web uygulaması
için bu korumayi zorla etkin hale getirebilirsiniz. Bunun için conf dosyasina asağıdaki satırı
ekleyebilirsiniz.
```
Header X-XSS-Protection "1; mode=block"
```
## 12. HTTP 1.0 protokolunu kullanim dışı bırakma
Güvenlik acisindan eski protokolleri kullanmak riskli oldugundan HTTP 1.0 protokolunu kullanim
dışı birakabilirsiniz. Bunun için rewrite modulunu kullanmaniz gerekecek. Rewrite modulunu etkin
hale getirmek için 
```
a2enmod rewrite
```
komutunu kullanin.

Asağıdaki satırları conf dosyasina ekleyin.
```
RewriteEngine On  
RewriteCondition %{THE_REQUEST} !HTTP/1.1$  
RewriteRule .* - [F]
```

ve Apache' yi yeniden baslatin.

## 13. Timeout degerini azaltma
Apache' de default olarak timeout degeri 300 saniye. Bu DoS ataklarının kurbani olabileceginiz
anlamina gelebilir. Timeout degerini kucultmek için asağıdaki satırı conf dosyasina ekleyebilirsiniz.
```
Timeout 60
```
## 14. mod_security modulunun kullanılması

Mod Security açık kaynak kodlu bir Web Application Firewall' dur. Genel bir web uygulaması 
koruması için ana kurallar belirlenmiştir.

### 14.1 mod_security kurulumu

Mod Security' yi kurmak için asağıdaki komutu calıştırılıyor`
$ sudo apt-get install libapache2-mod-security2
```
modulu etkin hale getirmek için 
```
a2enmod security2
```  
Baska UNIX distolarda core rule ları da ayrica indirip aktif hale getirmeniz gerekebilir. 
Bunun için asağıdaki adimları takip edebilirsiniz.

[https://github.com/SpiderLabs/owasp-modsecurity-crs/zipball/master](https://github.com/SpiderLabs/owasp-modsecurity-crs/zipball/master)  
Bu linkten core rule'ları indirdikten sonra zip dosyasini acin. Içindeki dosyları `$APACHE_INST_DIR/conf/` directory'sine
kopyalayin. `modsecurity_crs_10_setup.conf.example` dosyasini `modsecurity_crs_10_setup.conf` 
olarak adlandirin.  

Bu rule'ları etkinlestirmek için de conf dosyasina asağıdaki directive'i ekleyin
```
<IfModule security2_module>  
    Include conf/modsecurity_crs_10_setup.conf  
    Include conf/base_rules/*.conf  
</IfModule>
```
su an mod_security sayesinde web uygulamaniz için bir WAF kurmuş bulunmaktasınız.


## Referanslar

[1] https://geekflare.com/apache-web-server-hardening-security/  
[2] http://www.tecmint.com/apache-security-tips/  
[3] https://httpd.apache.org/docs/2.4/misc/security_tips.html  
[4] https://www.modsecurity.org/download.html