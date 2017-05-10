# sinalogin
use python to login in sina
    微博在pc端的登陆时，不是简单的向服务器发送账号密码，同时服务器返回账号密码是否正确的信息。通过对登陆时的抓包分析，我们发现微博登陆需要在客户端用javascript预先对账号密码进行了加密，然后再post指定数据到新浪服务器。其登陆逻辑包含两个方面：预登录和正式登陆。预登录主要是为了获取正式登陆时需要用到的账号密码加密信息，这些信息包含在成功预登录后的多个属性值里。同时预登录还包含了正式登陆需要发送的key值。

预登录的作用主要包含以下几点：

    l  获取客户端对用户账号密码的加密参数。

    l  判断是否需要输入验证码，如果需要，还会存有包含获取验证码url需要的pcid值。

    l  正式登陆时需要post的数据。

预登录链接：http://login.sina.com.cn/sso/prelogin.php​，预登录时，需要对请求进行模拟。

       头信息——模拟浏览器访问，需要模拟的头信息有：host（访问的服务器主机），user-agent（用户代理，新浪微博会根据user-agent来判断用户来自pc端还是移动端），referer（指定网页不能访问时跳转的页面）

    l  host: login.sina.com.cn

    l  user-agent可以使用浏览器的用户代理

    l  referer:http://weibo.com/?c=spr_web_sq_kings_weibo_t001

post数据——entry​（入口），callback（回调函数），su（加密后的用户账号，加密方式为：先转为unicode编码，base64编码。），mod（加密方式），checkpin（判断是否需要验证码登陆），client（登陆的客户端）

    l  entry: weibo,​

    l  callback:sinaSSOController.preloginCallBack,

    l  rsakt: mod,

    l  checkpin: 1,

    l  client: ssologin.js(v1.4.18)

预登录的时候，能返回以下信息，说明预登录成功：pubkey​，servertime, nonce, rsakv, pcid, showpin

正式登陆的主要是为了验证登陆密码，如果登陆时需要验证码，服务器会验证其准确性。以下为主要实现细节。

头信息的伪装（可以只需要伪装user-agent）。

post数据有很多，有几项是固定的，有几项是从预登录中获取的。从预登录中获取的数据有：servertime，nonce，rsakv。还有加密后的账号密码。如果预登录中返回的数据中showpin为1，表明需要输入验证码才能登陆，此时根据预登录返回的pcid，来获取验证码。

加密账号的方式为：先使用​python模块中的urllib.quote处理，再使用base64加密。使用quote进行加密是为了对账号进行消除歧义字符。密码的加密方式为：先创建一个RSA加密公钥，公钥的两个参数新浪微博都给了固定值，不过给的都是16进制的字符串，需要进行转化进制后才能使用，第一个是预登录成功后返回的pubkey，第二个是js加密文件中的“10001”即“65537”，在加密过程中还使用到了预登录时获取的servertime和nonce值。

验证码的获取链接：

http://login.sina.com.cn/cgi/pin.php?p="+pcid+"&r="+ random_number + "&s=0"

向服务器post数据后，会返回location.replace（"..."）内容，返回的retcode值为0，说明登陆成功。如果retcode=101表明登陆失败。成功模拟登陆后，locationlocation.replace中的url即为下一步需要访问的url，使用get方法向服务器访问该url，保存这次登陆的cookie信息，爬取数据时，加入获取到的cookie即可以访问相关微博页面。

