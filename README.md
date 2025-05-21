# Xugenping (XGP) 区块链系统

Xugenping是一个基于Python的区块链系统，支持智能合约、P2P网络、PBFT共识机制等功能。

## 系统要求

- Python 3.8+
- pip (Python包管理器)
- 操作系统：Windows/Linux/MacOS

## 安装步骤

1. 克隆项目代码：
```bash
git clone <repository_url>
cd blockchain
```

2. 创建并激活虚拟环境（推荐）：
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. 安装依赖包：
```bash
pip install -r requirements.txt
```

## 配置说明

1. 区块链配置
- 代币名称：Xugenping (XGP)
- 总发行量：19,840,228 XGP
- 初始区块奖励：50 XGP
- 减半周期：6个月
- 区块时间：10分钟

2. 智能合约配置
- 最小Gas价格：0.00001 XGP
- 最大Gas价格：0.001 XGP
- 默认Gas价格：0.0001 XGP
- 合约部署基础费用：1.0 XGP

## 运行说明

1. 初始化区块链：
```bash
python -m blockchain.cli.cli init
```

2. 启动Web服务器：
```bash
python -m blockchain.web.app
```
服务器将在 http://localhost:5000 启动

## API接口说明

### 区块链接口
- GET `/api/blockchain` - 获取区块链信息
- GET `/api/wallet` - 获取钱包信息
- GET `/api/balance` - 查询余额
- POST `/api/transaction` - 创建交易
- POST `/api/mine` - 开始挖矿
- POST `/api/mine/stop` - 停止挖矿
- GET `/api/mine/status` - 获取挖矿状态

### 智能合约接口
- POST `/api/contracts/deploy` - 部署合约
- POST `/api/contracts/execute/<contract_address>` - 执行合约
- GET `/api/contracts/state/<contract_address>` - 获取合约状态
- GET `/api/contracts/info/<contract_address>` - 获取合约信息
- POST `/api/contracts/estimate-gas` - 估算gas费用

## 使用示例

1. 部署智能合约：
```bash
curl -X POST http://localhost:5000/api/contracts/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyContract",
    "code": "0x600160015500",
    "creator": "0x123...",
    "gas_price": 0.0001
  }'
```

2. 执行合约：
```bash
curl -X POST http://localhost:5000/api/contracts/execute/0x123... \
  -H "Content-Type: application/json" \
  -d '{
    "input_data": "0x123...",
    "gas_price": 0.0001
  }'
```

3. 创建交易：
```bash
curl -X POST http://localhost:5000/api/transaction \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "0x456...",
    "amount": 100
  }'
```

## 目录结构
```
blockchain/
├── api/                # API接口
├── config/            # 配置文件
├── consensus/         # 共识机制
├── contracts/         # 智能合约
├── core/             # 核心功能
├── miner/            # 挖矿相关
├── network/          # P2P网络
├── security/         # 安全相关
├── web/              # Web服务
└── cli/              # 命令行工具
```

## 常见问题

1. 端口占用
如果5000端口被占用，可以修改 `blockchain/web/app.py` 中的端口号：
```python
app.run(host='0.0.0.0', port=5001)  # 修改为其他端口
```

2. 依赖安装失败
如果安装依赖时遇到问题，可以尝试：
```bash
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

3. 权限问题
在Linux/MacOS上可能需要使用sudo：
```bash
sudo pip install -r requirements.txt
```

## 安全说明

1. 私钥安全
- 请妥善保管钱包私钥
- 不要将私钥文件上传到公共仓库
- 定期备份钱包文件

2. 网络安全
- 建议在防火墙后运行节点
- 使用HTTPS进行API调用
- 定期更新系统和依赖包

## 开发说明

1. 添加新功能
- 在相应目录下创建新模块
- 更新requirements.txt添加新依赖
- 编写单元测试
- 更新文档

2. 运行测试
```bash
pytest tests/
```

## 许可证

MIT License

## 联系方式

如有问题，请提交Issue或联系开发团队。 