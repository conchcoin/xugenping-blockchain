# Python Blockchain Implementation

这是一个基于Python的区块链实现，包含以下功能：

- POW挖矿
- 钱包管理
- 命令行工具
- 区块和交易验证
- Web API接口

## 安装

1. 克隆仓库：
```bash
git clone <repository-url>
cd blockchain
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行工具

1. 初始化区块链：
```bash
python -m blockchain.cli.cli init
```

2. 查看余额：
```bash
python -m blockchain.cli.cli balance
```

3. 发送交易：
```bash
python -m blockchain.cli.cli send <recipient-address> <amount>
```

4. 开始挖矿：
```bash
python -m blockchain.cli.cli mine
```

### Web API

启动Web服务器：
```bash
python -m blockchain.web.app
```

API端点：
- GET /api/blockchain - 获取区块链信息
- GET /api/wallet - 获取钱包信息
- GET /api/balance - 获取余额
- POST /api/transaction - 创建新交易
- POST /api/mine - 开始挖矿
- POST /api/mine/stop - 停止挖矿
- GET /api/mine/status - 获取挖矿状态

## 项目结构

```
blockchain/
├── core/
│   ├── block.py
│   └── blockchain.py
├── wallet/
│   └── wallet.py
├── miner/
│   └── miner.py
├── cli/
│   └── cli.py
├── web/
│   └── app.py
├── contracts/
├── tests/
├── requirements.txt
└── README.md
```

## 功能特点

1. 工作量证明（POW）挖矿
2. RSA加密钱包
3. 交易签名和验证
4. 区块链数据持久化
5. RESTful API接口
6. 命令行工具

## 开发

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装开发依赖：
```bash
pip install -r requirements.txt
```

3. 运行测试：
```bash
pytest
```

## 许可证

MIT 