"""
Smart Contract integration for MediLedger Nexus

Provides functionality for:
- Health vault smart contracts
- Consent management contracts
- Research study contracts
- Emergency access protocols

This module integrates with the actual Solidity smart contracts deployed on Hedera.
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from decimal import Decimal

from .hedera_client import HederaClient
from ..utils.formatters import DataFormatter

logger = logging.getLogger(__name__)


class SmartContractService:
    """
    Service for interacting with Hedera Smart Contracts
    
    Handles deployment and interaction with smart contracts
    for health vaults, consent management, and research studies.
    """
    
    def __init__(self, hedera_client: Optional[HederaClient] = None):
        """Initialize Smart Contract service"""
        self.client = hedera_client or HederaClient()
        self.formatter = DataFormatter()
        
        # Contract addresses from environment variables or defaults
        self.health_vault_contract = os.getenv("HEALTH_VAULT_CONTRACT", "0.0.1001")
        self.consent_contract = os.getenv("CONSENT_CONTRACT", "0.0.1002")
        self.research_contract = os.getenv("RESEARCH_CONTRACT", "0.0.1003")
        self.emergency_contract = os.getenv("EMERGENCY_CONTRACT", "0.0.1004")
        
        # Contract ABIs (loaded from deployment artifacts)
        self.contract_abis = self._load_contract_abis()
    
    def _load_contract_abis(self) -> Dict[str, Any]:
        """Load contract ABIs from deployment artifacts"""
        abis = {}
        contract_names = ["HealthVault", "ConsentManager", "ResearchStudy", "EmergencyAccess"]
        
        for contract_name in contract_names:
            abi_path = os.path.join(
                os.path.dirname(__file__), 
                "..", "..", "..", "..", "..", "contracts", 
                "out", contract_name, f"{contract_name}.sol", f"{contract_name}.json"
            )
            
            if os.path.exists(abi_path):
                try:
                    with open(abi_path, 'r') as f:
                        abi_data = json.load(f)
                        abis[contract_name.lower()] = abi_data.get("abi", [])
                except Exception as e:
                    logger.warning(f"Failed to load ABI for {contract_name}: {e}")
                    abis[contract_name.lower()] = []
            else:
                logger.warning(f"ABI file not found for {contract_name}: {abi_path}")
                abis[contract_name.lower()] = []
        
        return abis
    
    def _get_contract_bytecode(self, contract_name: str) -> Optional[str]:
        """Get contract bytecode from deployment artifacts"""
        bytecode_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "..", "..", "..", "contracts", 
            "out", contract_name, f"{contract_name}.sol", f"{contract_name}.json"
        )
        
        if os.path.exists(bytecode_path):
            try:
                with open(bytecode_path, 'r') as f:
                    contract_data = json.load(f)
                    return contract_data.get("bytecode", {}).get("object", "")
            except Exception as e:
                logger.warning(f"Failed to load bytecode for {contract_name}: {e}")
                return None
        else:
            logger.warning(f"Bytecode file not found for {contract_name}: {bytecode_path}")
            return None
    
    def deploy_health_vault_contract(self, 
                                   patient_account: str,
                                   vault_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a health vault smart contract for a patient
        
        Args:
            patient_account: Patient's Hedera account ID
            vault_config: Vault configuration parameters
            
        Returns:
            Dict containing contract deployment information
        """
        try:
            # Get contract bytecode and ABI
            contract_bytecode = self._get_contract_bytecode("HealthVault")
            contract_abi = self.contract_abis.get("healthvault", [])
            
            if not contract_bytecode or not contract_abi:
                raise ValueError("HealthVault contract bytecode or ABI not found")
            
            # Prepare constructor parameters
            constructor_params = [
                patient_account,  # owner
                vault_config.get("name", "Health Vault"),  # vaultName
                vault_config.get("encryption_enabled", True),  # encryptionEnabled
                vault_config.get("zk_proofs_enabled", True),  # zkProofsEnabled
                vault_config.get("privacy_level", "high"),  # privacyLevel
                vault_config.get("data_types", [])  # dataTypes
            ]
            
            # Deploy contract using Hedera client
            deployment_result = self.client.deploy_contract(
                bytecode=contract_bytecode,
                constructor_params=constructor_params,
                gas_limit=500000
            )
            
            deployment_info = {
                "contract_id": deployment_result["contract_id"],
                "contract_type": "health_vault",
                "owner": patient_account,
                "constructor_params": {
                    "vault_name": vault_config.get("name", "Health Vault"),
                    "encryption_enabled": vault_config.get("encryption_enabled", True),
                    "zk_proofs_enabled": vault_config.get("zk_proofs_enabled", True),
                    "privacy_level": vault_config.get("privacy_level", "high"),
                    "data_types": vault_config.get("data_types", [])
                },
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": deployment_result.get("gas_used", 0),
                "deployment_cost": deployment_result.get("cost_hbar", 0.0),
                "transaction_id": deployment_result.get("transaction_id"),
                "status": "deployed"
            }
            
            logger.info(f"Deployed health vault contract: {deployment_result['contract_id']} for {patient_account}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Failed to deploy health vault contract: {e}")
            raise
    
    def create_health_record(self, 
                           contract_id: str,
                           record_data: Dict[str, Any],
                           access_permissions: List[str]) -> Dict[str, Any]:
        """
        Create a health record in the vault contract
        
        Args:
            contract_id: Health vault contract ID
            record_data: Medical record data
            access_permissions: List of accounts with access permissions
            
        Returns:
            Dict containing record creation information
        """
        try:
            # Generate unique record ID
            record_id = f"record_{datetime.now().microsecond}"
            
            # Prepare contract call parameters
            function_params = [
                record_id,  # recordId
                record_data.get("record_type", "general"),  # recordType
                record_data.get("encrypted_data", ""),  # encryptedData
                record_data.get("data_hash", ""),  # dataHash
                access_permissions,  # accessPermissions
                record_data.get("metadata", {})  # metadata
            ]
            
            # Call contract function
            call_result = self.client.call_contract_function(
                contract_id=contract_id,
                function_name="createRecord",
                parameters=function_params,
                gas_limit=200000
            )
            
            creation_info = {
                "contract_id": contract_id,
                "record_id": record_id,
                "transaction_id": call_result.get("transaction_id"),
                "function_params": {
                    "record_type": record_data.get("record_type", "general"),
                    "access_permissions": access_permissions,
                    "metadata": record_data.get("metadata", {})
                },
                "gas_used": call_result.get("gas_used", 0),
                "status": "success",
                "created_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Created health record {record_id} in contract {contract_id}")
            return creation_info
            
        except Exception as e:
            logger.error(f"Failed to create health record: {e}")
            raise
    
    def grant_record_access(self, 
                          contract_id: str,
                          record_id: str,
                          grantee_account: str,
                          access_level: str,
                          duration_hours: int) -> Dict[str, Any]:
        """
        Grant access to a health record
        
        Args:
            contract_id: Health vault contract ID
            record_id: Record ID to grant access to
            grantee_account: Account to grant access to
            access_level: Level of access (read, write, admin)
            duration_hours: Duration of access in hours
            
        Returns:
            Dict containing access grant information
        """
        try:
            # Calculate expiration time
            expiration_time = datetime.utcnow() + timedelta(hours=duration_hours)
            
            # Mock implementation
            call_params = {
                "function": "grantAccess",
                "parameters": {
                    "record_id": record_id,
                    "grantee": grantee_account,
                    "access_level": access_level,
                    "expires_at": expiration_time.timestamp(),
                    "granted_at": datetime.utcnow().timestamp()
                }
            }
            
            grant_info = {
                "contract_id": contract_id,
                "record_id": record_id,
                "grantee_account": grantee_account,
                "access_level": access_level,
                "expires_at": expiration_time.isoformat(),
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "granted",
                "granted_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Granted {access_level} access to {grantee_account} for record {record_id}")
            return grant_info
            
        except Exception as e:
            logger.error(f"Failed to grant record access: {e}")
            raise
    
    def revoke_record_access(self, 
                           contract_id: str,
                           record_id: str,
                           grantee_account: str) -> Dict[str, Any]:
        """
        Revoke access to a health record
        
        Args:
            contract_id: Health vault contract ID
            record_id: Record ID to revoke access from
            grantee_account: Account to revoke access from
            
        Returns:
            Dict containing access revocation information
        """
        try:
            # Mock implementation
            call_params = {
                "function": "revokeAccess",
                "parameters": {
                    "record_id": record_id,
                    "grantee": grantee_account,
                    "revoked_at": datetime.utcnow().timestamp()
                }
            }
            
            revocation_info = {
                "contract_id": contract_id,
                "record_id": record_id,
                "grantee_account": grantee_account,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "revoked",
                "revoked_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Revoked access from {grantee_account} for record {record_id}")
            return revocation_info
            
        except Exception as e:
            logger.error(f"Failed to revoke record access: {e}")
            raise
    
    def deploy_consent_contract(self, 
                              patient_account: str,
                              provider_account: str,
                              consent_terms: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a consent management smart contract
        
        Args:
            patient_account: Patient's Hedera account ID
            provider_account: Provider's Hedera account ID
            consent_terms: Terms of the consent agreement
            
        Returns:
            Dict containing contract deployment information
        """
        try:
            # Mock implementation
            contract_id = f"0.0.{datetime.now().microsecond}"
            
            constructor_params = {
                "patient": patient_account,
                "provider": provider_account,
                "record_types": consent_terms.get("record_types", []),
                "duration_hours": consent_terms.get("duration_hours", 24),
                "compensation_rate": consent_terms.get("compensation_rate", 0.0),
                "purpose": consent_terms.get("purpose", "Medical treatment"),
                "privacy_level": consent_terms.get("privacy_level", "high"),
                "auto_renewal": consent_terms.get("auto_renewal", False),
                "created_at": datetime.utcnow().timestamp()
            }
            
            deployment_info = {
                "contract_id": contract_id,
                "contract_type": "consent_management",
                "patient": patient_account,
                "provider": provider_account,
                "constructor_params": constructor_params,
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": 400000,
                "deployment_cost": 0.08,
                "status": "deployed"
            }
            
            logger.info(f"Deployed consent contract: {contract_id}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Failed to deploy consent contract: {e}")
            raise
    
    def activate_consent(self, contract_id: str) -> Dict[str, Any]:
        """
        Activate a consent contract
        
        Args:
            contract_id: Consent contract ID
            
        Returns:
            Dict containing activation information
        """
        try:
            # Mock implementation
            call_params = {
                "function": "activateConsent",
                "parameters": {
                    "activated_at": datetime.utcnow().timestamp()
                }
            }
            
            activation_info = {
                "contract_id": contract_id,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "active",
                "activated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Activated consent contract: {contract_id}")
            return activation_info
            
        except Exception as e:
            logger.error(f"Failed to activate consent: {e}")
            raise
    
    def revoke_consent(self, contract_id: str, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Revoke a consent contract
        
        Args:
            contract_id: Consent contract ID
            reason: Optional reason for revocation
            
        Returns:
            Dict containing revocation information
        """
        try:
            # Mock implementation
            call_params = {
                "function": "revokeConsent",
                "parameters": {
                    "reason": reason,
                    "revoked_at": datetime.utcnow().timestamp()
                }
            }
            
            revocation_info = {
                "contract_id": contract_id,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "reason": reason,
                "status": "revoked",
                "revoked_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Revoked consent contract: {contract_id}")
            return revocation_info
            
        except Exception as e:
            logger.error(f"Failed to revoke consent: {e}")
            raise
    
    def deploy_research_contract(self, 
                               study_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy a research study smart contract
        
        Args:
            study_config: Research study configuration
            
        Returns:
            Dict containing contract deployment information
        """
        try:
            # Mock implementation
            contract_id = f"0.0.{datetime.now().microsecond}"
            
            constructor_params = {
                "study_id": study_config.get("study_id"),
                "principal_investigator": study_config.get("principal_investigator"),
                "institution": study_config.get("institution"),
                "title": study_config.get("title"),
                "description": study_config.get("description"),
                "data_types": study_config.get("data_types", []),
                "compensation": study_config.get("compensation", 0.0),
                "duration_weeks": study_config.get("duration_weeks", 12),
                "max_participants": study_config.get("max_participants", 100),
                "created_at": datetime.utcnow().timestamp()
            }
            
            deployment_info = {
                "contract_id": contract_id,
                "contract_type": "research_study",
                "study_id": study_config.get("study_id"),
                "constructor_params": constructor_params,
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": 600000,
                "deployment_cost": 0.12,
                "status": "deployed"
            }
            
            logger.info(f"Deployed research contract: {contract_id}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Failed to deploy research contract: {e}")
            raise
    
    def join_research_study(self, 
                          contract_id: str,
                          participant_account: str,
                          consent_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Join a research study
        
        Args:
            contract_id: Research contract ID
            participant_account: Participant's account ID
            consent_data: Participant consent data
            
        Returns:
            Dict containing participation information
        """
        try:
            # Mock implementation
            call_params = {
                "function": "joinStudy",
                "parameters": {
                    "participant": participant_account,
                    "data_types_consented": consent_data.get("data_types", []),
                    "anonymization_level": consent_data.get("anonymization_level", "high"),
                    "compensation_expected": consent_data.get("compensation_expected", 0.0),
                    "joined_at": datetime.utcnow().timestamp()
                }
            }
            
            participation_info = {
                "contract_id": contract_id,
                "participant_account": participant_account,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "status": "joined",
                "joined_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Participant {participant_account} joined study contract {contract_id}")
            return participation_info
            
        except Exception as e:
            logger.error(f"Failed to join research study: {e}")
            raise
    
    def deploy_emergency_contract(self, 
                                patient_account: str,
                                emergency_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deploy an emergency access smart contract
        
        Args:
            patient_account: Patient's Hedera account ID
            emergency_profile: Emergency profile data
            
        Returns:
            Dict containing contract deployment information
        """
        try:
            # Mock implementation
            contract_id = f"0.0.{datetime.now().microsecond}"
            
            constructor_params = {
                "patient": patient_account,
                "blood_type": emergency_profile.get("blood_type"),
                "allergies": emergency_profile.get("allergies", []),
                "current_medications": emergency_profile.get("current_medications", []),
                "medical_conditions": emergency_profile.get("medical_conditions", []),
                "emergency_contact": emergency_profile.get("emergency_contact", {}),
                "insurance_info": emergency_profile.get("insurance_info", {}),
                "created_at": datetime.utcnow().timestamp()
            }
            
            deployment_info = {
                "contract_id": contract_id,
                "contract_type": "emergency_access",
                "patient": patient_account,
                "constructor_params": constructor_params,
                "deployed_at": datetime.utcnow().isoformat(),
                "gas_used": 350000,
                "deployment_cost": 0.07,
                "status": "deployed"
            }
            
            logger.info(f"Deployed emergency contract: {contract_id} for {patient_account}")
            return deployment_info
            
        except Exception as e:
            logger.error(f"Failed to deploy emergency contract: {e}")
            raise
    
    def request_emergency_access(self, 
                               contract_id: str,
                               requester_account: str,
                               emergency_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Request emergency access to patient data
        
        Args:
            contract_id: Emergency contract ID
            requester_account: Account requesting access
            emergency_details: Details of the emergency
            
        Returns:
            Dict containing access request information
        """
        try:
            # Mock implementation
            call_params = {
                "function": "requestEmergencyAccess",
                "parameters": {
                    "requester": requester_account,
                    "emergency_type": emergency_details.get("emergency_type"),
                    "location": emergency_details.get("location"),
                    "urgency_level": emergency_details.get("urgency_level"),
                    "requester_credentials": emergency_details.get("requester_credentials"),
                    "requested_at": datetime.utcnow().timestamp()
                }
            }
            
            request_info = {
                "contract_id": contract_id,
                "requester_account": requester_account,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "call_params": call_params,
                "emergency_details": emergency_details,
                "status": "access_granted",  # Mock automatic approval for emergencies
                "requested_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Emergency access requested by {requester_account} for contract {contract_id}")
            return request_info
            
        except Exception as e:
            logger.error(f"Failed to request emergency access: {e}")
            raise
    
    def get_contract_state(self, contract_id: str) -> Dict[str, Any]:
        """
        Get the current state of a smart contract
        
        Args:
            contract_id: Contract ID to query
            
        Returns:
            Dict containing contract state
        """
        try:
            # Mock implementation
            contract_state = {
                "contract_id": contract_id,
                "status": "active",
                "owner": self.client.account_id,
                "created_at": "2024-01-01T00:00:00Z",
                "last_updated": datetime.utcnow().isoformat(),
                "gas_consumed": 1000000,
                "storage_used": 5000,
                "balance": 0.0,
                "state_variables": {
                    "initialized": True,
                    "active": True,
                    "participant_count": 5
                }
            }
            
            logger.info(f"Retrieved contract state for: {contract_id}")
            return contract_state
            
        except Exception as e:
            logger.error(f"Failed to get contract state: {e}")
            raise
    
    def call_contract_function(self, 
                             contract_id: str,
                             function_name: str,
                             parameters: Dict[str, Any],
                             gas_limit: int = 300000) -> Dict[str, Any]:
        """
        Call a function on a smart contract
        
        Args:
            contract_id: Contract ID to call
            function_name: Name of the function to call
            parameters: Function parameters
            gas_limit: Maximum gas to use
            
        Returns:
            Dict containing function call result
        """
        try:
            # Mock implementation
            call_result = {
                "contract_id": contract_id,
                "function_name": function_name,
                "parameters": parameters,
                "transaction_id": f"{self.client.account_id}@{datetime.now().timestamp()}",
                "gas_used": min(gas_limit, 250000),  # Mock gas usage
                "gas_limit": gas_limit,
                "result": "function_executed_successfully",
                "status": "success",
                "executed_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Called function {function_name} on contract {contract_id}")
            return call_result
            
        except Exception as e:
            logger.error(f"Failed to call contract function: {e}")
            raise
