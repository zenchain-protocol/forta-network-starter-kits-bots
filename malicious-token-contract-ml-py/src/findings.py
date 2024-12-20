from forta_bot_sdk import Finding, FindingType, FindingSeverity
from bot_alert_rate import calculate_alert_rate, ScanCountType

class TokenContractFindings:
    def __init__(
        self,
        from_address: str,
        contract_address: str,
        contained_addresses: set,
        model_score: float,
        model_threshold: float,
        bot_id: str,
    ):
        self.metadata = {
            "address_contained_in_created_contract_" + str(i): str(address)
            for i, address in enumerate(contained_addresses, 1)
        }
        self.metadata["model_score"] = str(model_score)
        self.metadata["model_threshold"] = str(model_threshold)
        self.description = f"{from_address} created contract {contract_address}"
        self.labels = []
        self.bot_id = bot_id

    def malicious_contract_creation(
        self,
        chain_id: int,
        labels: list,
    ) -> Finding:
        scan_count_type = ScanCountType.CONTRACT_CREATION_COUNT
        custom_scan_count = None
        if chain_id in [43114, 10, 250]:
            scan_count_type = ScanCountType.CUSTOM_SCAN_COUNT
            custom_scan_count = 500_000

        self.metadata["anomaly_score"] = str(calculate_alert_rate(
            chain_id,
            self.bot_id,
            "SUSPICIOUS-TOKEN-CONTRACT-CREATION",
            scan_count_type,
            custom_scan_count,
        ))
        self.label = labels
        return Finding(
            {
                "name": "Suspicious Token Contract Creation",
                "description": self.description,
                "alert_id": "SUSPICIOUS-TOKEN-CONTRACT-CREATION",
                "type": FindingType.Suspicious,
                "severity": FindingSeverity.High,
                "metadata": self.metadata,
                "labels": self.labels,
                "source": {
                    "chains": [
                        {"chain_id": chain_id}
                    ]  # associates this finding to Ethereum mainnet
                },
            }
        )

    def safe_contract_creation(
        self,
        chain_id: int,
        labels: list,
    ) -> Finding:
        self.label = labels

        if chain_id not in [43114, 10, 250]:
            self.metadata["anomaly_score"] = str(
                calculate_alert_rate(
                    chain_id,
                    self.bot_id,
                    "SAFE-TOKEN-CONTRACT-CREATION",
                    ScanCountType.CONTRACT_CREATION_COUNT,
                ),
            )
        return Finding(
            {
                "name": "Safe Token Contract Creation",
                "description": self.description,
                "alert_id": "SAFE-TOKEN-CONTRACT-CREATION",
                "type": FindingType.Info,
                "severity": FindingSeverity.Info,
                "metadata": self.metadata,
                "labels": self.labels,
                "source": {
                    "chains": [
                        {"chain_id": chain_id}
                    ]  # associates this finding to Ethereum mainnet
                },
            }
        )

    def non_malicious_contract_creation(self, chain_id: int) -> Finding:
        if chain_id not in [43114, 10, 250]:
            self.metadata["anomaly_score"] = str(
                calculate_alert_rate(
                    chain_id,
                    self.bot_id,
                    "NON-MALICIOUS-TOKEN-CONTRACT-CREATION",
                    ScanCountType.CONTRACT_CREATION_COUNT,
                ),
            )
        return Finding(
            {
                "name": "Non-malicious Token Contract Creation",
                "description": self.description,
                "alert_id": "NON-MALICIOUS-TOKEN-CONTRACT-CREATION",
                "type": FindingType.Info,
                "severity": FindingSeverity.Info,
                "metadata": self.metadata,
                "labels": self.labels,
                "source": {
                    "chains": [
                        {"chain_id": chain_id}
                    ]  # associates this finding to Ethereum mainnet
                },
            }
        )
