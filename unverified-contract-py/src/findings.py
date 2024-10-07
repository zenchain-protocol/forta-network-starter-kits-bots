from forta_bot_sdk import Finding, FindingSeverity, FindingType, EntityType
from bot_alert_rate import calculate_alert_rate, ScanCountType
import hashlib

class UnverifiedCodeContractFindings:

    @staticmethod
    def unverified_code(from_address: str, contract_address: str, chain_id: int, contained_addresses: set, bot_id: str) -> Finding:

        labels = [{"entity": from_address,
                   "entity_type": EntityType.Address,
                   "label": "attacker",
                   "confidence": 0.3},  # low
                  {"entity": contract_address,
                   "entity_type": EntityType.Address,
                   "label": "attacker_contract",
                   "confidence": 0.3}]  # low

        addresses = {"address_contained_in_created_contract_" +
                     str(i): address for i, address in enumerate(contained_addresses, 1)}
        metadata = {**addresses}

        if chain_id not in [43114, 10, 250]:
            metadata['anomaly_score'] = calculate_alert_rate(
                chain_id,
                bot_id,
                'UNVERIFIED-CODE-CONTRACT-CREATION',
                ScanCountType.CONTRACT_CREATION_COUNT)

        # Ensure all metadata values are strings
        metadata = {key: str(value) for key, value in metadata.items()}
        
        unique_key = hashlib.sha256(f'{from_address},{contract_address}'.encode()).hexdigest()

        return Finding({
            'name': 'Contract with unverified code was created',
            'description': f'{from_address} created contract {contract_address}',
            'alert_id': 'UNVERIFIED-CODE-CONTRACT-CREATION',
            'type': FindingType.Suspicious,
            'severity': FindingSeverity.Medium,
            'metadata': metadata,
            'labels': labels,
            'unique_key': unique_key
        })
