<?php
/**********************************************************************
* Copyright (C) 2005-2016 All rights reserved.
* FILENAME: 	 useragent_digger.php
* VERSION: 		 1.0
* CREATED: 		 2016-05-07 16:17
* AUTHOR: 		 xuexiang
* DESCRIPTION: 
*
* HISTORY: 
**********************************************************************/
require_once 'Mobile_Detect.php';
error_reporting( E_ALL ^ E_NOTICE );


//ua='Mozilla/5.0(iPhone;U;CPUiPhoneOS3_0likeMacOSX;en-us)AppleWebKit/420.1(KHTML,likeGecko)Version/3.0Mobile/1A542aSafari/419.3'; 
$method = $argv[1];
$method = urldecode(substr($method, 3));

$detect = new Mobile_Detect( $method );
$dev_arr = [];
$os_arr = [];
$bro_arr = [];
$dev_ver = [];
$os_ver = [];
$bro_ver = [];
$cont_dev = array(

                // Build
                'Mobile',
                'Build',
                'Version',
                'VendorID',

                // Devices
                'iPad',
                'iPhone',
                'iPod',
                //'BlackBerry'    => array('BlackBerry[VER]', 'BlackBerry [VER];'),
                'Kindle'
            );
$cont_bro = array(
                // Browser
                'Chrome',
                'Coast',
                'Dolfin',
                // @reference: https://developer.mozilla.org/en-US/docs/User_Agent_Strings_Reference
                'Firefox',
                'Fennec',
                // @reference: http://msdn.microsoft.com/en-us/library/ms537503(v=vs.85).aspx
                'IE',
                // http://en.wikipedia.org/wiki/NetFront
                'NetFront',
                'NokiaBrowser',
                'Opera',
                'Opera Mini',
                'Opera Mobi',
                'UCBrowser',
                'MQQBrowser',
                'Mb2345Browser',
                'hao123',
                'QQBrowser',
                '2345Explorer',
                'LBBROWSER',
                'SE 2.X MetaSr',
                '360SE',
                'Maxthon',
                'MicroMessenger',
                // @note: Safari 7534.48.3 is actually Version 5.1.
                // @note: On BlackBerry the Version is overwriten by the OS.
                'Safari',
                'Skyfire',
                'Tizen',
#'Webkit',

                // Engine
#'Gecko',
                'Trident',
#'Presto',
                'IE'
            );
$cont_os = array(
               // OS
               'iOS',
               'Android',
               'BlackBerry',
               'BREW',
               'Java',
               // @reference: http://windowsteamblog.com/windows_phone/b/wpdev/archive/2011/08/29/introducing-the-ie9-on-windows-phone-mango-user-agent-string.aspx
               // @reference: http://en.wikipedia.org/wiki/Windows_NT#Releases
               'Windows Phone OS',
               'Windows Phone',
               'Windows CE',
               // http://social.msdn.microsoft.com/Forums/en-US/windowsdeveloperpreviewgeneral/thread/6be392da-4d2f-41b4-8354-8dcee20c85cd
               'Windows NT',
               'Symbian',
               'webOS',
               'Windows'
           );

//定义打印数组函数
function print_arr( $arr )
{
    foreach( $arr as $key => $val )
    {
        echo $key.':'.$val.' ';
    }
}
function print_arr_key( $arr )
{
    foreach( $arr as $key => $val )
    {
        echo $key.' ';
    }
}
function print_arr_val( $arr )
{
    foreach( $arr as $key => $val )
    {
        echo $val.' ';
    }
}

//输出设备类型
$deviceType = ( $detect->isMobile() ? ( $detect->isTablet() ? 'tablet' : 'phone' ) : 'computer' );
echo $deviceType.'##';

//判断设备型号
if ( $deviceType == 'phone' || $deviceType == 'tablet' )
{
    foreach( $detect->getPhoneDevices() as $name => $match )
    {
        $check = $detect-> {'is'.$name}();
        if ( $check )
        {
            $dev_arr[$name] = $check;
        }
    }
    foreach( $detect->getTabletDevices() as $name => $match )
    {
        $check = $detect-> {'is'.$name}();
        if ( $check )
        {
            $dev_arr[$name] = $check;
        }
    }
}
else
{
    $dev_arr['computer'] = 1;
}

//判断操作系统类型
foreach( $detect->getOperatingSystems() as $name => $regex )
{
    $check = $detect-> {'is'.$name}();
    if ( $check )
    {
        $os_arr[$name] = $check;
    }
}

//判断浏览器类型
foreach( $detect->getBrowsers() as $name => $match )
{
    $check = $detect-> {'is'.$name}();
    if ( $check )
    {
        $bro_arr[$name] = $check;
    }
}
//添加手机型号，只需向类库中$phoneDevices数组中添加即可
//判断设备、系统及浏览器的版本
foreach( $detect->getProperties() as $name => $match )
{
    $check = $detect->version( $name );
    if ( $check !== false and in_array( $name, $cont_dev ) )
    {
        $dev_ver[$name] = $check;
    }
    if ( $check !== false and in_array( $name, $cont_os ) )
    {
        $os_ver[$name] = $check;
    }
    if ( $check !== false and in_array( $name, $cont_bro ) )
    {
        $bro_ver[$name] = $check;
    }
}

//输出设备类型及型号
if ( $dev_arr == [] )
{
    $dev_arr = $dev_ver;
    print_arr_val( $dev_arr );
    echo '##';
}
else
{
    if ( array_key_exists( "iOS", $os_ver ) )
    {
        print_arr_key( $dev_arr );
        echo $dev_ver['Mobile'].'##';
    }
    else
    {
        print_arr_key( $dev_arr );
        print_arr_val( $dev_ver );
        echo '##';
    }
}

//输出系统类型及型号
if ( array_key_exists( "Android", $os_ver ) )
{
    echo 'Android:'.$os_ver['Android'].'##';
}
else if ( array_key_exists( "iOS", $os_ver ) )
{
    echo 'iOS:'.$os_ver['iOS'].'##';
}
else
{
    print_arr( $os_ver );
    echo '##';
}




//输出浏览器类型及型号
if ( array_key_exists( "UCBrowser", $bro_ver ) )
{
    echo "UCBrowser:".$bro_ver['UCBrowser'];
}
else if ( array_key_exists( "MQQBrowser", $bro_ver ) )
{
    echo "MQQBrowser:".$bro_ver['MQQBrowser'];
}
else if ( array_key_exists( "Mb2345Browser", $bro_ver ) )
{
    echo "Mb2345Browser:".$bro_ver['Mb2345Browser'];
}
else if ( array_key_exists( "hao123", $bro_ver ) )
{
    echo "hao123:".$bro_ver['hao123'];
}
else if ( array_key_exists( "QQBrowser", $bro_ver ) )
{
    echo "QQBrowser".":".$bro_ver['QQBrowser'];
}
else if ( array_key_exists( "2345Explorer", $bro_ver ) )
{
    echo "2345Explorer".":".$bro_ver['2345Explorer'];
}
else if ( array_key_exists( "LBBROWSER", $bro_arr ) )
{
    echo "LBBROWSER";
}
else if ( array_key_exists( "SE 2.X MetaSr", $bro_ver ) )
{
    echo "SE 2.X MetaSr".":".$bro_ver['SE 2.X MetaSr'];
}
else if ( array_key_exists( "360SE", $bro_arr ) )
{
    echo "360SE";
}
else if ( array_key_exists( "Maxthon", $bro_ver ) )
{
    echo "Maxthon".":".$bro_ver['Maxthon'];
}
else if ( array_key_exists( "IE", $bro_ver ) )
{
    echo "IE".":".$bro_ver['IE'];
}
else if ( array_key_exists( "Chrome", $bro_ver ) and array_key_exists( "Safari", $bro_ver ) )
{
    echo 'Chrome:'.$bro_ver['Chrome'];
}
else if ( array_key_exists( "iOS", $os_ver ) and array_key_exists( 'Safari', $bro_ver ) )
{
    echo "Safari:".$bro_ver['Safari'];
}
else if ( array_key_exists( "Opera Mobi", $bro_ver ) )
{
    echo "Opera Mobi:".$bro_ver['Opera Mobi'];
}
else
{
    print_arr( $bro_ver );
    //echo '##';
}

?>
