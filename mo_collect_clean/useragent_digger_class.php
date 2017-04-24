<?php
/**********************************************************************
* Copyright (C) 2005-2016 All rights reserved.
* FILENAME: 	 useragent_digger_class.php
* VERSION: 		 1.0
* CREATED: 		 2016-05-07 16:42
* AUTHOR: 		 xuexiang
* DESCRIPTION:
*
* HISTORY:
**********************************************************************/

require_once 'Mobile_Detect.php';
error_reporting( E_ALL ^ E_NOTICE );


//ua='Mozilla/5.0(iPhone;U;CPUiPhoneOS3_0likeMacOSX;en-us)AppleWebKit/420.1(KHTML,likeGecko)Version/3.0Mobile/1A542aSafari/419.3';
$param = $argv[1];
$user_agent = urldecode( substr( $param, 3 ) );


class useragent_digger_class
{
    private $m_detector;
    private $m_user_agent;

    //设备类型
    private $m_device_type;
    //设备品牌
    private $m_device_brand;
    //设备型号
    private $m_device_model;
    //浏览器类型
    private $m_browser_type;


    public function get_detect( $ua )
    {
        $this->m_user_agent = $ua;
        $this->m_detector =  new Mobile_Detect( $ua );

        //获取设备信息
        $device_arr = $this->get_device_info();
        $this->m_device_type = $device_arr[0];
        $this->m_device_brand = $device_arr[1];

        //获取浏览器
        $this->m_browser_type = $this->get_browser_info();

        //获取
        $param_arr = $this->get_version_info();


        echo "$this->m_device_type, $this->m_device_brand, $param_arr[0], $param_arr[1] || $this->m_browser_type:$param_arr[2]";
    }

    /**
     * 获取设备信息：类型和型号
     *
     * @param 空
     * @return 设务类型
     */
    protected function get_device_info()
    {
        //设备类型
        $deviceType = "computer";
        //设备型号
        $deviceBrand = "";

        //分析：设备类型
        if ( $this->m_detector->isMobile() )
        {
            if ( $this->m_detector->isTablet() )
            {
                $deviceType = "tablet";
            }
            else
            {
                $deviceType = "phone";
            }

            //分析：设备型号
            if ( $deviceType == 'phone' || $deviceType == 'tablet' )
            {
                foreach( $this->m_detector->getPhoneDevices() as $name => $match )
                {
                    $check = $this->m_detector-> {'is'.$name}();
                    if ( $check )
                    {
                        $deviceBrand = $name;
                        break;
                    }
                }

                foreach( $this->m_detector->getTabletDevices() as $name => $match )
                {
                    $check = $this->m_detector-> {'is'.$name}();
                    if ( $check )
                    {
                        $deviceBrand = $name;
                        break;
                    }
                }
            }
        }

        return array( $deviceType, $deviceBrand );
    }

    /**
     * 获取操作系统类型
     *
     * @param 空
     * @return OS类型
     */
    protected function get_os_type()
    {
        foreach( $this->m_detector->getOperatingSystems() as $name => $regex )
        {
            $check = $this->m_detector-> {'is'.$name}();
            if ( $check )
            {
                $os_arr[$name] = $check;
            }
        }
    }


    /**
     * 获取浏览器信息
     *
     * @param
     * @return
     */
    public function get_browser_info()
    {
        $browser_type = "";

        //先使用正则匹配: 多个则取第一个
        $ma_ret = array();
        $num = preg_match( '/\w{1,10}Browser/', $m_user_agent, $ma_ret );
        if ( $num > 0 )
        {
            $browser_type = $ma_ret[0];
        }


        foreach( $this->m_detector->getBrowsers() as $name => $match )
        {
            $check = $this->m_detector-> {'is'.$name}();
            if ( $check )
            {
                $browser_type = $name;
                break;
            }
        }

        return $browser_type;
    }

    /**
     * 获取参数
     *
     * @param
     * @return
     */
    protected function get_version_info()
    {
        $deviceParam = "";
        $osParam = "";
        $browseParam = "";

        foreach( $this->m_detector->getProperties() as $name => $match )
        {
            $check = $this->m_detector->version( $name );
            if ( $check !== false )
            {
                if ( $name == $this->m_device_brand )
                {
                    $osParam = $check;
                }
                else if ( $name == $this->m_browser_type)
                {
                    $browseParam = $check;
                }

            }
    }

              return array( $deviceParam, $osParam, $browseParam );
    }


};


//应用
$app = new useragent_digger_class();
echo $app->get_detect( $user_agent );


?>

