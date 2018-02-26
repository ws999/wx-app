API DOCUMENT
****
**note**
>1. request in form style;
>2. 所有需要登录认证的请求都必须在URL中额外携带token参数;token通过login接口获取
>3. response json style:
  >>- code: 0
  >>- msg: ':)'
  >>- data: { }
****
## /wx-app/api/user/login 用户登录
  - login_required: false
  - methods: POST
  - parameters
  >- code
  - return data json
  >- user:
  >>- _id
  >>- open_id
  >>- union_id
  >>- nickname
  >>- ...
  >- cookie:
  >>- weappsid
  >>- expires
****
## /wx-app/api/user/info 用户基本信息
  - login_required: true
  - methods: GET
  - none parameters
  - return data json
  >- user:
  >>- nickname
  >>- capital: -float, 账户余额-
  >>- ...
****
## /wx-app/api/user/info_set 更新信息(每次登录)
  - login_required: true
  - methods: POST
  - parameters
  >- nickname
  >- avatar
  >- gender
  >- province
  >- city
  >- intro
  - return data json
  >- user:
  >>- _id
  >>- open_id
  >>- union_id
  >>- nickname
  >>- ...
****
## /wx-app/api/user/capital 账户余额
  - login_required: true
  - methods: GET
  - none parameters
  - return data json
  >- capital: 100.0 -float, 元-
****
## /wx-app/api/user/capital_log 账单
  - login_required: true
  - methods: GET
  - parameters
  >- per_page:
  >- page:
  - return data json
  >- total: 10 -int, 总页数-
  >- page: 1 -int, 当前页码-
  >- result: -list, 变动记录列表-
****
  ## /wx-app/api/img/upload 上传图片
    - login_required: false
    - methods: POST
    - parameters
    >- type: -redpacket-
    - return img json
****
## /wx-app/api/redpacket/create 创建红包
  - login_required: true
  - methods: POST
  - parameters
  >- amount: float, 红包总金额, 元-
  >- number: -int, 红包总数量-
  >- title: -str, 标题-
  >- level -int-
  - return data json
  >- _id: -str, 红包id-
  >- amount: -float, 红包总金额-
  >- count: -int, 红包总数量-
  >- left_count: -int, 红包剩余数量-
  >- title: -str, 标题-
  >- level: -int-
  >- expire_time: -过期时间-
  >- ...
****
## /wx-app/api/img/wxqr/create 生成分享页(创建成功后调取)
  - login_required: false
  - methods: GET
  - parammeters
  >- redpacket_id: 红包_id
  >- shape: circle - 目前仅支持圆形 -
  - return img data
  >- ...
****
## /wx-app/api/img/wxqr/blend 生成分享页完整图片(必须先生成分享页)
  - login_required: false
  - methods: GET
  - parammeters
  >- redpacket_id: 红包_id
  - return img data
  >- ...
****
## /wx-app/api/redpacket/\<redpacket_id>/detail 红包详情
  - login_required: true
  - methods: GET
  - parameters
  >- per_page:
  >- page:
  - return data json
  >- total: 10 -int, 总页数-
  >- page: 1 -int, 当前页码-
  >- redpacketlog: -list, 领取记录列表-
  >- redpacket: -dict, 红包详情-
  >>-  could_collect: true -bool, 是否还未被领完-
  >>- has_collect: true -bool, 当前用户是否已领取, 未登录为false-
  >>- amount: -float, 红包总金额(元)-
  >>- count: -int, 红包总数量-
  >>- left_count: -int, 红包剩余数量-
  >>- title: -str, 标题-
  >>- poster
  >>- user_nickname
  >>- user_avatar
****
## /wx-app/api/redpacket/\<redpacket_id>/collect 领取红包(挑战成功)
  - login_required: true
  - methods: POST
  - parameters
  >- redpacket_id - 在url链接中 -
  - return data json
  >- value: 100.0 -float, 元-
****
## /wx-app/api/redpacket/\<redpacket_id>/fail_report 挑战失败报告
- login_required: true
- methods: POST
- parameters
>- redpacket_id - 在url链接中 -
- return data json
>- {}
****
## /wx-app/api/user/rp_out_log 个人红包发放记录
  - login_required: true
  - methods: GET
  - parameters
  >- per_page:
  >- page:
  - return data json
  >- total: 10 -int, 总页数-
  >- page: 1 -int, 当前页码-
  >- rp_out_log: -list, 发放记录列表-
  >- count: -总数量-
  >- amount_total: -总金额-
****
## /wx-app/api/user/rp_in_log 个人红包领取记录
  - login_required: true
  - methods: GET
  - parameters
  >- per_page:
  >- page:
  - return data json
  >- total: 10 -int, 总页数-
  >- page: 1 -int, 当前页码-
  >- rp_in_log: -list, 领取记录列表-
  >- count: -总数量-
  >- amount_total: -总金额-
****
## /wx-app/api/order/pay/create 异步, 创建充值订单, 返回异步请求所需参数
  - login_required: true
  - methods: POST
  - parammeters
  >- product_type: -int, 1为充值进红包账户余额-
  >- pay_type: -int, 0为微信支付, 与product_type不相等-
  >- amount: -充值金额, 不包含手续费-
  - return data json
  >- order_no: -str-
  >- wxpay_jsapi_args: -str-
****
## /wx-app/api/order/transfer/request 同步, 创建提现订单并请求, 直接返回提现结果
  - login_required: true
  - methods: POST
  - parammeters
  >- product_type: -int, 0为提现到微信账户-
  >- pay_type: -int, 1为红包余额提现, 与product_type不相等-
  >- amount: - 提现金额(元) -
  - return data json
  >- order_no: -str-
  >- status: SUCCESS -str-
****
## /wx-app/api/order/\<order_no>/status 查询订单状态
  - login_required: true
  - methods: GET
  - parameters
  >- order_no: 订单号
  >- pay_type:0,1 -int, 0微信支付, 1红包提现-
  - return data json
  >- status: 0 -int, -pay_type=0时 {0:未支付, 1:已支付}; pay_type=1时 {0:提现失败,1:提现成功}-
****
