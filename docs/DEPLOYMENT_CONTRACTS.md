# MediLedger Nexus Smart Contracts Deployment Guide

This guide provides step-by-step instructions for deploying the MediLedger Nexus smart contracts to Hedera Hashgraph.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Contract Compilation](#contract-compilation)
4. [Testing](#testing)
5. [Deployment to Hedera Testnet](#deployment-to-hedera-testnet)
6. [Deployment to Hedera Mainnet](#deployment-to-hedera-mainnet)
7. [Contract Verification](#contract-verification)
8. [Integration with Backend](#integration-with-backend)
9. [Monitoring & Maintenance](#monitoring--maintenance)
10. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- Node.js 18+
- Foundry (Forge, Cast, Anvil)
- Git
- Hedera account with HBAR for deployment

### Accounts & Services
- Hedera Testnet account (for testing)
- Hedera Mainnet account (for production)
- Hedera Developer Portal access
- IPFS/Arweave account (for metadata storage)

## Environment Setup

### 1. Install Foundry
```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
source ~/.bashrc  # or restart terminal
foundryup

# Verify installation
forge --version
cast --version
anvil --version
```

### 2. Clone Repository
```bash
git clone https://github.com/your-org/mediledger-nexus.git
cd mediledger-nexus/contracts
```

### 3. Install Dependencies
```bash
# Initialize git repository (if not already done)
git init

# Install forge-std
forge install forge-std

# Install additional dependencies
forge install OpenZeppelin/openzeppelin-contracts
```

### 4. Environment Configuration
Create a `.env` file in the contracts directory:

```bash
# Hedera Configuration
HEDERA_NETWORK=testnet
HEDERA_ACCOUNT_ID=0.0.123456
HEDERA_PRIVATE_KEY=your_private_key_here
HEDERA_OPERATOR_ID=0.0.123456
HEDERA_OPERATOR_KEY=your_operator_key_here

# Deployment Configuration
DEPLOYMENT_GAS_LIMIT=1000000
DEPLOYMENT_GAS_PRICE=1000000000

# Contract Addresses (will be populated after deployment)
HEALTH_VAULT_CONTRACT=
CONSENT_MANAGER_CONTRACT=
RESEARCH_STUDY_CONTRACT=
EMERGENCY_ACCESS_CONTRACT=

# IPFS Configuration (optional)
IPFS_GATEWAY=https://ipfs.io/ipfs/
ARWEAVE_GATEWAY=https://arweave.net/
```

## Contract Compilation

### 1. Compile Contracts
```bash
# Compile all contracts
forge build

# Compile specific contract
forge build --contracts HealthVault

# Compile with optimization
forge build --optimize --optimizer-runs 200
```

### 2. Verify Compilation
```bash
# Check compilation output
ls -la out/

# Verify contract artifacts
forge build --sizes
```

### 3. Generate Documentation
```bash
# Generate NatSpec documentation
forge doc

# Serve documentation locally
forge doc --serve
```

## Testing

### 1. Run All Tests
```bash
# Run all tests
forge test

# Run tests with verbose output
forge test -vv

# Run specific test file
forge test --match-path test/TestHealthVault.sol

# Run tests with gas reporting
forge test --gas-report
```

### 2. Run Individual Test Suites
```bash
# Health Vault tests
forge test --match-contract TestHealthVault -vv

# Consent Manager tests
forge test --match-contract TestConsentManager -vv

# Research Study tests
forge test --match-contract TestResearchStudy -vv

# Emergency Access tests
forge test --match-contract TestEmergencyAccess -vv
```

### 3. Test Coverage
```bash
# Generate test coverage report
forge coverage

# Generate detailed coverage report
forge coverage --report lcov
```

### 4. Gas Optimization
```bash
# Analyze gas usage
forge test --gas-report

# Optimize contracts
forge build --optimize --optimizer-runs 1000
```

## Deployment to Hedera Testnet

### 1. Prepare Deployment Script
Create `script/Deploy.s.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Script.sol";
import "../src/HealthVault.sol";
import "../src/ConsentManager.sol";
import "../src/ResearchStudy.sol";
import "../src/EmergencyAccess.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("HEDERA_PRIVATE_KEY");
        address deployer = vm.addr(deployerPrivateKey);
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy HealthVault contract
        HealthVault healthVault = new HealthVault(
            deployer,
            "MediLedger Health Vault",
            true,  // encryptionEnabled
            true,  // zkProofsEnabled
            "high", // privacyLevel
            new string[](0) // dataTypes
        );
        
        // Deploy ConsentManager contract
        ConsentManager consentManager = new ConsentManager();
        
        // Deploy ResearchStudy contract
        ResearchStudy researchStudy = new ResearchStudy();
        
        // Deploy EmergencyAccess contract
        EmergencyAccess emergencyAccess = new EmergencyAccess();
        
        vm.stopBroadcast();
        
        // Log deployment addresses
        console.log("HealthVault deployed at:", address(healthVault));
        console.log("ConsentManager deployed at:", address(consentManager));
        console.log("ResearchStudy deployed at:", address(researchStudy));
        console.log("EmergencyAccess deployed at:", address(emergencyAccess));
    }
}
```

### 2. Deploy to Testnet
```bash
# Deploy to Hedera Testnet
forge script script/Deploy.s.sol --rpc-url hedera-testnet --broadcast --verify

# Deploy with specific gas settings
forge script script/Deploy.s.sol \
    --rpc-url hedera-testnet \
    --broadcast \
    --verify \
    --gas-limit 1000000 \
    --gas-price 1000000000
```

### 3. Verify Deployment
```bash
# Check deployment status
cast call <CONTRACT_ADDRESS> "owner()" --rpc-url hedera-testnet

# Verify contract code
cast code <CONTRACT_ADDRESS> --rpc-url hedera-testnet
```

### 4. Update Environment Variables
After successful deployment, update your `.env` file with the deployed contract addresses:

```bash
HEALTH_VAULT_CONTRACT=0.0.1234567
CONSENT_MANAGER_CONTRACT=0.0.1234568
RESEARCH_STUDY_CONTRACT=0.0.1234569
EMERGENCY_ACCESS_CONTRACT=0.0.1234570
```

## Deployment to Hedera Mainnet

### 1. Pre-deployment Checklist
- [ ] All tests passing
- [ ] Security audit completed
- [ ] Gas optimization verified
- [ ] Contract addresses documented
- [ ] Backup deployment plan ready

### 2. Deploy to Mainnet
```bash
# Deploy to Hedera Mainnet
forge script script/Deploy.s.sol --rpc-url hedera-mainnet --broadcast --verify

# Deploy with higher gas limit for mainnet
forge script script/Deploy.s.sol \
    --rpc-url hedera-mainnet \
    --broadcast \
    --verify \
    --gas-limit 2000000 \
    --gas-price 2000000000
```

### 3. Post-deployment Verification
```bash
# Verify all contracts are deployed correctly
cast call <HEALTH_VAULT_ADDRESS> "owner()" --rpc-url hedera-mainnet
cast call <CONSENT_MANAGER_ADDRESS> "owner()" --rpc-url hedera-mainnet
cast call <RESEARCH_STUDY_ADDRESS> "owner()" --rpc-url hedera-mainnet
cast call <EMERGENCY_ACCESS_ADDRESS> "owner()" --rpc-url hedera-mainnet
```

## Contract Verification

### 1. Verify on Hedera Explorer
```bash
# Verify contract source code
cast verify-contract <CONTRACT_ADDRESS> \
    --chain-id hedera-mainnet \
    --etherscan-api-key <API_KEY> \
    --constructor-args $(cast abi-encode "constructor(address,string,bool,bool,string,string[])" \
        <OWNER_ADDRESS> \
        "MediLedger Health Vault" \
        true \
        true \
        "high" \
        "[]")
```

### 2. Verify Contract Functions
```bash
# Test basic contract functions
cast call <HEALTH_VAULT_ADDRESS> "getVaultInfo()" --rpc-url hedera-mainnet
cast call <CONSENT_MANAGER_ADDRESS> "getConsentCount()" --rpc-url hedera-mainnet
```

## Integration with Backend

### 1. Update Backend Configuration
Update the backend's environment variables with the deployed contract addresses:

```bash
# Backend .env file
HEALTH_VAULT_CONTRACT=0.0.1234567
CONSENT_CONTRACT=0.0.1234568
RESEARCH_CONTRACT=0.0.1234569
EMERGENCY_CONTRACT=0.0.1234570
```

### 2. Test Backend Integration
```bash
# Test contract interaction from backend
cd ../backend
python -c "
from src.mediledger_nexus.blockchain.smart_contracts import SmartContractService
service = SmartContractService()
print('Contract addresses loaded:', service.health_vault_contract)
"
```

### 3. Deploy Backend with Contract Integration
```bash
# Deploy backend with updated contract addresses
# Follow the backend deployment guide
```

## Monitoring & Maintenance

### 1. Contract Monitoring
```bash
# Monitor contract events
cast logs --from-block latest --address <CONTRACT_ADDRESS> --rpc-url hedera-mainnet

# Monitor contract balance
cast balance <CONTRACT_ADDRESS> --rpc-url hedera-mainnet
```

### 2. Event Monitoring
Set up monitoring for important contract events:

```bash
# Health Vault events
cast logs --topic 0x1234567890abcdef... --rpc-url hedera-mainnet

# Consent Manager events
cast logs --topic 0xabcdef1234567890... --rpc-url hedera-mainnet
```

### 3. Regular Maintenance
- Monitor contract gas usage
- Check for failed transactions
- Update contract documentation
- Review access permissions

## Troubleshooting

### Common Issues

#### 1. Compilation Errors
```bash
# Check Solidity version compatibility
forge build --force

# Update dependencies
forge update

# Clean build cache
forge clean
```

#### 2. Deployment Failures
```bash
# Check account balance
cast balance <ACCOUNT_ADDRESS> --rpc-url hedera-testnet

# Check gas estimation
cast estimate <CONTRACT_ADDRESS> "functionName()" --rpc-url hedera-testnet

# Check network connectivity
cast block-number --rpc-url hedera-testnet
```

#### 3. Contract Interaction Issues
```bash
# Check contract state
cast call <CONTRACT_ADDRESS> "functionName()" --rpc-url hedera-testnet

# Check transaction status
cast tx <TX_HASH> --rpc-url hedera-testnet

# Check contract events
cast logs --address <CONTRACT_ADDRESS> --rpc-url hedera-testnet
```

### Debugging Tools

#### 1. Local Testing
```bash
# Start local Anvil node
anvil

# Deploy to local node
forge script script/Deploy.s.sol --rpc-url http://localhost:8545 --broadcast
```

#### 2. Gas Analysis
```bash
# Analyze gas usage
forge test --gas-report

# Optimize gas usage
forge build --optimize --optimizer-runs 1000
```

#### 3. Security Analysis
```bash
# Run security checks
forge test --match-test testSecurity

# Check for common vulnerabilities
slither .
```

## Security Considerations

### 1. Private Key Management
- Never commit private keys to version control
- Use hardware wallets for mainnet deployments
- Implement key rotation policies

### 2. Contract Security
- Conduct security audits before mainnet deployment
- Use established libraries (OpenZeppelin)
- Implement access controls and pausable functions

### 3. Network Security
- Use HTTPS for all API calls
- Implement rate limiting
- Monitor for suspicious activity

## Best Practices

### 1. Development
- Write comprehensive tests
- Use consistent coding standards
- Document all functions and events

### 2. Deployment
- Test on testnet first
- Use deterministic deployment
- Keep deployment records

### 3. Maintenance
- Monitor contract activity
- Update dependencies regularly
- Plan for contract upgrades

## Support

For deployment issues:
1. Check the logs first
2. Verify network connectivity
3. Check account balances
4. Review contract state
5. Contact Hedera support

## Next Steps

After successful deployment:
1. Set up monitoring and alerting
2. Implement automated testing
3. Plan for contract upgrades
4. Set up disaster recovery
5. Document operational procedures
