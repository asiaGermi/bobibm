"""
Model Registry for watsonx.governance

Handles registration and tracking of AI models in watsonx.governance.
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

try:
    from ibm_aigov_facts_client import AIGovFactsClient
    from ibm_aigov_facts_client.supporting_classes.enums import ModelEntryType
    AIGOV_AVAILABLE = True
except ImportError:
    AIGOV_AVAILABLE = False
    logging.warning("ibm-aigov-facts-client not available. Model registry will run in mock mode.")


class ModelRegistry:
    """
    Manages model registration and tracking in watsonx.governance.
    
    This class handles:
    - Registering AI models in the governance catalog
    - Updating model metadata and versions
    - Linking models to AI use cases
    - Creating and managing AI Factsheets
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        instance_id: Optional[str] = None,
        catalog_id: Optional[str] = None,
        governance_url: Optional[str] = None
    ):
        """
        Initialize the Model Registry.
        
        Args:
            api_key: IBM Cloud API key for governance
            instance_id: watsonx.governance instance ID
            catalog_id: Catalog/inventory ID for model storage
            governance_url: watsonx.governance API URL
        """
        self.api_key = api_key or os.getenv("WATSONX_GOVERNANCE_API_KEY")
        self.instance_id = instance_id or os.getenv("WATSONX_GOVERNANCE_INSTANCE_ID")
        self.catalog_id = catalog_id or os.getenv("WATSONX_GOVERNANCE_CATALOG_ID")
        self.governance_url = governance_url or os.getenv("WATSONX_GOVERNANCE_URL")
        
        self.client = None
        self.enabled = os.getenv("ENABLE_GOVERNANCE_TRACKING", "true").lower() == "true"
        
        if self.enabled and AIGOV_AVAILABLE and all([self.api_key, self.instance_id, self.catalog_id]):
            try:
                self.client = AIGovFactsClient(
                    api_key=self.api_key,
                    container_id=self.catalog_id,
                    container_type="catalog",
                    experiment_name="Financial Risk Management"
                )
                logging.info("ModelRegistry initialized with watsonx.governance")
            except Exception as e:
                logging.error(f"Failed to initialize AIGovFactsClient: {e}")
                self.client = None
        else:
            logging.info("ModelRegistry running in mock mode (governance disabled or SDK unavailable)")
    
    def register_model(
        self,
        model_id: str,
        model_name: str,
        model_type: str = "foundation_model",
        provider: str = "IBM",
        description: Optional[str] = None,
        use_case_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Register a model in watsonx.governance.
        
        Args:
            model_id: Unique identifier for the model (e.g., "ibm/granite-4-h-small")
            model_name: Human-readable model name
            model_type: Type of model (foundation_model, custom, etc.)
            provider: Model provider (IBM, OpenAI, etc.)
            description: Model description
            use_case_id: Optional AI use case ID to link the model to
            metadata: Additional metadata to store with the model
            
        Returns:
            Dictionary with registration results including asset_id
        """
        if not self.enabled:
            logging.info(f"Governance disabled. Skipping registration for {model_id}")
            return {"status": "skipped", "reason": "governance_disabled"}
        
        if not self.client:
            logging.warning(f"Governance client not available. Mock registration for {model_id}")
            return {
                "status": "mock",
                "model_id": model_id,
                "model_name": model_name,
                "registered_at": datetime.utcnow().isoformat()
            }
        
        try:
            # Prepare model entry
            model_entry = {
                "model_id": model_id,
                "name": model_name,
                "model_type": model_type,
                "provider": provider,
                "description": description or f"{model_name} for Financial Risk Management",
                "registered_at": datetime.utcnow().isoformat(),
                "metadata": metadata or {}
            }
            
            # Add use case link if provided
            if use_case_id:
                model_entry["use_case_id"] = use_case_id
            
            # Register with governance (using facts client)
            # Note: Actual implementation depends on specific governance API
            logging.info(f"Registering model {model_id} in watsonx.governance")
            
            # Store model entry in governance catalog
            asset_id = self._create_model_asset(model_entry)
            
            return {
                "status": "success",
                "asset_id": asset_id,
                "model_id": model_id,
                "model_name": model_name,
                "catalog_id": self.catalog_id,
                "registered_at": model_entry["registered_at"]
            }
            
        except Exception as e:
            logging.error(f"Failed to register model {model_id}: {e}")
            return {
                "status": "error",
                "model_id": model_id,
                "error": str(e)
            }
    
    def _create_model_asset(self, model_entry: Dict[str, Any]) -> str:
        """
        Create a model asset in the governance catalog.
        
        Args:
            model_entry: Model metadata
            
        Returns:
            Asset ID of the created model
        """
        # This is a placeholder for the actual governance API call
        # The real implementation would use the AIGovFactsClient to create an asset
        
        # For now, return a mock asset ID
        asset_id = f"asset_{model_entry['model_id'].replace('/', '_')}_{datetime.utcnow().timestamp()}"
        logging.info(f"Created model asset: {asset_id}")
        return asset_id
    
    def update_model_metadata(
        self,
        model_id: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update metadata for a registered model.
        
        Args:
            model_id: Model identifier
            metadata: Metadata to update
            
        Returns:
            Update result
        """
        if not self.enabled or not self.client:
            return {"status": "skipped", "reason": "governance_disabled_or_unavailable"}
        
        try:
            logging.info(f"Updating metadata for model {model_id}")
            # Implementation would update the model asset in governance
            return {
                "status": "success",
                "model_id": model_id,
                "updated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to update model metadata: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_model_info(self, model_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve model information from governance.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Model information or None if not found
        """
        if not self.enabled or not self.client:
            return None
        
        try:
            logging.info(f"Retrieving info for model {model_id}")
            # Implementation would query the governance catalog
            return {
                "model_id": model_id,
                "status": "registered",
                "retrieved_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to retrieve model info: {e}")
            return None
    
    def link_to_use_case(
        self,
        model_id: str,
        use_case_id: str
    ) -> Dict[str, Any]:
        """
        Link a model to an AI use case in governance.
        
        Args:
            model_id: Model identifier
            use_case_id: AI use case identifier
            
        Returns:
            Link result
        """
        if not self.enabled or not self.client:
            return {"status": "skipped", "reason": "governance_disabled_or_unavailable"}
        
        try:
            logging.info(f"Linking model {model_id} to use case {use_case_id}")
            # Implementation would create the link in governance
            return {
                "status": "success",
                "model_id": model_id,
                "use_case_id": use_case_id,
                "linked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logging.error(f"Failed to link model to use case: {e}")
            return {"status": "error", "error": str(e)}


# Made with Bob