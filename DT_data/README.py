
### 一、销售额= 当日定价商品销售额(当日定价*当日销量)
    当日定价：MySQL中wrk_comweb_hour_price表, price字段
    时间范围：2015-12-25 —— 今(2016-12-19)
    商品数量：904
    价格异常：7665/264438
    当日销量：SQLServer中TB_Inf_Map_OrderProducts表, Amount字段求和
    1.获取当日定价
    2.补全当日定价丢失数据(取该时间当前时间左右各10天的数据补全, 如果还为0, 舍弃该组数据)
    3.获取当日该商品销量(验证订单是否取消)
    4.计算销售额
    --------------------------------------------------------
### 二、毛利率= 当日定价商品毛利率((当日定价-采购价)/采购价)
    采购价：SQLServer中TB_Inf_Map_Product表, PurchasePrice字段
    --------------------------------------------------------
### 三、毛利= 当日定价商品毛利额（销售额*毛利率）
    --------------------------------------------------------
### 四、定价差= 健客价-市场次低价
    1.市场次低价：从bas_comweb_url表中找到健客该商品对应竞争对手的商品编号，从wrk_comweb_hour_price表中查出健客商品和竞争对手商品当天
        次低价(补全价格为0异常数据, 如果还为0, 舍弃商品价格)
    2.补全价格
    3.将健客价和竞争对手价格存入数组并去零、去重、排序
    4.如果数组长度大于等于2, 取第二位作为次低价；如果长度等于1，取第一位；长度为0，次低价为0
    ②价差比=（健客价-市场次低价）/市场次低价
    *入库(tb_deloitte_price_data)字段：
        产品id(prod_code)、当日定价(price)、当日销量(sale_num)、当日销售额(sales_volume)、采购价(market_price)、
        毛利率(gross_margin)、毛利(gross_profit)、当天次低价(low_price)、定价差(price_diff)、价差比(price_diff_ratio)、
        当日日期(date_time)、入库日期(collect_time)
    --------------------------------------------------------
### 五、价格敏感=（当次调价日均销量-上一价格日均销量）/调价价差
    (补全价格为0异常数据, 如果还为0, 不计当天天数)
    当次调价日均销量：当前价格至下一次调价之间总销量/天数
    上一价格日均销量：上一价格至当前价格之间总销量/天数
    1.获取该商品全量日期的价格数据
    2.补全数据
    3.获取价格变化时始末日期, 始末价格, 获取价格持续天数
    4.计算当前价格销量
    5.计算日均销量
    *入库(tb_deloitte_price_sensitive_pretreatment)价格敏感预处理表：
        产品id(prod_id)、当次价格(last_price)、调价后价格(now_price)、当次价格开始日期(start_date)、当次价格结束日期(end_date)、价格持续天数(diff_days)、当次价格总销量(sales_volume)、当此价格日平均销量(average_sales_volume)
    (tb_deloitte_price_sensitive)价格敏感表：
        产品id(prod_id)、上一价格(last_price)、当次价格(now_price)、起始日期(start_date)、调价日期(end_date)、天数(diff_days)
    
    --------------------------------------------------------
### 六、价格变动
    ①变动比率= （当月均价-前三月均价）/前三月均价
    1.获取全量商品
    (补全价格为0异常数据, 如果还为0, 不计当天价格和天数)
    2.获取商品当月和前三个月价格
    3.获取商品当月价格数组, 计算当月均价
    4.获取商品前三个月价格数组, 计算前三个月均价
    5.计算变动比率
    *入库(tb_deloitte_market_price) 变动比率表:
        竞争对手id(comp_id)、产品id(prod_id)、当前月份(now_month)、
        当月均价(now_month_ave_price)、前三个月均价(three_month_ave_price)、
        变动比率(change_ratio)
    ②低价集中情况= 最低均价商品数/在监控商品总数
    1.获取全量健客商品
    2.获取健客商品对应的竞争对手商品
    3.获取并补全健客价格
    4.获取并补全竞争对手价格存入数组, 计算当天最小价格
    5.比较健客价和竞争对手最低价
    *入库(tb_deloitte_low_price_focus_pretreatment)低价集中预处理表:
        健客商品id(jk_id)、日期(date_time)、健客商品价格(jk_price)、竞争对手最低(comp_price_min)、
        健客价是否为最低价(jk_low_price)
    (tb_deloitte_low_price_focus)低价集中表:
    比较日期(date_time)、健客最低价数目(jk_low_price_num)、当日总数(all_count)、低价比率(low_price_per)
### 七、低价情况
    ①低价数量比例= 当月健客均价最低商品数/在监控商品总数
    1.获取健客商品
    2.获取当月健客该商品均价, 价格异常补全
    3.获取健客商品对应竞争商家商品
    4.获取竞争对手当月该商品均价, 返回当月均价数组
    5.补全并去除均价数组内0价格
    6.判断健客价是否为最低价
    *入库(tb_mk_dt_lowprice_num_mon_tmp)低价数量预处理表:
        健客id(jk_id), 健客月均价(jk_ave_price), 竞争对手月最低价(comp_low_price), 健客价是否为最低价(jk_low_price), 月份(date_time)
    (tb_shw_dt_lowprice_num_mon)低价数量表:
    月份(date_time), 健客低价数目(jk_low_price_num), 总数(all_count), 低价数量比例(low_price_num_per)
    ②低价销量比例= 当月健客均价最低商品数销售额/公司总销售额
    1.获取当月健客最低价商品id
    2.获取低价商品销售额
    3.获取本月总销售额
    *入库(tb_shw_dt_lowprice_sales_mon)低价销量表:
    月份(date_time), 低价商品销售额(sales_volume), 当月总销售额(all_sales_volume), 低价销量比例(low_price_ratio)
### 八、低价引流效果
    低价商品订单分析= 单一订单中健客最低价商品销售额/订单金额
    1.生成日期列表
    2.获取该日期低价商品id
    3.获取当日存在低价商品的订单号
    4.获取低价订单中商品
    5.计算低价产品销售额和订单总销售额
    *入库(tb_mk_dt_lowprice_drainage_day)低价引流表:
        当日日期(date_time), 订单号(order_code), 低价引流率(drainage), 低价商品销售额(low_price_sales), 订单总销售额(all_sales)
    """