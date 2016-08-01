Bu kilavuzda farkli kaynaklardan yararlanarak bir Apache HTTP serverini sikilastirma ile alakali
odev kapsaminda bilgiler paylasiyorum. Herhangi bir unix sistem uzerinde Apache HTTP Server inizi
daha guvenli hale getirmek icin bu adimlari izleyebilirsiniz. Ben sistem olarak Ubuntu 14.04 uzerinde
calistim. Ancak diger UNIX distrolarinda da bu kilavuzdan yararlanamamaniz icin bir sebep
oldugunu dusunmuyorum.

# 1. Server hakkinda bilgileri gizleyin
## 1.1. Apache ve OS versiyonunun saklanmasi
Default olarak herhangi bir hata sayfasinda kullanici sizin kullandiginiz apache versiyonunu 
gorebilir. Bu da saldirganlarin sizin kullandiginiz sistemi anlamaya calismasi surecini ortadan
kaldirir ve onlarin isini kolaylastirmis olursunuz.

Server hakkindaki bilgileri gizlemek icin httpd.conf(yada baska bir conf dosyasinda) dosyasina su 
directiveleri ekleyebilirsiniz.

>ServerTokens Prod  
>ServerSignatures Off
 
# 2. Directory lere erisimi engelleyin
Default olarak eger bir index.html dosyaniz yoksa Apache root directorynin altindaki herseyi
listeler. Bu durumda kullanicinin gormesini istemediginiz dosyalar da erisime acik kalir. 
Bu durumu engellemek icin httpd.conf dosyasinda erisimi engellemek istediginiz Directorylerde
asagidaki degisikligi yapabilirsiniz.
><Directory /var/www/html>  
>&nbsp;&nbsp;&nbsp;&nbsp;Options -Indexes  
>\</Directory>

# 3. Apache yi surekli olarak guncel tutun
Apache nin developer community si surekli olarak guvenlik aciklarini kapatmak icin ugrasiyor.
Bu nedenle surekli olarak en guncel Apache versiyonunu kullanmaniz sizin faydaniza olacaktir.
Apache versiyonunu asagidaki command ile ogrenebibilirsiniz.
>apache2 -v  

# 4. Apache'yi baska ayricaliksiz kullanici ve grupla calistirin
Ubuntu'da apache yi apt-get install ile yuklediginizde Apache zaten user ve group olarak www-data' yi
kullaniyor. Ancak baska distrolarda Apache daemon olarak veya nobody olarak calistiriliyor olabilir. 
Bu durumda asagidaki commandleri kullanarak yeni bir group ve user olusturun.

>groupadd apache  
>useradd -G apache apache  

Apache nin yuklendigi directory de (bundan sonra bu directory $APACHE_INST_DIR olarak belirtilecek) 
httpd.conf veya apache2.conf seklinde bir dosya olacaktir(bundan sonra sadece apache2.conf belirtilecek).
Bu dosyada User ve Group kisimlarini asagidaki gibi degistirin

>User apache  
>Group apache

dosyayi kaydedip Apache'yi tekrar baslatin.

# 5. System ayarlarini koruma

Default olarak kullanicilar .htaccess dosyasini kullanarak apache configuration ini override
edebilirler. Bunu engellemek icin conf dosyanizda($APACHE_INST_DIR/apache2.conf) AllowOverride i None olarak set etmeniz gerekiyor. Bunu 
root directory directive'inde yapmaniz gerekiyor.
>\<Directory />  
>&nbsp;&nbsp;&nbsp;&nbsp;AllowOverride None  
>\</Directory>

Bu degisikligi yaptiktan sonra Apache yi yeniden baslatin veya reload edin.
# 6. HTTP Request Methodlarini limitleme
Cogu zaman web uygulamanizda sadece GET, POST, HEAD methodlarina ihtiyaciniz olacak. Ancak 
apache bu methodlarla birlikte PUT, DELETE, TRACE, CONNECT gibi diger HTTP 1.1 protokol metodlarini
da destekliyor. Bu durum potansiyel riskleri dogurdugundan sadece kullanilan HTTP methodlarini
kabul ederek riski ortadan kaldirabilirsiniz. Asagidaki directive i limitlemek istediginiz
directory directive lerinin icinde kullanabilirsiniz.
><LimitExcept GET HEAD POST>
>&nbsp;&nbsp;&nbsp;&nbsp;deny from all
></LimitExcept>

# 7. HTTP TRACE metodunu devre disi birakin
Default olarak Apache web server TRACE metodu etkindir. Bu durum Cross Site Tracing atagina ve
saldirganlarin kullanicilarin cookie bilgilerine ulasmasina olanak saglar. Bu nedenle TraceEnable
ayarini off yapmaniz bu tur ataklari onlemenizi saglayacaktir. $APACHE_INST_DIR/apache2.conf
dosyasinda asagidaki sekilde degisiklik yaptiktan sonra Apache' yi tekrar baslatabilirsiniz.

>TraceEnable off

Bu sekilde serveriniz TRACE metodlarina izin vermeyecek ve Cross Site Tracing ataklarini 
bloklayacaktir.

# 8. Cookie'yi HttpOnly ve Secure flag ile olusturun
Cogu Cross Site Scripting atagini cookie de HttpOnly ve Secure flagleri ile engelleyebilirsiniz.
HttpOnly ve Secure flagleri olmadan cookieler manipule edilerek saldirilar yapilabilir.
HttpOnly ve Secure flaglerini set etmek icin oncelikle headers modulunu etkin hale getirmeniz gerekiyor. 
Ubuntu'da su sekilde yapabilirsiniz
> a2enmod headers

Ardindan $APACHE_INST_DIR/apache2.conf dosyasinda asagidaki degisikligi yapmaniz gerekiyor.
> Header edit Set-Cookie ^(.*)$ $1;HttpOnly;Secure

Bu sekilde cookienin sonunda HttpOnly ve Secure flaglerini eklemis oluyorsunuz. Degisiklikleri
etkin hale getirmek icin Apache'yi yeniden baslatmaniz gerekiyor.

# 9. Clickjacking ataklarindan koruma
Clickjacking saldirganlarin site icerisinde tiklanabilir iceriklere hyperlinkler gizlemesi 
kullanicilari yaniltmasidir. Bunu engellemek icin conf dosyasina su satiri ekleyebilirsiniz. 
Bu yontemde de Header'da degisiklik yapabilmeniz icin Apache' nin header modulunu onceki gibi 
etkin hale getirmeniz gerekiyor. 
> Header always append X-Frame-Options SAMEORIGIN

# 10. Server Side Include lari devre disi birakma
Server Side Include(SSI) lar server uzerine ek yuk bindirdiginden cok yogun bir trafik aliyorsaniz
veya ortak bir environment kullaniyorsaniz SSI' i devre disi birakmayi dusunebilirsiniz.
SSI'i devre disi birakacaginiz direcotry directive' inde asagidaki gibi degisiklik yapabilirsiniz.
> <Directory /var/www/html>  
> &nbsp;&nbsp;&nbsp;&nbsp;Options -Includes -Indexes  
> &nbsp;&nbsp;&nbsp;&nbsp;...  
> \</Directory> 

# 11. X-XSS Korunmasi
Cross Site Scripting korumasi bircok web browser da bypass edilebiliyor. Ancak web uygulamasi
icin bu korumayi zorla etkin hale getirebilirsiniz. Bunun icin conf dosyasina asagidaki satiri
ekleyebilirsiniz.
> Header X-XSS-Protection "1; mode=block"

# 12. Sadece HTTP 1.0 protokolunu kullanim disi birakma
Guvenlik acisindan eski protokolleri kullanmak riskli oldugundan HTTP 1.0 protokolunu kullanim
disi birakabilirsiniz. Bunun icin rewrite modulunu kullanmaniz gerekecek. Rewrite modulunu etkin
hale getirmek icin 
> a2enmod rewrite
komutunu kullanin.

Asagidaki satirlari conf dosyasina ekleyin.
> RewriteEngine On  
> RewriteCondition %{THE_REQUEST} !HTTP/1.1$  
> RewriteRule .* - [F]

ve Apache' yi yeniden baslatin.

# 13. Timeout degerini kucultme
Apache' de default olarak timeout degeri 300 saniye. Bu DoS ataklarinin kurbani olabileceginiz
anlamina gelebilir. Timeout degerini kucultmek icin asagidaki satiri conf dosyasina ekleyebilirsiniz.

> Timeout 60

# 14. mod_security modulunun kullanilmasi

Mod Security acik kaynak kodlu bir Web Application Firewall' dur. Genel bir web uygulamasi 
korumasi icin ana kurallar belirlenmistir.




# 6. Use Allow and Deny directives to restrict access to directories
# 7. Use mod_security and mod_evasive modules to secure Apache
# 8. Disable Apache's following of symbolic links
# 9. Turn off server side includes and CGI Execution
# 10. Limit request size
# 11. Protect against DDOS attacks
# 12. Enable Apache logging
# 13. Secure Apache with SSL Certificates
# Web Application Security
## Cookies
## xss protection

# Dynamic Content Security
## CGI 

